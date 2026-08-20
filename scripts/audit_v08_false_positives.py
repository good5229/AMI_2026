#!/usr/bin/env python3
"""Create a deterministic, no-tuning inventory of frozen v0.8 false positives."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from v08_detector import THRESHOLD, candidate  # noqa: E402

CALIBRATION = ROOT / "lightguard_v0_1/data/validation/v08/v08_calibration_set.json"
CONFIRMATORY = ROOT / "lightguard_v0_1/data/validation/v08/v08_confirmatory_holdout.json"
FREEZE = ROOT / "lightguard_v0_1/data/validation/v08/v08_candidate_freeze.json"
INVENTORY = ROOT / "lightguard_v0_1/reports/v09/v08_false_positive_inventory.csv"
TAXONOMY = ROOT / "lightguard_v0_1/reports/v09/v08_false_positive_taxonomy.md"

EXPECTED_SHA256 = {
    CALIBRATION: "b9825d7b8d336de9421a5941d2c7f069202b3f402fa4090b2837abb7d3a38b2f",
    CONFIRMATORY: "71a4d7099be61f073f8411acd3b0af999dd672060dde9621513e0505e32c1a1d",
    FREEZE: "12fdb827f3b3d553707b616425bbc9721405df7623d40c79a87169589eed2b35",
}
EXPECTED_CASE_COUNTS = {"calibration": 288, "confirmatory": 432}
MODELS = ("C1", "C2", "C3")
FAMILIES = (
    "solar_boundary_normal",
    "weather_context_normal",
    "missing_load_phase_normal",
    "persistence_artifact_normal",
    "near_threshold_load_variation",
    "other_evidence_grounded_normal",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def boolean(value: bool) -> str:
    return "true" if value else "false"


def is_weather_context(case: dict) -> bool:
    return (
        case["weather_available"]
        and case["weather_regime"] in {"high_cloud", "overcast", "rainfall"}
    )


def is_missing_load_or_phase(case: dict) -> bool:
    return case["load_mismatch"] is None or case["phase_selectivity"] is None


def is_persistence_artifact(case: dict) -> bool:
    return (
        case["duration_min"] >= 60
        and not case["transient"]
        and not case["normal_partial_policy"]
    )


def is_near_threshold_load_variation(case: dict, outcome: dict) -> bool:
    return (
        case["load_mismatch"] is not None
        and 0.0 < case["load_mismatch"] <= 0.06
        and 0.0 <= outcome["score"] - THRESHOLD <= 0.10
    )


def evidence_flags(case: dict, outcome: dict) -> list[str]:
    flags = []
    if case["near_solar_boundary"]:
        flags.append("solar_boundary")
    if is_weather_context(case):
        flags.append("weather_context")
    if case["load_mismatch"] is None:
        flags.append("missing_load")
    if case["phase_selectivity"] is None:
        flags.append("missing_phase")
    if is_persistence_artifact(case):
        flags.append("persistence")
    if is_near_threshold_load_variation(case, outcome):
        flags.append("near_threshold_load_variation")
    return flags or ["other"]


def primary_family(case: dict, outcome: dict) -> str:
    """Use a fixed priority while preserving all overlapping flags separately."""
    if case["near_solar_boundary"]:
        return "solar_boundary_normal"
    if is_weather_context(case):
        return "weather_context_normal"
    if is_missing_load_or_phase(case):
        return "missing_load_phase_normal"
    if is_persistence_artifact(case):
        return "persistence_artifact_normal"
    if is_near_threshold_load_variation(case, outcome):
        return "near_threshold_load_variation"
    return "other_evidence_grounded_normal"


def validate_source(path: Path, split: str) -> dict:
    actual_sha = sha256(path)
    if actual_sha != EXPECTED_SHA256[path]:
        raise ValueError(f"Frozen v0.8 source hash mismatch: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("split") != split or payload.get("case_count") != EXPECTED_CASE_COUNTS[split]:
        raise ValueError(f"Frozen v0.8 {split} boundary mismatch")
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) != EXPECTED_CASE_COUNTS[split]:
        raise ValueError(f"Frozen v0.8 {split} cases mismatch")
    return payload


def normalize(case: dict, model: str, outcome: dict) -> dict:
    if case["label"] != "normal" or outcome["decision"] != "anomaly":
        raise ValueError("Inventory rows must be normal cases decided as anomaly")
    flags = evidence_flags(case, outcome)
    return {
        "split": case["split"],
        "model": model,
        "case_id": case["case_id"],
        "asset_cabinet_uid": case["asset_cabinet_uid"],
        "region_id": case["region_id"],
        "season": case["season"],
        "cell_id": case["cell_id"],
        "original_label": case["label"],
        "scenario_type": case["scenario_type"],
        "severity": case["severity"],
        "factor_tuple_id": case["factor_tuple_id"],
        "signal_parameter_id": case["signal_parameter_id"],
        "random_seed": case["random_seed"],
        "decision": outcome["decision"],
        "score": f"{outcome['score']:.8f}",
        "threshold": f"{THRESHOLD:.8f}",
        "score_margin": f"{outcome['score'] - THRESHOLD:.8f}",
        "taxonomy_family": primary_family(case, outcome),
        "evidence_flags": ";".join(flags),
        "solar_position": case["solar_position"],
        "near_solar_boundary": boolean(case["near_solar_boundary"]),
        "weather_regime": case["weather_regime"],
        "weather_available": boolean(case["weather_available"]),
        "feature_availability": case["feature_availability"],
        "rated_load_status": case["rated_load_status"],
        "load_mismatch": "" if case["load_mismatch"] is None else f"{case['load_mismatch']:.8f}",
        "phase_selectivity": "" if case["phase_selectivity"] is None else f"{case['phase_selectivity']:.8f}",
        "duration_min": case["duration_min"],
        "transient": boolean(case["transient"]),
        "normal_partial_policy": boolean(case["normal_partial_policy"]),
    }


def audit(payloads: list[dict], configs: dict) -> list[dict]:
    rows = []
    for payload in payloads:
        for model in MODELS:
            for case in payload["cases"]:
                outcome = candidate(case, configs[model], model)
                if case["label"] == "normal" and outcome["decision"] == "anomaly":
                    rows.append(normalize(case, model, outcome))
    return sorted(rows, key=lambda row: (row["split"], row["model"], row["case_id"]))


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    body = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    body.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(body)


def write_taxonomy(rows: list[dict]) -> None:
    primary = Counter((row["split"], row["model"], row["taxonomy_family"]) for row in rows)
    flags = Counter()
    for row in rows:
        for flag in row["evidence_flags"].split(";"):
            flags[(row["split"], row["model"], flag)] += 1

    primary_rows = []
    flag_rows = []
    for split in ("calibration", "confirmatory"):
        for model in MODELS:
            for family in FAMILIES:
                primary_rows.append([split, model, family, str(primary[(split, model, family)])])
            for flag in ("solar_boundary", "weather_context", "missing_load", "missing_phase", "persistence", "near_threshold_load_variation", "other"):
                flag_rows.append([split, model, flag, str(flags[(split, model, flag)])])

    report = f"""# v0.8 False-Positive Taxonomy for v0.9 Forensics

## Scope and frozen boundary

This is a deterministic, row-level audit of the frozen v0.8 calibration and
confirmatory sets. It replays only the frozen C1/C2/C3 configurations at their
frozen threshold of `{THRESHOLD:.2f}`. It does not edit the detector, v0.8 data,
or v0.8 results, and it does not select or tune a v0.9 candidate.

- Calibration source SHA-256: `{EXPECTED_SHA256[CALIBRATION]}`
- Confirmatory source SHA-256: `{EXPECTED_SHA256[CONFIRMATORY]}`
- Candidate-freeze SHA-256: `{EXPECTED_SHA256[FREEZE]}`
- Calibration/confirmatory case counts: `288` / `432`
- Inventory definition: original label `normal` and frozen model decision `anomaly`
- The inventory retains original case, asset, factor-tuple, signal-parameter, and seed identifiers.

The resulting calibration false-positive count is expected to be zero under the
frozen selected C1/C2/C3 configurations. Confirmatory false positives are
failure-analysis evidence only; they are not available for v0.9 tuning.

## Primary-family rule

Each inventory row has exactly one primary family so counts are additive. Fixed
priority is: solar boundary, weather context, missing load/phase, persistence,
near-threshold load variation, then other. `evidence_flags` in the CSV preserves
all overlapping evidence, so a primary solar-boundary row can still be counted as
weather-context or missing-feature evidence below.

Definitions:

- `solar_boundary_normal`: `near_solar_boundary=true` from the frozen scenario.
- `weather_context_normal`: weather is available and frozen regime is `high_cloud`, `overcast`, or `rainfall`.
- `missing_load_phase_normal`: frozen `load_mismatch` or `phase_selectivity` is absent; absence is retained, never imputed.
- `persistence_artifact_normal`: non-transient, non-policy normal with duration at least 60 minutes.
- `near_threshold_load_variation`: available load mismatch in `(0, 0.06]` and score margin in `[0, 0.10]`.
- `other_evidence_grounded_normal`: no preceding observable rule applies.

## Additive primary-family counts

{markdown_table(["split", "model", "primary family", "false positives"], primary_rows)}

## Overlapping evidence-flag counts

{markdown_table(["split", "model", "evidence flag", "false positives"], flag_rows)}

## Interpretation boundary

The taxonomy identifies controlled hard-negative mechanisms represented in the
frozen v0.8 design. It is not a fault label, municipal AMI estimate, or proof of
field behavior. The KMA regime is retained as experiment context; v0.8's
non-promoted weather candidate remains context-only and this audit makes no
weather-policy claim.
"""
    TAXONOMY.parent.mkdir(parents=True, exist_ok=True)
    TAXONOMY.write_text(report, encoding="utf-8")


def main() -> None:
    calibration = validate_source(CALIBRATION, "calibration")
    confirmatory = validate_source(CONFIRMATORY, "confirmatory")
    if sha256(FREEZE) != EXPECTED_SHA256[FREEZE]:
        raise ValueError("Frozen v0.8 candidate configuration hash mismatch")
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if freeze.get("confirmatory_seen") is not False:
        raise ValueError("v0.8 candidate freeze must precede confirmatory inspection")
    configs = {model: freeze["models"][model]["config"] for model in MODELS}
    if any(config.get("threshold") != THRESHOLD for config in configs.values()):
        raise ValueError("Frozen v0.8 threshold mismatch")

    rows = audit([calibration, confirmatory], configs)
    fields = list(rows[0]) if rows else [
        "split", "model", "case_id", "asset_cabinet_uid", "region_id", "season", "cell_id",
        "original_label", "scenario_type", "severity", "factor_tuple_id", "signal_parameter_id",
        "random_seed", "decision", "score", "threshold", "score_margin", "taxonomy_family",
        "evidence_flags", "solar_position", "near_solar_boundary", "weather_regime", "weather_available",
        "feature_availability", "rated_load_status", "load_mismatch", "phase_selectivity", "duration_min",
        "transient", "normal_partial_policy",
    ]
    INVENTORY.parent.mkdir(parents=True, exist_ok=True)
    with INVENTORY.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    write_taxonomy(rows)

    print(json.dumps({
        "inventory_rows": len(rows),
        "by_split_model": {
            f"{split}:{model}": sum(row["split"] == split and row["model"] == model for row in rows)
            for split in ("calibration", "confirmatory") for model in MODELS
        },
        "inventory": str(INVENTORY.relative_to(ROOT)),
        "taxonomy": str(TAXONOMY.relative_to(ROOT)),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
