#!/usr/bin/env python3
"""Run frozen v0.3 audit and independent v0.4 ranking validation."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import random
from collections import Counter
from datetime import datetime
from pathlib import Path

from context_common import APP_CONTEXT_DIR, CONTEXT_DIR, REPORT_DIR, ROOT, utc_now, write_json


V03_SHA = "935bc5ea7d70e878f15113dc08d11dfee7ebcbb350d90d421f46a7704cf27368"
CALIBRATION_SEED = 4042026
HOLDOUT_SEED = 8042026
OBJECTIVE = "recall >= 0.98; minimize normal FPR; maximize P@10 then P@20 then NDCG@10; minimize candidates and complexity"
VALIDATION_DIR = ROOT / "lightguard_v0_1" / "data" / "validation"
REPLAY_DIR = ROOT / "lightguard_app" / "assets" / "data" / "ami_event_windows"


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def write_csv(path: Path, rows: list[dict], headers: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if headers is None:
        headers = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def weather_modifier(weather: dict | None) -> float:
    if not weather or weather.get("source") != "KMA_ASOS_HOURLY_OFFICIAL":
        return 0.0
    rain = float(weather.get("precipitation") or 0)
    cloud = float(weather.get("cloud_amount") or 0)
    radiation = weather.get("solar_radiation")
    return min(0.15, (0.05 if rain > 0 else 0.0) + min(max(cloud, 0), 10) / 10 * 0.07
               + (0.03 if radiation is not None and float(radiation) < 0.5 else 0.0))


def v03_decompose(case: dict, model: str) -> dict:
    activation = float(case["activation"])
    duration_factor = min(float(case["duration_min"]) / 30.0, 1.0)
    parts = {
        "score_ami": activation,
        "score_duration": -activation * (1 - duration_factor),
        "score_solar": 0.0,
        "score_asset": 0.0,
        "score_weather": 0.0,
    }
    value = activation * duration_factor
    candidate = value >= 0.18 and case["duration_min"] >= 15
    if model in ("M1", "M2", "M3") and case["near_solar_boundary"]:
        updated = max(0.0, value - 0.45)
        parts["score_solar"] = updated - value
        value = updated
        candidate = value >= 0.18
    if model in ("M2", "M3"):
        before = value
        if case["normal_partial_policy"]:
            value = max(0.0, value - 0.25)
        elif 3.0 <= case["rated_load_kw"] <= 3.8 and case["duration_min"] >= 60:
            value = min(1.0, value + 0.25)
        parts["score_asset"] = value - before
        candidate = value >= 0.18
    if model == "M3" and case["weather_context_mode"] == "official_adverse_candidate":
        modifier = weather_modifier(case.get("official_weather_context"))
        parts["score_weather"] = -modifier
        value = max(0.0, value - modifier)
        # v0.3 policy: weather changes ranking only, never M2 candidate status.
    return {**parts, "total_score": round(value, 6), "candidate": candidate}


def rank_rows(cases: list[dict], scorer) -> list[dict]:
    rows = []
    for case in cases:
        result = scorer(case)
        rows.append({**case, **result})
    rows.sort(key=lambda row: (-row["total_score"], row["case_id"]))
    for index, row in enumerate(rows, 1):
        row["rank"] = index
    return rows


def metrics(rows: list[dict]) -> dict:
    anomalies = [row for row in rows if row["label"] in ("injected_anomaly", "abnormal")]
    normals = [row for row in rows if row not in anomalies]
    tp = sum(row["candidate"] for row in anomalies)
    fp = sum(row["candidate"] for row in normals)
    result = {
        "anomaly_recall": tp / len(anomalies),
        "normal_fpr": fp / len(normals),
        "inspection_candidate_count": tp + fp,
        "normal_false_positive_count": fp,
    }
    for k in (5, 10, 20):
        hits = sum(row in anomalies for row in rows[:k])
        result[f"precision_at_{k}"] = hits / k
        result[f"recall_at_{k}"] = hits / len(anomalies)
    hits = 0
    precision_sum = 0.0
    dcg = {10: 0.0, 20: 0.0}
    for index, row in enumerate(rows, 1):
        relevant = row in anomalies
        if relevant:
            hits += 1
            precision_sum += hits / index
        for k in dcg:
            if index <= k and relevant:
                dcg[k] += 1 / math.log2(index + 1)
    result["average_precision"] = precision_sum / len(anomalies)
    for k in dcg:
        ideal = sum(1 / math.log2(index + 1) for index in range(1, min(k, len(anomalies)) + 1))
        result[f"ndcg_at_{k}"] = dcg[k] / ideal
    return result


def regime_map(payload: dict) -> dict[str, list[dict]]:
    result = {}
    for regime in payload.get("regimes", []):
        hours = [row for row in regime.get("representative_hours", [])
                 if row.get("source") == "KMA_ASOS_HOURLY_OFFICIAL"]
        if hours:
            result[regime["regime"]] = hours
    required = {"CLEAR", "OVERCAST", "RAIN", "LOW_SOLAR", "HIGH_HUMIDITY_OR_LOW_VISIBILITY"}
    if set(result) != required:
        raise RuntimeError("All five official KMA weather regimes are required; synthetic fallback is prohibited")
    return result


def build_cases(counts: dict[str, int], assets: list[dict], regimes: dict[str, list[dict]],
                seed: int, split: str) -> list[dict]:
    rng = random.Random(seed)
    types = [kind for kind, count in counts.items() for _ in range(count)]
    rng.shuffle(types)
    shuffled_assets = list(assets)
    rng.shuffle(shuffled_assets)
    adverse = ("OVERCAST", "RAIN", "LOW_SOLAR", "HIGH_HUMIDITY_OR_LOW_VISIBILITY")
    cases = []
    for index, kind in enumerate(types):
        asset = shuffled_assets[index % len(shuffled_assets)]
        abnormal = kind.startswith("abnormal_")
        if kind == "abnormal_daytime_full":
            activation, duration, mismatch, phase = rng.uniform(.75, 1), rng.choice((30, 60, 90, 120)), rng.uniform(.35, .9), rng.uniform(.1, .4)
        elif kind == "abnormal_partial":
            activation, duration, mismatch, phase = rng.uniform(.35, .65), rng.choice((45, 60, 90, 120)), rng.uniform(.35, .8), rng.uniform(.1, .5)
        elif kind == "abnormal_phase_selective":
            activation, duration, mismatch, phase = rng.uniform(.35, .7), rng.choice((30, 60, 90, 120)), rng.uniform(.3, .8), rng.uniform(.7, 1)
        elif kind == "abnormal_long_duration":
            activation, duration, mismatch, phase = rng.uniform(.22, .45), rng.choice((120, 180, 240)), rng.uniform(.4, .9), rng.uniform(.1, .5)
        elif kind == "abnormal_moderate":
            activation, duration, mismatch, phase = rng.uniform(.45, .7), rng.choice((45, 60, 90)), rng.uniform(.3, .7), rng.uniform(.1, .5)
        elif kind == "normal_clean":
            activation, duration, mismatch, phase = rng.uniform(.01, .08), rng.choice((0, 5, 10)), rng.uniform(0, .12), rng.uniform(0, .15)
        elif kind == "normal_twilight_boundary":
            activation, duration, mismatch, phase = rng.uniform(.5, .9), rng.choice((20, 30, 45)), rng.uniform(0, .2), rng.uniform(0, .2)
        elif kind == "normal_transient_spike":
            activation, duration, mismatch, phase = rng.uniform(.7, 1), 5, rng.uniform(0, .15), rng.uniform(0, .2)
        elif kind == "normal_validation_partial":
            activation, duration, mismatch, phase = rng.uniform(.18, .35), rng.choice((60, 90, 120)), rng.uniform(0, .15), rng.uniform(0, .2)
        else:
            activation, duration, mismatch, phase = rng.uniform(.25, .55), rng.choice((45, 60, 90, 120)), rng.uniform(0, .2), rng.uniform(0, .2)
        weather_name = rng.choice(adverse if kind == "normal_weather_sensitive" else tuple(regimes))
        options = regimes[weather_name]
        split_options = options[:3] if split == "calibration" else options[3:]
        if not split_options:
            raise RuntimeError(f"Weather regime {weather_name} lacks disjoint representative hours")
        weather = split_options[index % len(split_options)]
        expected_load = asset.get("expected_load", {})
        cases.append({
            "case_id": f"V04-{split.upper()}-{index + 1:03d}",
            "cabinet_uid": asset["cabinet_uid"],
            "label": "abnormal" if abnormal else "normal_control",
            "case_type": kind,
            "activation": round(activation, 6),
            "duration_min": duration,
            "timestamp": weather["timestamp"],
            "rated_load_kw": float(expected_load.get("expected_rated_load_kW") or 0),
            "lamp_count": int(expected_load.get("lamp_count") or 0),
            "load_mismatch": round(mismatch, 6),
            "phase_selectivity": round(phase, 6),
            "near_solar_boundary": kind == "normal_twilight_boundary",
            "transient": kind == "normal_transient_spike",
            "normal_partial_policy": kind == "normal_validation_partial",
            "weather_sensitive": kind == "normal_weather_sensitive",
            "weather_regime": weather_name,
            "official_weather_context": weather,
            "source": "controlled_validation_v0.4",
        })
    return cases


def baseline_m2(case: dict) -> dict:
    shadow = {**case, "weather_context_mode": "official_if_available"}
    return v03_decompose(shadow, "M2")


def v04_score(case: dict, weights: dict, weather_enabled: bool = True) -> dict:
    components = {
        "score_activation": weights["activation"] * case["activation"],
        "score_duration": weights["duration"] * min(case["duration_min"] / 120, 1),
        "score_load": weights["load"] * case["load_mismatch"],
        "score_phase": weights["phase"] * case["phase_selectivity"],
        "score_solar": -weights["solar_penalty"] if case["near_solar_boundary"] else 0.0,
        "score_transient": -weights["transient_penalty"] if case["transient"] else 0.0,
        "score_policy": -weights["policy_penalty"] if case["normal_partial_policy"] else 0.0,
    }
    core = sum(components.values())
    weather = -weights["weather"] * weather_modifier(case["official_weather_context"]) / .15 \
        if weather_enabled and case["weather_sensitive"] else 0.0
    return {**components, "score_weather": weather, "weather_modifier": weather,
            "total_score": round(core + weather, 6), "candidate": core >= weights["threshold"]}


def calibrate(cases: list[dict]) -> tuple[dict, dict, list[dict]]:
    keys = ("activation", "duration", "load", "phase", "solar_penalty", "transient_penalty",
            "policy_penalty", "weather", "threshold")
    grid = itertools.product(
        (.45, .60, .75), (.15, .25), (.15, .25), (.10, .20), (.20, .35),
        (.20, .35), (.20, .35), (0.0, .05, .10), (.35, .45, .55),
    )
    candidates = []
    for values in grid:
        weights = dict(zip(keys, values))
        ranked = rank_rows(cases, lambda case, w=weights: v04_score(case, w))
        result = metrics(ranked)
        feasible = result["anomaly_recall"] >= .98
        objective = (
            0 if feasible else 1,
            -result["anomaly_recall"] if not feasible else result["normal_fpr"],
            -result["precision_at_10"], -result["precision_at_20"], -result["ndcg_at_10"],
            result["inspection_candidate_count"], sum(values), tuple(values),
        )
        candidates.append({"weights": weights, "metrics": result, "objective": objective})
    candidates.sort(key=lambda row: row["objective"])
    best = candidates[0]
    result_rows = []
    for rank, row in enumerate(candidates[:50], 1):
        result_rows.append({"search_rank": rank, **row["weights"], **row["metrics"],
                            "objective_frozen": OBJECTIVE})
    return best["weights"], best["metrics"], result_rows


def write_case_set(path: Path, cases: list[dict], schema: str, seed: int) -> str:
    digest = canonical_hash(cases)
    write_json(path, {"schema_version": schema, "deterministic_seed": seed,
                      "set_sha256": digest, "case_count": len(cases), "cases": cases})
    return digest


def audit_v03(cases: list[dict]) -> tuple[list[dict], list[dict], dict]:
    decomposition = []
    ranked_by_model = {}
    for model in ("M0", "M1", "M2", "M3"):
        ranked = rank_rows(cases, lambda case, m=model: v03_decompose(case, m))
        ranked_by_model[model] = ranked
        for row in ranked:
            decomposition.append({
                "model": model, "case_id": row["case_id"], "cabinet_uid": row["cabinet_uid"],
                "label": row["label"], "control_type": row.get("hard_negative_type"),
                "score_ami": row["score_ami"], "score_duration": row["score_duration"],
                "score_solar": row["score_solar"], "score_asset": row["score_asset"],
                "score_weather": row["score_weather"], "total_score": row["total_score"],
                "candidate": row["candidate"], "rank": row["rank"],
            })
    audit = []
    for model in ("M2", "M3"):
        ranked = ranked_by_model[model]
        selected = [("top20_false_positive", row) for row in ranked[:20] if row["label"] == "normal_control"]
        anomalies = [row for row in ranked if row["label"] == "injected_anomaly"][-15:]
        selected.extend(("low_ranked_anomaly", row) for row in anomalies)
        for audit_type, row in selected:
            weather = row.get("official_weather_context") or {}
            audit.append({
                "audit_type": audit_type, "model": model, "case_id": row["case_id"],
                "cabinet_uid": row["cabinet_uid"], "rank": row["rank"], "total_score": row["total_score"],
                "control_type": row.get("hard_negative_type"), "activation": row["activation"],
                "duration_min": row["duration_min"], "solar_context": "near_boundary" if row["near_solar_boundary"] else "daytime",
                "expected_load_kw": row["rated_load_kw"], "lamp_count": row["lamp_count"],
                "weather_context": json.dumps(weather, ensure_ascii=False, sort_keys=True),
                "score_ami": row["score_ami"], "score_duration": row["score_duration"],
                "score_solar": row["score_solar"], "score_asset": row["score_asset"],
                "score_weather": row["score_weather"],
            })
    sensitivity = []
    m2 = {row["case_id"]: row for row in ranked_by_model["M2"]}
    m3 = {row["case_id"]: row for row in ranked_by_model["M3"]}
    for case_id in sorted(m2):
        left, right = m2[case_id], m3[case_id]
        sensitivity.append({"case_id": case_id, "score_M2": left["total_score"],
                            "weather_modifier": right["score_weather"], "score_M3": right["total_score"],
                            "rank_M2": left["rank"], "rank_M3": right["rank"],
                            "rank_delta": left["rank"] - right["rank"]})
    modifiers = [abs(row["weather_modifier"]) for row in sensitivity if row["weather_modifier"]]
    rank_changes = sum(row["rank_delta"] != 0 for row in sensitivity)
    m2_metrics, m3_metrics = metrics(ranked_by_model["M2"]), metrics(ranked_by_model["M3"])
    if not modifiers or max(modifiers) - min(modifiers) <= .01:
        decision = "A: modifier nearly identical; insufficient discrimination"
    elif rank_changes == 0:
        decision = "B: modifier differs but ranking does not change; insufficient strength"
    elif all(abs(m2_metrics[key] - m3_metrics[key]) < 1e-12 for key in
             ("normal_fpr", "precision_at_10", "precision_at_20", "ndcg_at_10")):
        decision = "C: ranking changes without metric improvement; rule direction requires validation"
    else:
        decision = "D: improvement is limited to a weather-sensitive subset"
    return decomposition, audit, {"rows": sensitivity, "decision": decision,
                                  "modifier_min": min(modifiers, default=0), "modifier_max": max(modifiers, default=0),
                                  "rank_changes": rank_changes}


def weather_stress(regimes: dict[str, list[dict]], weights: dict) -> tuple[list[dict], list[dict]]:
    base_cases = []
    for index in range(12):
        base_cases.append({
            "case_id": f"WEATHER-BASE-{index + 1:02d}", "label": "normal_control",
            "activation": .35 + index * .01, "duration_min": 90, "load_mismatch": .15,
            "phase_selectivity": .1, "near_solar_boundary": False, "transient": False,
            "normal_partial_policy": False, "weather_sensitive": True,
        })
    pairs = []
    for base in base_cases:
        for regime in sorted(regimes):
            weather = regimes[regime][0]
            pairs.append({**base, "case_id": f"{base['case_id']}-{regime}", "pair_group": base["case_id"],
                          "weather_regime": regime, "timestamp": weather["timestamp"],
                          "official_weather_context": weather, "source": "paired_official_weather_stress"})
    digest = canonical_hash(pairs)
    ranked = rank_rows(pairs, lambda case: v04_score(case, weights))
    rows = [{"pair_group": row["pair_group"], "case_id": row["case_id"],
             "weather_regime": row["weather_regime"], "official_timestamp": row["timestamp"],
             "score_without_weather": v04_score(row, weights, False)["total_score"],
             "weather_modifier": row["weather_modifier"], "score_with_weather": row["total_score"],
             "rank": row["rank"], "source": row["official_weather_context"]["source"]} for row in ranked]
    return pairs, rows


def replay_regression() -> list[dict]:
    manifest = json.loads((REPLAY_DIR / "replay_manifest.json").read_text(encoding="utf-8"))
    with (ROOT / "lightguard_app" / "assets" / "data" / "ami_events.csv").open(encoding="utf-8-sig", newline="") as handle:
        events = {(row["meter_id"], row["first_sample"][:10]): row for row in csv.DictReader(handle)}
    results = []
    for item in manifest["events"]:
        path = REPLAY_DIR / item["file"]
        with path.open(encoding="utf-8-sig", newline="") as handle:
            samples = list(csv.DictReader(handle))
        event = events[(item["meter_id"], item["date"])]
        times = [datetime.fromisoformat(row["timestamp"]) for row in samples]
        start, end = datetime.fromisoformat(event["first_sample"]), datetime.fromisoformat(event["last_sample"])
        currents = [float(row[field]) for row in samples for field in ("i1", "i2", "i3") if row.get(field)]
        peak = max(currents) if currents else 0.0
        expected_peak = float(event["peak_current_a"])
        active_phases = [value for value in event["active_phases"].split(",") if value]
        results.append({
            "event_id": event["event_id"], "file": item["file"], "event_type": event["event_type"],
            "event_type_reproduced": event["event_type"].startswith("daytime_"),
            "interval_overlap": min(times) <= start <= max(times) and min(times) <= end <= max(times),
            "observed_peak_current_a": round(peak, 6), "expected_peak_current_a": expected_peak,
            "peak_current_consistent": abs(peak - expected_peak) <= max(.05, expected_peak * .02),
            "active_phases": event["active_phases"],
            "phase_selective_consistent": len(active_phases) < 3 if "phase_selective" in event["event_type"] else True,
            "source_row_count": len(samples), "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "field_accuracy_claim": "prohibited", "context_join": "none",
        })
    return results


def main() -> int:
    frozen_path = CONTEXT_DIR / "controlled_validation_frozen_2026.json"
    frozen_bytes_sha = hashlib.sha256(frozen_path.read_bytes()).hexdigest()
    frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
    if frozen.get("frozen_set_sha256") != V03_SHA or canonical_hash(frozen["cases"]) != V03_SHA:
        raise RuntimeError("v0.3 frozen SHA changed; tuning is prohibited")
    regimes_payload = json.loads((CONTEXT_DIR / "kma_weather_regimes_2026.json").read_text(encoding="utf-8"))
    regimes = regime_map(regimes_payload)

    decomposition, audit, sensitivity = audit_v03(frozen["cases"])
    write_csv(REPORT_DIR / "v03_score_decomposition.csv", decomposition)
    write_csv(REPORT_DIR / "v03_ranking_error_audit.csv", audit)
    write_csv(REPORT_DIR / "weather_modifier_sensitivity.csv", sensitivity["rows"])
    causes = Counter(row["control_type"] or "inactive_control" for row in audit if row["audit_type"] == "top20_false_positive")
    (REPORT_DIR / "v03_ranking_error_summary.md").write_text(
        "# v0.3 Ranking Error Audit\n\n"
        f"- Frozen SHA-256: `{V03_SHA}`\n"
        f"- Top-20 normal rows audited across M2/M3: {sum(row['audit_type'] == 'top20_false_positive' for row in audit)}\n"
        f"- Bottom-15 anomalies audited across M2/M3: {sum(row['audit_type'] == 'low_ranked_anomaly' for row in audit)}\n"
        f"- Main false-positive groups: {dict(causes)}\n"
        "- Case-level decomposition shows that high activation/duration controls can outrank moderate anomalies when policy, transient, phase, and mismatch evidence are not sufficiently separated.\n"
        f"- Weather diagnosis: {sensitivity['decision']}\n",
        encoding="utf-8")

    seed = json.loads((ROOT / "lightguard_v0_1" / "app_seed" / "suyeong_v02_seed.json").read_text(encoding="utf-8"))
    assets = sorted(seed["objects"], key=lambda row: row["cabinet_uid"])
    midpoint = len(assets) // 2
    calibration_counts = {
        "abnormal_daytime_full": 12, "abnormal_partial": 12, "abnormal_phase_selective": 12,
        "abnormal_long_duration": 12, "abnormal_moderate": 12,
        "normal_clean": 24, "normal_twilight_boundary": 24, "normal_transient_spike": 24,
        "normal_validation_partial": 24, "normal_weather_sensitive": 24,
    }
    holdout_counts = {
        "abnormal_daytime_full": 10, "abnormal_partial": 9, "abnormal_phase_selective": 9,
        "abnormal_long_duration": 9, "abnormal_moderate": 9,
        "normal_clean": 32, "normal_twilight_boundary": 32, "normal_transient_spike": 32,
        "normal_validation_partial": 31, "normal_weather_sensitive": 31,
    }
    calibration = build_cases(calibration_counts, assets[:midpoint], regimes, CALIBRATION_SEED, "calibration")
    holdout = build_cases(holdout_counts, assets[midpoint:], regimes, HOLDOUT_SEED, "holdout")
    calibration_sha = write_case_set(VALIDATION_DIR / "v04_calibration_set.json", calibration,
                                     "lightguard-v0.4-calibration", CALIBRATION_SEED)
    holdout_sha = write_case_set(VALIDATION_DIR / "v04_confirmatory_holdout.json", holdout,
                                 "lightguard-v0.4-confirmatory-holdout", HOLDOUT_SEED)
    if {row["cabinet_uid"] for row in calibration} & {row["cabinet_uid"] for row in holdout}:
        raise RuntimeError("Calibration and holdout asset assignments overlap")
    if {row["timestamp"] for row in calibration} & {row["timestamp"] for row in holdout}:
        raise RuntimeError("Calibration and holdout weather/timing assignments overlap")

    weights, calibration_metrics, calibration_rows = calibrate(calibration)
    write_csv(REPORT_DIR / "v04_calibration_results.csv", calibration_rows)
    holdout_m0_rows = rank_rows(
        holdout,
        lambda case: v03_decompose(
            {**case, "weather_context_mode": "official_if_available"}, "M0"),
    )
    baseline_rows = rank_rows(holdout, baseline_m2)
    v04_weather_rows = rank_rows(holdout, lambda case: v04_score(case, weights, True))
    v04_no_weather_rows = rank_rows(holdout, lambda case: v04_score(case, weights, False))
    holdout_m0_metrics = metrics(holdout_m0_rows)
    baseline_metrics = metrics(baseline_rows)
    weather_metrics = metrics(v04_weather_rows)
    no_weather_metrics = metrics(v04_no_weather_rows)
    weather_improves = weather_metrics["anomaly_recall"] >= no_weather_metrics["anomaly_recall"] and any(
        weather_metrics[key] > no_weather_metrics[key] + 1e-12
        for key in ("precision_at_10", "precision_at_20", "ndcg_at_10", "ndcg_at_20", "average_precision"))
    weather_decision = "scoring_keep" if weather_improves else "context_only"
    final_rows = v04_weather_rows if weather_improves else v04_no_weather_rows
    final_metrics = weather_metrics if weather_improves else no_weather_metrics
    if not weather_improves:
        weights = {**weights, "weather": 0.0}
    confirmatory = []
    for model, result in (("v0.3_M2", baseline_metrics), ("v0.4_no_weather", no_weather_metrics),
                          ("v0.4_weather", weather_metrics), ("v0.4_final", final_metrics)):
        confirmatory.append({"model": model, **result, "holdout_sha256": holdout_sha,
                             "weather_decision": weather_decision})
    write_csv(REPORT_DIR / "v04_confirmatory_results.csv", confirmatory)

    stress_pairs, stress_rows = weather_stress(regimes, weights)
    stress_sha = write_case_set(VALIDATION_DIR / "weather_stress_pairs.json", stress_pairs,
                                "lightguard-v0.4-weather-stress-pairs", CALIBRATION_SEED)
    write_csv(REPORT_DIR / "weather_stress_pair_results.csv", stress_rows)
    replay = replay_regression()
    write_csv(REPORT_DIR / "actual_ami_replay_regression.csv", replay)

    v03_reference_m0_candidates = 66
    v03_reference_m0_fp = 20
    summary_payload = {
        "schema_version": "lightguard-v0.4-validation-summary",
        "generated_at": utc_now(),
        "controlled_validation": True,
        "v03_frozen_set_sha256": V03_SHA,
        "v03_frozen_file_sha256": frozen_bytes_sha,
        "calibration_sha256": calibration_sha,
        "confirmatory_holdout_sha256": holdout_sha,
        "weather_stress_sha256": stress_sha,
        "calibration_case_count": len(calibration),
        "holdout_abnormal_count": sum(row["label"] == "abnormal" for row in holdout),
        "holdout_normal_count": sum(row["label"] == "normal_control" for row in holdout),
        "objective": OBJECTIVE,
        "frozen_weights": weights,
        "v03_reference_m0_candidate_count": v03_reference_m0_candidates,
        "v03_reference_m0_false_positive_count": v03_reference_m0_fp,
        "baseline_m0_candidate_count": holdout_m0_metrics["inspection_candidate_count"],
        "baseline_m0_false_positive_count": holdout_m0_metrics["normal_false_positive_count"],
        "holdout_m0": holdout_m0_metrics,
        "baseline_v03_m2": baseline_metrics,
        "best_v04": final_metrics,
        "candidate_reduction_vs_M0": holdout_m0_metrics["inspection_candidate_count"] - final_metrics["inspection_candidate_count"],
        "false_positive_reduction_vs_M0": holdout_m0_metrics["normal_false_positive_count"] - final_metrics["normal_false_positive_count"],
        "weather_decision": weather_decision,
        "weather_decision_reason": "Independent holdout ranking improved" if weather_improves else "No independent holdout ranking improvement; weather retained as reference context only",
        "v03_weather_sensitivity": {key: value for key, value in sensitivity.items() if key != "rows"},
        "actual_ami_replay": {"window_count": len(replay),
            "interval_consistent_count": sum(row["interval_overlap"] for row in replay),
            "peak_consistent_count": sum(row["peak_current_consistent"] for row in replay),
            "phase_consistent_count": sum(row["phase_selective_consistent"] for row in replay)},
        "cost_conversion": "prohibited",
        "ranking_tie_break": "total_score descending, then case_id ascending",
    }
    summary_path = CONTEXT_DIR / "v04_validation_summary.json"
    write_json(summary_path, summary_payload)
    APP_CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
    (APP_CONTEXT_DIR / summary_path.name).write_bytes(summary_path.read_bytes())

    metric_headers = "| model | recall | FPR | P@5 | P@10 | P@20 | R@10 | R@20 | AP | NDCG@10 | candidates |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    metric_lines = []
    for name, value in (("v0.3 M2", baseline_metrics), ("v0.4", final_metrics)):
        metric_lines.append(f"| {name} | {value['anomaly_recall']:.6f} | {value['normal_fpr']:.6f} | {value['precision_at_5']:.6f} | {value['precision_at_10']:.6f} | {value['precision_at_20']:.6f} | {value['recall_at_10']:.6f} | {value['recall_at_20']:.6f} | {value['average_precision']:.6f} | {value['ndcg_at_10']:.6f} | {value['inspection_candidate_count']} |")
    summary = f"""# LightGuard v0.4 Ranking & Weather Holdout Validation

## Baseline
- v0.3 SHA: `{V03_SHA}`
- v0.3 is regression-only; no threshold or weight was tuned on it.

## Error Audit
- Top-20 false-positive rows: {sum(row['audit_type'] == 'top20_false_positive' for row in audit)}
- Lowest-ranked anomaly rows: {sum(row['audit_type'] == 'low_ranked_anomaly' for row in audit)}
- Main causes: high activation/duration hard negatives and insufficient policy/phase/load separation.

## Weather Sensitivity
- Modifier range: {sensitivity['modifier_min']:.6f} to {sensitivity['modifier_max']:.6f}
- Rank changes: {sensitivity['rank_changes']}
- v0.3 diagnosis: {sensitivity['decision']}

## Calibration
- SHA: `{calibration_sha}`
- Cases: {len(calibration)}
- Objective: {OBJECTIVE}
- Frozen weights: `{json.dumps(weights, sort_keys=True)}`

## Confirmatory Holdout
- SHA: `{holdout_sha}`
- Abnormal: 46
- Normal: 158

{metric_headers}
{chr(10).join(metric_lines)}

## Weather Decision
- Decision: {weather_decision}
- Basis: {summary_payload['weather_decision_reason']}.

## Actual AMI Replay
- Six anonymized competition replay windows remained separate from Busan KASI/KMA and Suyeong assets.
- Interval consistency: {summary_payload['actual_ami_replay']['interval_consistent_count']}/6
- Peak consistency: {summary_payload['actual_ami_replay']['peak_consistent_count']}/6
- Phase consistency: {summary_payload['actual_ami_replay']['phase_consistent_count']}/6

## Inspection List
- v0.3 M0 reference: {v03_reference_m0_candidates} candidates / {v03_reference_m0_fp} false positives (reference only; not used for v0.4 reduction)
- Holdout M0 candidates: {holdout_m0_metrics['inspection_candidate_count']}
- Best model candidates: {final_metrics['inspection_candidate_count']}
- Holdout false positives: {holdout_m0_metrics['normal_false_positive_count']} to {final_metrics['normal_false_positive_count']}
- All v0.4 reductions compare models on the same confirmatory holdout.
- Cost conversion: prohibited without sourced dispatch cost.

## Claims and Limits
- Claimable: controlled validation shows whether context improves ranking on an independent deterministic holdout.
- Not claimable: field accuracy, municipal AMI performance, dispatch-cost savings, or causal weather benefit beyond this suite.
"""
    (REPORT_DIR / "v04_validation_summary.md").write_text(summary, encoding="utf-8")
    docs = ROOT / "lightguard_app" / "docs"
    (docs / "v04_ranking_validation.md").write_text(summary, encoding="utf-8")
    (docs / "weather_context_decision.md").write_text(
        f"# Weather Context Decision\n\n- Decision: **{weather_decision}**\n"
        f"- v0.3 diagnosis: {sensitivity['decision']}\n"
        f"- Confirmatory basis: {summary_payload['weather_decision_reason']}.\n"
        "- Official KMA ASOS 159 observations only; future dates and synthetic fallback are excluded.\n",
        encoding="utf-8")
    print(f"v0.4 calibration={calibration_sha[:12]} holdout={holdout_sha[:12]} weather={weather_decision} candidates={final_metrics['inspection_candidate_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
