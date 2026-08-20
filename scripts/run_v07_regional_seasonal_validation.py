#!/usr/bin/env python3
"""Build the v0.7 controlled regional-seasonal validation artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v07"
REPORTS = ROOT / "lightguard_v0_1/reports/v07"
APP_OUTPUT = ROOT / "lightguard_app/assets/data/context/v07_regional_seasonal_summary.json"
CONTEXT_PATH = DATA / "regional_seasonal_context_2025.json"
SEEDS = {
    "suyeong": ROOT / "lightguard_app/assets/data/suyeong_v02_seed.json",
    "gangneung": ROOT / "lightguard_app/assets/data/gangneung_v02_seed.json",
    "chungju": ROOT / "lightguard_app/assets/data/chungju_v02_seed.json",
}
FROZEN_CONFIG = {
    "activation_weight": 0.60,
    "duration_weight": 0.25,
    "load_mismatch_weight": 0.25,
    "phase_selectivity_weight": 0.20,
    "near_solar_boundary_penalty": 0.20,
    "transient_penalty": 0.20,
    "normal_partial_policy_penalty": 0.20,
    "weather_weight": 0.0,
    "threshold": 0.55,
}
CASE_SPECS = (
    ("normal_clean", "normal", 0.08, 5, 0.03, 0.00, False, False, False),
    ("normal_twilight_boundary", "normal", 0.65, 45, 0.05, 0.00, True, False, False),
    ("normal_transient", "normal", 0.60, 5, 0.05, 0.00, False, True, False),
    ("normal_partial_policy", "normal", 0.50, 60, 0.05, 0.00, False, False, True),
    ("post_sunrise_persistence", "anomaly", 0.20, 90, 0.30, 0.00, False, False, False),
    ("daytime_partial", "anomaly", 0.50, 45, 0.30, 0.00, False, False, False),
    ("daytime_full", "anomaly", 0.90, 30, 0.30, 0.00, False, False, False),
    ("phase_selective", "anomaly", 0.50, 45, 0.30, 0.90, False, False, False),
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def objects_from_seed(payload) -> list[dict]:
    if isinstance(payload, list):
        return payload
    for key in ("objects", "cabinets", "assets"):
        if isinstance(payload.get(key), list):
            return payload[key]
    raise ValueError("Seed does not contain an asset list")


def num(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def asset_stats(path: Path) -> dict[str, float | int]:
    assets = objects_from_seed(load_json(path))
    loads, lamps = [], []
    for asset in assets:
        expected = asset.get("expected_load") or asset.get("expectedLoad") or {}
        info = asset.get("asset_info") or asset.get("assetInfo") or {}
        load = num(expected.get("rated_power_w", expected.get("ratedPowerW", info.get("rated_power_w"))))
        lamp = num(expected.get("lamp_count", expected.get("lampCount", info.get("lamp_count"))))
        if load > 0:
            loads.append(load / 1000.0)
        if lamp > 0:
            lamps.append(lamp)
    return {
        "asset_count": len(assets),
        "rated_load_available": len(loads),
        "rated_load_coverage": round(len(loads) / len(assets), 8),
        "rated_load_status": "observed" if loads else "unavailable_no_imputation",
        "lamp_count_available": len(lamps),
        "lamp_count_coverage": round(len(lamps) / len(assets), 8),
        "median_rated_load_kw": round(median(loads), 6) if loads else 0.0,
        "median_lamp_count": round(median(lamps), 3) if lamps else 0,
    }


def parse_hhmm(day: str, value: str) -> datetime:
    digits = "".join(ch for ch in str(value) if ch.isdigit()).zfill(4)[-4:]
    return datetime.fromisoformat(day).replace(
        hour=int(digits[:2]), minute=int(digits[2:]), second=0, microsecond=0
    )


def weather_at_noon(cell: dict) -> dict:
    anchor = cell["anchor_date"].replace("-", "") + "1200"
    rows = cell["kma_observations"]
    selected = min(rows, key=lambda row: abs(int(str(row.get("tm", "0")).replace("-", "").replace(":", "").replace(" ", "")) - int(anchor)))
    return {
        "tm": selected.get("tm"),
        "temperature_c": num(selected.get("ta"), None),
        "humidity_pct": num(selected.get("hm"), None),
        "wind_speed_ms": num(selected.get("ws"), None),
        "precipitation_mm": num(selected.get("rn"), 0.0),
    }


def score(case: dict) -> float:
    duration_component = min(num(case["duration_min"]) / 90.0, 1.0)
    value = (
        FROZEN_CONFIG["activation_weight"] * num(case["activation"])
        + FROZEN_CONFIG["duration_weight"] * duration_component
        + FROZEN_CONFIG["load_mismatch_weight"] * num(case["load_mismatch"])
        + FROZEN_CONFIG["phase_selectivity_weight"] * num(case["phase_selectivity"])
    )
    if case["near_solar_boundary"]:
        value -= FROZEN_CONFIG["near_solar_boundary_penalty"]
    if case["transient"]:
        value -= FROZEN_CONFIG["transient_penalty"]
    if case["normal_partial_policy"]:
        value -= FROZEN_CONFIG["normal_partial_policy_penalty"]
    return round(max(0.0, min(1.0, value)), 8)


def wilson(successes: int, total: int) -> list[float]:
    if total == 0:
        return [0.0, 1.0]
    z = 1.959963984540054
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    radius = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return [round(max(0.0, centre - radius), 8), round(min(1.0, centre + radius), 8)]


def cell_metrics(rows: list[dict]) -> dict:
    anomalies = [row for row in rows if row["label"] == "anomaly"]
    normals = [row for row in rows if row["label"] == "normal"]
    tp = sum(row["detected"] for row in anomalies)
    fp = sum(row["detected"] for row in normals)
    return {
        "anomaly_count": len(anomalies),
        "normal_count": len(normals),
        "true_positive": tp,
        "false_positive": fp,
        "recall": round(tp / len(anomalies), 8),
        "fpr": round(fp / len(normals), 8),
        "recall_wilson_95": wilson(tp, len(anomalies)),
        "fpr_wilson_95": wilson(fp, len(normals)),
    }


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if not CONTEXT_PATH.exists():
        raise SystemExit(f"Missing official cache: run scripts/fetch_regional_seasonal_context.py")
    context = load_json(CONTEXT_PATH)
    regional_assets = {region: asset_stats(path) for region, path in SEEDS.items()}
    cases: list[dict] = []
    for cell in context["cells"]:
        region = cell["region_id"]
        stats = regional_assets[region]
        sunrise = parse_hhmm(cell["anchor_date"], cell["solar"]["sunrise"])
        noon = datetime.fromisoformat(cell["anchor_date"]).replace(hour=12)
        weather = weather_at_noon(cell)
        for index, spec in enumerate(CASE_SPECS):
            case_type, label, activation, duration, mismatch, phase, boundary, transient, policy = spec
            timestamp = sunrise + timedelta(minutes=15) if boundary else noon + timedelta(minutes=index)
            case = {
                "case_id": f"{cell['cell_id']}_{case_type}",
                "cell_id": cell["cell_id"],
                "region_id": region,
                "region_name_ko": cell["region_name_ko"],
                "season": cell["season"],
                "station_id": cell["station_id"],
                "cabinet_uid": f"{region}-distribution-proxy",
                "label": label,
                "case_type": case_type,
                "activation": activation,
                "duration_min": duration,
                "timestamp": timestamp.isoformat(),
                "rated_load_kw": stats["median_rated_load_kw"],
                "lamp_count": stats["median_lamp_count"],
                "load_mismatch": mismatch,
                "phase_selectivity": phase,
                "near_solar_boundary": boundary,
                "transient": transient,
                "normal_partial_policy": policy,
                "weather_sensitive": True,
                "weather_regime": cell["season"],
                "official_weather_context": weather,
                "official_solar_context": cell["solar"],
                "source": "controlled_regional_seasonal_v07",
            }
            case["score"] = score(case)
            case["detected"] = case["score"] >= FROZEN_CONFIG["threshold"]
            cases.append(case)

    metrics_by_cell = []
    for cell in context["cells"]:
        rows = [row for row in cases if row["cell_id"] == cell["cell_id"]]
        metrics_by_cell.append({
            "cell_id": cell["cell_id"],
            "region_id": cell["region_id"],
            "season": cell["season"],
            **cell_metrics(rows),
        })
    overall = cell_metrics(cases)
    macro_recall = round(mean(row["recall"] for row in metrics_by_cell), 8)
    macro_fpr = round(mean(row["fpr"] for row in metrics_by_cell), 8)
    worst = min(metrics_by_cell, key=lambda row: (row["recall"], -row["fpr"], row["cell_id"]))
    summary = {
        "schema_version": "lightguard.regional-seasonal-validation.v1",
        "validation_kind": "controlled_cross_context_invariance",
        "claim_boundary": "Not field or external regional AMI generalization.",
        "context_year": 2025,
        "region_count": 3,
        "season_count": 4,
        "cell_count": 12,
        "scenario_count": len(cases),
        "official_context": {
            "kma_station_ids": ["159", "105", "127"],
            "kma_hours_per_cell": 168,
            "kasi_area_context": True,
        },
        "regional_assets": regional_assets,
        "frozen_detector_config": FROZEN_CONFIG,
        "overall": overall,
        "macro_recall": macro_recall,
        "macro_fpr": macro_fpr,
        "worst_cell": worst,
        "cells": metrics_by_cell,
        "external_ami_validation": {
            "status": "unavailable",
            "reason": "Competition AMI contains five Busan B-line meters without municipal cabinet mapping; no Gangneung or Chungju field AMI is available.",
        },
    }

    DATA.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    cases_path = DATA / "regional_seasonal_cases.json"
    summary_path = DATA / "regional_seasonal_summary.json"
    write_json(cases_path, {"schema_version": "lightguard.regional-seasonal-cases.v1", "cases": cases})
    write_json(summary_path, summary)
    write_json(APP_OUTPUT, summary)

    csv_path = REPORTS / "cell_metrics.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(metrics_by_cell[0].keys()))
        writer.writeheader()
        writer.writerows(metrics_by_cell)

    report = f"""# LightGuard v0.7 regional-seasonal validation

## Result

- Scope: 3 regions x 4 seasons = 12 controlled cells, 96 scenarios
- Macro recall: {macro_recall:.4f}
- Macro FPR: {macro_fpr:.4f}
- Worst cell: {worst['cell_id']} (recall {worst['recall']:.4f}, FPR {worst['fpr']:.4f})
- Official context: KMA ASOS stations 159, 105, 127 and KASI area solar times
- Detector: v0.4 frozen threshold/configuration, weather weight 0.0

## Interpretation boundary

This is controlled cross-context invariance evidence. It does not demonstrate
field performance or external AMI generalization in Gangneung or Chungju.
Each cell has four anomaly and four normal cases, so Wilson intervals remain
wide and point estimates must not be presented without their intervals.
"""
    (REPORTS / "regional_seasonal_generalization.md").write_text(report, encoding="utf-8")
    (REPORTS / "external_ami_boundary.md").write_text(
        "# External AMI boundary\n\n"
        "Status: unavailable.\n\n"
        "The available competition AMI consists of five Busan B-line meters and "
        "has no verified mapping to municipal distribution cabinets. No field AMI "
        "for Gangneung or Chungju is available. v0.7 therefore evaluates controlled "
        "regional-seasonal scenarios only and makes no deployment-performance claim.\n",
        encoding="utf-8",
    )
    manifest_targets = [CONTEXT_PATH, cases_path, summary_path, csv_path, REPORTS / "regional_seasonal_generalization.md", REPORTS / "external_ami_boundary.md"]
    manifest = {
        "schema_version": "lightguard.v07-manifest.v1",
        "files": {str(path.relative_to(ROOT)): sha256(path) for path in manifest_targets},
    }
    write_json(REPORTS / "reproducibility_manifest.json", manifest)
    print(json.dumps({"cells": 12, "scenarios": len(cases), "macro_recall": macro_recall, "macro_fpr": macro_fpr, "worst_cell": worst["cell_id"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
