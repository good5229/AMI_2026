#!/usr/bin/env python3
"""Build deterministic v0.9 episode-separated calibration and holdout cases."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v09"
MANIFEST = DATA / "v09_episode_manifest.json"
CONTEXT = ROOT / "lightguard_v0_1/data/validation/v07/regional_seasonal_context_2025.json"
SEED = 20260901

NORMAL = (
    "normal_night_operation", "sunrise_grace_operation", "sunset_grace_operation", "allowed_partial_operation",
    "short_transient_spike", "near_threshold_load_variation", "missing_feature_normal", "weather_context_normal",
)
ABNORMAL = (
    "post_sunrise_persistent_activation", "post_sunrise_weak_persistence", "pre_sunset_early_activation",
    "deep_day_partial_activation", "deep_day_full_activation", "phase_selective_activation",
    "moderate_load_mismatch", "repeated_long_persistence",
)
CONFIRM_EXTRA_NORMAL = ("sunrise_boundary_20m", "sunset_boundary_20m", "delayed_control_normal", "phase_noise_normal")
CONFIRM_EXTRA_ABNORMAL = ("post_sunrise_45m_weak", "pre_sunset_60m_weak", "missing_load_abnormal", "missing_phase_abnormal")


def sha(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def canonical(payload: object) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def load_assets(region: str) -> tuple[list[dict], list[dict]]:
    payload = json.loads((ROOT / f"lightguard_app/assets/data/{region}_v02_seed.json").read_text(encoding="utf-8"))
    assets = []
    for obj in payload["objects"]:
        expected = obj.get("expected_load", {})
        rated = expected.get("rated_power_w")
        assets.append({"uid": obj["cabinet_uid"], "rated_load_kw": float(rated) / 1000 if rated is not None else None})
    assets.sort(key=lambda row: sha(f"{SEED}|asset|{region}|{row['uid']}"))
    cut = max(1, int(len(assets) * 0.40))
    return assets[:cut], assets[cut:]


def weather_by_episode() -> dict[tuple[str, str], dict]:
    payload = json.loads(CONTEXT.read_text(encoding="utf-8"))
    result = {}
    for cell in payload["cells"]:
        grouped: dict[str, list[dict]] = defaultdict(list)
        for row in cell["kma_observations"]:
            grouped[row["timestamp"][:10]].append(row)
        for day, rows in grouped.items():
            rain = sum(float(row["precipitation"] or 0) for row in rows)
            clouds = [float(row["cloud_amount"]) for row in rows if row["cloud_amount"] is not None]
            cloud = sum(clouds) / len(clouds) if clouds else 0.0
            regime = "rainfall" if rain > 0 else "overcast" if cloud >= 7 else "high_cloud" if cloud >= 4 else "clear"
            result[(cell["cell_id"], day)] = {"regime": regime, "rainfall_mm": round(rain, 3), "mean_cloud_amount": round(cloud, 3)}
    return result


def scenario_values(name: str) -> dict:
    table = {
        "normal_night_operation": ("none", 180, 60, .08, .02, .00, "compatible", False, False),
        "sunrise_grace_operation": ("sunrise", 10, 20, .55, .04, .00, "unknown", False, False),
        "sunset_grace_operation": ("sunset", 10, 30, .60, .04, .00, "unknown", False, False),
        "allowed_partial_operation": ("none", 180, 60, .58, .12, .30, "allowed", False, False),
        "short_transient_spike": ("sunrise", 180, 10, .90, .08, .10, "unknown", True, False),
        "near_threshold_load_variation": ("none", 180, 45, .48, .08, .05, "compatible", False, False),
        "missing_feature_normal": ("none", 180, 60, .65, None, None, "unknown", False, True),
        "weather_context_normal": ("sunrise", 25, 35, .62, .06, .05, "unknown", False, False),
        "sunrise_boundary_20m": ("sunrise", 20, 30, .64, .04, .00, "unknown", False, False),
        "sunset_boundary_20m": ("sunset", 20, 30, .64, .04, .00, "unknown", False, False),
        "delayed_control_normal": ("sunrise", 45, 45, .65, .05, .00, "allowed", False, False),
        "phase_noise_normal": ("none", 180, 15, .58, .05, .50, "compatible", True, False),
        "post_sunrise_persistent_activation": ("sunrise", 90, 90, .70, .30, .00, "prohibited", False, False),
        "post_sunrise_weak_persistence": ("sunrise", 60, 90, .45, .25, .00, "prohibited", False, False),
        "pre_sunset_early_activation": ("sunset", 90, 60, .70, .25, .00, "prohibited", False, False),
        "deep_day_partial_activation": ("sunrise", 180, 60, .55, .45, .50, "prohibited", False, False),
        "deep_day_full_activation": ("sunrise", 180, 45, .90, .50, .00, "prohibited", False, False),
        "phase_selective_activation": ("sunrise", 180, 60, .55, .20, 1.00, "prohibited", False, False),
        "moderate_load_mismatch": ("sunrise", 180, 60, .50, .55, .00, "prohibited", False, False),
        "repeated_long_persistence": ("sunrise", 120, 90, .45, .30, .20, "prohibited", False, False),
        "post_sunrise_45m_weak": ("sunrise", 45, 90, .45, .25, .00, "prohibited", False, False),
        "pre_sunset_60m_weak": ("sunset", 60, 60, .48, .25, .00, "prohibited", False, False),
        "missing_load_abnormal": ("sunrise", 180, 75, .70, None, .50, "prohibited", False, False),
        "missing_phase_abnormal": ("sunrise", 180, 75, .70, .50, None, "prohibited", False, False),
    }
    side, margin, duration, activation, load, phase, policy, transient, both_missing = table[name]
    return {"solar_side": side, "solar_margin_min": margin, "continuous_on_minutes": duration,
            "activation_evidence": activation, "load_mismatch": load, "phase_selectivity": phase,
            "policy_status": policy, "transient": transient, "both_missing": both_missing}


def materialize(episode: dict, name: str, label: str, index: int, asset: dict, weather: dict) -> dict:
    values = scenario_values(name)
    load = values["load_mismatch"] if asset["rated_load_kw"] is not None else None
    phase = values["phase_selectivity"]
    if values.pop("both_missing"):
        load = None
        phase = None
    margin = float(values["solar_margin_min"])
    solar_evidence = 0.0 if values["solar_side"] == "none" else max(0.0, min(1.0, (margin - 15.0) / 105.0))
    duration = float(values["continuous_on_minutes"])
    persistence = .6 * max(0.0, min(1.0, (duration - 10.0) / 50.0)) + .4 * min(1.0, duration / 60.0)
    policy = None if values["policy_status"] == "unknown" else float(values["policy_status"] == "prohibited")
    near_boundary = values["solar_side"] != "none" and margin <= 30
    expected_kw = asset["rated_load_kw"]
    observed_kw = expected_kw * (1.0 - load) if expected_kw is not None and load is not None else None
    hard = label == "normal" and name != "normal_night_operation"
    case_id = f"V09-{episode['split'][:3].upper()}-{episode['episode_id'][4:].upper()}-{index + 1:02d}"
    return {
        "case_id": case_id, "split": episode["split"], "episode_id": episode["episode_id"], "date": episode["date"],
        "region_id": episode["region_id"], "season": episode["season"], "cell_id": episode["cell_id"],
        "label": label, "hard_negative": hard, "scenario_type": name, "asset_cabinet_uid": asset["uid"],
        "rated_load_status": "available" if expected_kw is not None else "unavailable_no_imputation",
        "rated_load_kw": expected_kw, "observed_load_kw": observed_kw, "load_imputation": "none",
        **values, "load_mismatch": load, "phase_selectivity": phase,
        "near_solar_boundary": near_boundary, "normal_partial_policy": values["policy_status"] == "allowed",
        "solar_evidence": solar_evidence, "persistence_evidence": round(persistence, 8),
        "load_evidence": load, "phase_evidence": phase, "policy_evidence": policy,
        "boundary_conflict": 1.0 if near_boundary else 0.0,
        "transient_conflict": 1.0 if values["transient"] else 0.0,
        "policy_conflict": 1.0 if values["policy_status"] == "allowed" else 0.0,
        "load_phase_conflict": 0.5 if label == "normal" and load is not None and load <= .08 and (phase or 0) <= .10 else 0.0,
        "weather_regime": weather["regime"], "weather_context": weather, "weather_weight": 0.0,
        "recurrence": (int(sha(case_id)[:4], 16) % 101) / 100,
        "asset_criticality": (int(sha(asset["uid"])[:4], 16) % 101) / 100,
        "age_since_last_review": (int(sha(case_id + "age")[:4], 16) % 101) / 100,
        "signal_parameter_id": sha(f"{SEED}|signal|{case_id}|{name}")[:24],
        "source": "v09_controlled_generated_case_not_actual_ami",
    }


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["scenario_generation_gate"]["status"] != "open" or len(manifest["episodes"]) != 48:
        raise RuntimeError("all 48 official-context episodes must be ready")
    weather = weather_by_episode()
    pools = {region: load_assets(region) for region in ("suyeong", "gangneung", "chungju")}
    by_split = {"calibration": [], "confirmatory": []}
    cursors = defaultdict(int)
    for episode in manifest["episodes"]:
        split = episode["split"]
        names = list(NORMAL) + list(ABNORMAL)
        if split == "confirmatory":
            names = list(NORMAL) + list(CONFIRM_EXTRA_NORMAL) + list(ABNORMAL) + list(CONFIRM_EXTRA_ABNORMAL)
        for index, name in enumerate(names):
            label = "normal" if index < len(names) // 2 else "abnormal"
            pool = pools[episode["region_id"]][0 if split == "calibration" else 1]
            key = (episode["region_id"], split)
            asset = pool[cursors[key] % len(pool)]
            cursors[key] += 1
            by_split[split].append(materialize(episode, name, label, index, asset, weather[(episode["cell_id"], episode["date"])]))
    expected = {"calibration": 384, "confirmatory": 576}
    episode_sha = hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
    for split, cases in by_split.items():
        if len(cases) != expected[split]:
            raise AssertionError((split, len(cases)))
        payload = {"schema_version": f"lightguard.v09-{split}.v1", "split": split, "episode_manifest_sha256": episode_sha,
                   "case_count": len(cases), "actual_ami": False, "post_result_retuning_permitted": False,
                   "design_seed": SEED, "cases": cases}
        name = "v09_calibration_set.json" if split == "calibration" else "v09_confirmatory_holdout.json"
        (DATA / name).write_bytes(canonical(payload))
    print(json.dumps({split: len(cases) for split, cases in by_split.items()}, sort_keys=True))


if __name__ == "__main__":
    main()
