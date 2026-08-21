#!/usr/bin/env python3
"""Materialize and evaluate v0.8 calibration data without reading holdout rows."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from v08_detector import candidate, frozen_v04, metrics  # noqa: E402

DESIGN = ROOT / "lightguard_v0_1/data/validation/v08_design_matrix.csv"
CONTEXT = ROOT / "lightguard_v0_1/data/validation/v07/regional_seasonal_context_2025.json"
OUT = ROOT / "lightguard_v0_1/data/validation/v08/v08_calibration_set.json"
FREEZE = ROOT / "lightguard_v0_1/data/validation/v08/v08_candidate_freeze.json"
RESULTS = ROOT / "lightguard_v0_1/reports/v08/v08_calibration_results.csv"
DESIGN_SHA = "9fba439a9bd22d184e6a705af559a9b43a39fb4b9498cfa3d3a50c2f5853dbb0"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json(payload) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def load_calibration_rows() -> list[dict]:
    if sha256_bytes(DESIGN.read_bytes()) != DESIGN_SHA:
        raise ValueError("v0.8 design freeze mismatch")
    with DESIGN.open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row["split"] == "calibration"]
    if len(rows) != 288 or any(row["split"] != "calibration" for row in rows):
        raise ValueError("Calibration boundary failure")
    return rows


def materialize(row: dict, cell: dict) -> dict:
    feature_state = row["feature_availability"]
    rated_available = row["rated_load_status"] == "available" and feature_state != "load_unavailable"
    phase_available = row["phase_pattern"] != "not_applicable" and feature_state != "phase_unavailable"
    weather_available = feature_state != "weather_unavailable"
    activation = float(row["activation_fraction"])
    expected = 1.0 if row["solar_position"] == "night" else 0.5 if row["solar_position"] == "twilight_boundary" else 0.0
    observation = None
    if weather_available:
        observations = cell["kma_observations"]
        observation = observations[int(row["random_seed"]) % len(observations)]
    regime_uncertainty = {"clear": 0.0, "high_cloud": 0.35, "overcast": 0.65, "rainfall": 1.0}[row["weather_regime"]]
    scenario_type = row["scenario_type"]
    return {
        "case_id": row["case_id"],
        "split": "calibration",
        "region_id": row["region_id"],
        "season": row["season"],
        "cell_id": f"{row['region_id']}_{row['season']}",
        "asset_cabinet_uid": row["asset_cabinet_uid"],
        "asset_stratum": row["asset_stratum"],
        "label": row["label"],
        "scenario_type": scenario_type,
        "severity": row["severity"],
        "duration_min": int(row["duration_min"]),
        "solar_position": row["solar_position"],
        "phase_pattern": row["phase_pattern"],
        "weather_regime": row["weather_regime"],
        "feature_availability": feature_state,
        "rated_load_status": row["rated_load_status"],
        "rated_load_w": float(row["rated_load_w"]) if row["rated_load_w"] else None,
        "activation_fraction": activation,
        "expected_activation_fraction": expected,
        "activation_evidence": abs(activation - expected),
        "load_mismatch": abs(float(row["observed_load_ratio"]) - 1.0) if rated_available else None,
        "phase_selectivity": float(row["phase_imbalance_ratio"]) if phase_available else None,
        "near_solar_boundary": row["solar_position"] in {"twilight_boundary", "pre_sunset"},
        "transient": "transient" in scenario_type or "temporary" in scenario_type,
        "normal_partial_policy": scenario_type == "allowed_partial_operation",
        "weather_available": weather_available,
        "weather_uncertainty": regime_uncertainty,
        "official_weather_context": observation,
        "official_solar_context": cell["solar"],
        "random_seed": int(row["random_seed"]),
        "factor_tuple_id": row["factor_tuple_id"],
        "signal_parameter_id": row["signal_parameter_id"],
        "source": "v08_controlled_calibration_not_actual_ami",
    }


def evaluate(cases: list[dict], variant: str, config: dict) -> dict:
    outcomes = [frozen_v04(case) if variant == "frozen_v04" else candidate(case, config, variant) for case in cases]
    return metrics(cases, outcomes)


def feasible(result: dict) -> bool:
    return result["fpr"] <= 0.05 and result["hard_negative_fpr"] <= 0.05


def choose(cases: list[dict], variant: str, configs: list[dict]) -> tuple[dict, dict]:
    evaluated = [(config, evaluate(cases, variant, config)) for config in configs]
    constrained = [item for item in evaluated if feasible(item[1])]
    pool = constrained or evaluated
    return max(
        pool,
        key=lambda item: (
            item[1]["recall"],
            item[1]["weak_recall"],
            item[1]["average_precision"],
            -item[1]["fpr"],
            -item[1]["abstention_rate"],
            json.dumps(item[0], sort_keys=True),
        ),
    )


def main() -> None:
    context_payload = json.loads(CONTEXT.read_text(encoding="utf-8"))
    context = {cell["cell_id"]: cell for cell in context_payload["cells"]}
    design_rows = load_calibration_rows()
    cases = [materialize(row, context[f"{row['region_id']}_{row['season']}"]) for row in design_rows]
    calibration_payload = {
        "schema_version": "lightguard.v08-calibration.v1",
        "split": "calibration",
        "design_sha256": DESIGN_SHA,
        "case_count": len(cases),
        "v07_cases_ingested": False,
        "actual_ami": False,
        "cases": cases,
    }
    calibration_bytes = canonical_json(calibration_payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(calibration_bytes)
    calibration_sha = sha256_bytes(calibration_bytes)

    baseline_result = evaluate(cases, "frozen_v04", {})
    c1_configs = [
        {"interaction_weight": interaction, "load_weight": load, "phase_weight": phase}
        for interaction, load, phase in itertools.product((0.30, 0.45, 0.60), (0.25, 0.35), (0.20, 0.30))
    ]
    c1_config, c1_result = choose(cases, "C1", c1_configs)
    c2_configs = [
        {**c1_config, "availability_boost": boost, "abstain_margin": margin}
        for boost, margin in itertools.product((0.0, 0.10, 0.20), (0.05, 0.10))
    ]
    c2_config, c2_result = choose(cases, "C2", c2_configs)
    c3_configs = [{**c2_config, "weather_weight": weight} for weight in (0.02, 0.05, 0.08)]
    c3_config, c3_result = choose(cases, "C3", c3_configs)
    models = {
        "frozen_v04": {"config": {"threshold": 0.55}, "metrics": baseline_result},
        "C1": {"config": {**c1_config, "threshold": 0.55}, "metrics": c1_result},
        "C2": {"config": {**c2_config, "threshold": 0.55}, "metrics": c2_result},
        "C3": {"config": {**c3_config, "threshold": 0.55}, "metrics": c3_result},
    }
    freeze = {
        "schema_version": "lightguard.v08-candidate-freeze.v1",
        "calibration_sha256": calibration_sha,
        "design_sha256": DESIGN_SHA,
        "threshold_policy": "fixed_at_0.55_not_lowered",
        "selection_objective": "maximize recall then weak recall and AP subject to FPR and hard-negative FPR <= 0.05",
        "confirmatory_seen": False,
        "models": models,
    }
    freeze_bytes = canonical_json(freeze)
    FREEZE.write_bytes(freeze_bytes)
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    fields = ["model", "recall", "fpr", "hard_negative_fpr", "weak_recall", "precision", "average_precision", "balanced_accuracy", "worst_cell_recall", "abstention_rate", "feasible", "config_json"]
    with RESULTS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for model, payload in models.items():
            result = payload["metrics"]
            writer.writerow({
                "model": model,
                **{key: result[key] for key in fields[1:10]},
                "feasible": feasible(result),
                "config_json": json.dumps(payload["config"], sort_keys=True, separators=(",", ":")),
            })
    print(json.dumps({
        "calibration_cases": len(cases),
        "calibration_sha256": calibration_sha,
        "candidate_freeze_sha256": sha256_bytes(freeze_bytes),
        "metrics": {model: payload["metrics"] for model, payload in models.items()},
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
