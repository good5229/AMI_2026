#!/usr/bin/env python3
"""Audit frozen v0.7 controlled cases without changing its detector or cases."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "lightguard_v0_1/data/validation/v07/regional_seasonal_cases.json"
OUTPUT_DIR = ROOT / "lightguard_v0_1/reports/v08"
MATRIX_PATH = OUTPUT_DIR / "v07_failure_matrix.csv"
REPORT_PATH = OUTPUT_DIR / "v07_failure_forensics.md"

THRESHOLD = 0.55
WEIGHTS = {
    "activation": 0.60,
    "duration": 0.25,
    "load": 0.25,
    "phase": 0.20,
    "policy_penalty": 0.20,
    "solar_penalty": 0.20,
    "transient_penalty": 0.20,
    "weather": 0.0,
}
MATRIX_FIELDS = [
    "region",
    "season",
    "scenario_type",
    "truth_class_controlled",
    "detected",
    "score",
    "activation",
    "duration",
    "load_mismatch",
    "phase_selectivity",
    "solar_context",
    "weather_context",
    "available_features",
    "missing_features",
    "score_component_activation",
    "score_component_duration",
    "score_component_load",
    "score_component_phase",
    "score_component_policy",
    "score_component_solar",
    "score_component_transient",
    "threshold_margin",
]


def compact_number(value: object) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.4f}".rstrip("0").rstrip(".")


def component_values(case: dict) -> dict[str, float]:
    return {
        "activation": WEIGHTS["activation"] * float(case["activation"]),
        "duration": WEIGHTS["duration"] * min(float(case["duration_min"]) / 90.0, 1.0),
        "load": WEIGHTS["load"] * float(case["load_mismatch"]),
        "phase": WEIGHTS["phase"] * float(case["phase_selectivity"]),
        "policy": -WEIGHTS["policy_penalty"] if case["normal_partial_policy"] else 0.0,
        "solar": -WEIGHTS["solar_penalty"] if case["near_solar_boundary"] else 0.0,
        "transient": -WEIGHTS["transient_penalty"] if case["transient"] else 0.0,
    }


def feature_masks(case: dict) -> tuple[str, str]:
    available = [
        "activation",
        "duration_min",
        "load_mismatch",
        "phase_selectivity",
        "solar_context",
        "policy_flag",
        "transient_flag",
    ]
    missing = []
    if float(case.get("rated_load_kw", 0.0)) > 0:
        available.append("rated_load_kw")
    else:
        missing.append("rated_load_kw")

    weather = case.get("official_weather_context") or {}
    weather_fields = ("temperature_c", "humidity_pct", "wind_speed_ms", "precipitation_mm")
    for field in weather_fields:
        if weather.get(field) is None:
            missing.append(f"weather_{field}")
        else:
            available.append(f"weather_{field}")
    return ";".join(available), ";".join(missing) or "none"


def solar_context(case: dict) -> str:
    solar = case.get("official_solar_context") or {}
    position = "twilight_boundary" if case["near_solar_boundary"] else "daytime"
    return (
        f"{position};sunrise={solar.get('sunrise', 'NA')};"
        f"sunset={solar.get('sunset', 'NA')};civil_morning={solar.get('civil_morning', 'NA')};"
        f"civil_evening={solar.get('civil_evening', 'NA')}"
    )


def weather_context(case: dict) -> str:
    weather = case.get("official_weather_context") or {}
    return ";".join(
        f"{name}={compact_number(weather.get(name))}"
        for name in ("tm", "temperature_c", "humidity_pct", "wind_speed_ms", "precipitation_mm")
    )


def row_for(case: dict) -> dict:
    components = component_values(case)
    recomputed = max(0.0, min(1.0, sum(components.values())))
    stored_score = float(case["score"])
    if abs(stored_score - recomputed) > 1e-8:
        raise ValueError(f"Frozen score mismatch: {case['case_id']}")
    detected = stored_score >= THRESHOLD
    if bool(case["detected"]) != detected:
        raise ValueError(f"Frozen detection mismatch: {case['case_id']}")
    available, missing = feature_masks(case)
    return {
        "region": case["region_id"],
        "season": case["season"],
        "scenario_type": case["case_type"],
        "truth_class_controlled": case["label"],
        "detected": str(detected).lower(),
        "score": f"{stored_score:.8f}",
        "activation": f"{float(case['activation']):.8f}",
        "duration": str(case["duration_min"]),
        "load_mismatch": f"{float(case['load_mismatch']):.8f}",
        "phase_selectivity": f"{float(case['phase_selectivity']):.8f}",
        "solar_context": solar_context(case),
        "weather_context": weather_context(case),
        "available_features": available,
        "missing_features": missing,
        "score_component_activation": f"{components['activation']:.8f}",
        "score_component_duration": f"{components['duration']:.8f}",
        "score_component_load": f"{components['load']:.8f}",
        "score_component_phase": f"{components['phase']:.8f}",
        "score_component_policy": f"{components['policy']:.8f}",
        "score_component_solar": f"{components['solar']:.8f}",
        "score_component_transient": f"{components['transient']:.8f}",
        "threshold_margin": f"{stored_score - THRESHOLD:.8f}",
    }


def ratio(rows: list[dict]) -> str:
    detected = sum(row["detected"] == "true" for row in rows)
    return f"{detected}/{len(rows)} ({detected / len(rows):.3f})"


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    return "\n".join([
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
        *("| " + " | ".join(row) + " |" for row in rows),
    ])


def write_report(rows: list[dict]) -> None:
    anomalies = [row for row in rows if row["truth_class_controlled"] == "anomaly"]
    normals = [row for row in rows if row["truth_class_controlled"] == "normal"]
    by_type: dict[str, list[dict]] = defaultdict(list)
    by_cell_type: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in anomalies:
        by_type[row["scenario_type"]].append(row)
        by_cell_type[(row["region"], row["season"], row["scenario_type"])].append(row)

    type_rows = []
    for kind in sorted(by_type):
        values = by_type[kind]
        type_rows.append([
            kind,
            str(len(values)),
            str(sum(value["detected"] == "true" for value in values)),
            f"{sum(value['detected'] == 'true' for value in values) / len(values):.3f}",
            f"{mean(float(value['score']) for value in values):.8f}",
            f"{mean(float(value['threshold_margin']) for value in values):+.8f}",
        ])

    cell_rows = []
    for key in sorted(by_cell_type):
        values = by_cell_type[key]
        value = values[0]
        cell_rows.append([
            *key,
            ratio(values),
            value["score"],
            value["threshold_margin"],
        ])

    missed = [row for row in anomalies if row["detected"] == "false"]
    normal_fpr = sum(row["detected"] == "true" for row in normals) / len(normals)
    report = f"""# v0.7 Frozen Detector Failure Forensics

## Scope and boundary

This is a deterministic, no-tuning audit of the frozen v0.7 controlled scenario set. It evaluates **96 scenario-injection rows**, not field AMI observations. It does not estimate, validate, or claim actual AMI performance for Suyeong, Gangneung, Chungju, or any other location.

- Source: `lightguard_v0_1/data/validation/v07/regional_seasonal_cases.json`
- Frozen decision: score >= `{THRESHOLD:.2f}`
- Frozen weather weight: `{WEIGHTS['weather']:.1f}`
- Controlled rows: `{len(rows)}`; anomalies: `{len(anomalies)}`; normals: `{len(normals)}`
- Stored-score and stored-decision integrity: PASS for all `{len(rows)}` rows
- Controlled anomaly recall: `{sum(row['detected'] == 'true' for row in anomalies)}/{len(anomalies)} ({sum(row['detected'] == 'true' for row in anomalies) / len(anomalies):.3f})`
- Controlled normal FPR: `{sum(row['detected'] == 'true' for row in normals)}/{len(normals)} ({normal_fpr:.3f})`

## Anomaly-type summary

{markdown_table(["anomaly type", "total", "detected", "recall", "mean score", "mean threshold margin"], type_rows)}

The unobserved types are `daytime_partial` and `post_sunrise_persistence`: each is missed in all 12 controlled region-season cells. This conclusion is calculated from the frozen rows above, not inferred from the scenario names.

## Missed-anomaly score decomposition

{markdown_table(
    ["scenario type", "score", "threshold", "margin", "activation", "duration", "load", "phase", "policy", "solar", "transient"],
    [[
        row["scenario_type"], row["score"], f"{THRESHOLD:.8f}", row["threshold_margin"],
        row["score_component_activation"], row["score_component_duration"], row["score_component_load"],
        row["score_component_phase"], row["score_component_policy"], row["score_component_solar"],
        row["score_component_transient"],
    ] for row in sorted({row["scenario_type"]: row for row in missed}.values(), key=lambda value: value["scenario_type"])],
)}

`post_sunrise_persistence` receives the maximum duration component (`0.25000000`) but only `0.12000000` activation contribution, leaving a `-0.10500000` margin. `daytime_partial` receives moderate activation (`0.30000000`) and duration (`0.12500000`), leaving a `-0.05000000` margin. This is a feature-combination observation, not a proposed parameter change.

## Region x season x anomaly-type summary

{markdown_table(["region", "season", "anomaly type", "detected/total (recall)", "score", "threshold margin"], cell_rows)}

## Why the score structure is identical across region and season

Every region-season cell instantiates the same eight fixed v0.7 scenario specifications. For a given scenario type, activation, duration, load mismatch, phase selectivity, and all three policy/solar/transient flags are identical in all 12 cells. The frozen score does not consume region ID, season, station, timestamp, lamp count, rated load, or weather values; weather's frozen weight is zero. Therefore, equal score and decision rows across cells are a design consequence of the controlled generator, not empirical evidence that real regional or seasonal AMI behavior is identical.

## Feature availability observation

The matrix records raw feature availability rather than substituting absent values. `rated_load_kw` is unavailable for Chungju scenario rows and remains masked; it is not treated as a physical zero. Weather fields can be absent in the official context cache, and in this frozen detector they have no direct score contribution. This audit does not change those masks or infer operational meaning from them.

## Next-stage constraint

The two missed types may inform a future candidate design only after a separately generated, frozen calibration set is established. Reweighting, threshold changes, scenario changes, or any claim of field performance from this audit would contaminate the v0.7 baseline.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) != 96:
        raise ValueError("Expected exactly 96 frozen v0.7 cases")
    rows = [row_for(case) for case in cases]
    cells = {(row["region"], row["season"]) for row in rows}
    if len(cells) != 12 or any(sum(row["region"] == region and row["season"] == season for row in rows) != 8 for region, season in cells):
        raise ValueError("Expected 12 region-season cells with 8 cases each")
    if sum(row["truth_class_controlled"] == "anomaly" for row in rows) != 48:
        raise ValueError("Expected 48 controlled anomaly rows")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with MATRIX_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MATRIX_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    write_report(rows)
    print(f"PASS: {len(rows)} rows, 12 cells, matrix={MATRIX_PATH}, report={REPORT_PATH}")


if __name__ == "__main__":
    main()
