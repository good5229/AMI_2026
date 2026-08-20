#!/usr/bin/env python3
"""Summarize controlled factor effects on the frozen confirmatory holdout."""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from v08_detector import candidate, frozen_v04  # noqa: E402

HOLDOUT = ROOT / "lightguard_v0_1/data/validation/v08/v08_confirmatory_holdout.json"
FREEZE = ROOT / "lightguard_v0_1/data/validation/v08/v08_candidate_freeze.json"
OUTPUT = ROOT / "lightguard_v0_1/reports/v08/v08_factor_effects.csv"


def summarize(rows: list[dict]) -> dict:
    anomalies = [row for row in rows if row["label"] == "abnormal"]
    normals = [row for row in rows if row["label"] == "normal"]
    return {
        "total": len(rows),
        "anomalies": len(anomalies),
        "normals": len(normals),
        "recall": sum(row["decision"] == "anomaly" for row in anomalies) / len(anomalies) if anomalies else None,
        "fpr": sum(row["decision"] == "anomaly" for row in normals) / len(normals) if normals else None,
        "abstention_rate": sum(row["decision"] == "abstain" for row in rows) / len(rows),
    }


def main() -> None:
    cases = json.loads(HOLDOUT.read_text(encoding="utf-8"))["cases"]
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    configs = {model: payload["config"] for model, payload in freeze["models"].items()}
    factors = {
        "region": lambda row: row["region_id"],
        "season": lambda row: row["season"],
        "region_x_season": lambda row: f"{row['region_id']}:{row['season']}",
        "feature_availability": lambda row: row["feature_availability"],
        "scenario_type": lambda row: row["scenario_type"],
        "severity": lambda row: row["severity"],
    }
    output_rows = []
    for model in ("frozen_v04", "C1", "C2", "C3"):
        values = [frozen_v04(case) if model == "frozen_v04" else candidate(case, configs[model], model) for case in cases]
        scored = [{**case, **value} for case, value in zip(cases, values)]
        overall = summarize(scored)
        for factor, accessor in factors.items():
            groups: dict[str, list[dict]] = defaultdict(list)
            for row in scored:
                groups[accessor(row)].append(row)
            for level, rows in sorted(groups.items()):
                result = summarize(rows)
                output_rows.append({
                    "model": model,
                    "factor": factor,
                    "level": level,
                    "total": result["total"],
                    "anomalies": result["anomalies"],
                    "normals": result["normals"],
                    "recall": "" if result["recall"] is None else f"{result['recall']:.8f}",
                    "fpr": "" if result["fpr"] is None else f"{result['fpr']:.8f}",
                    "abstention_rate": f"{result['abstention_rate']:.8f}",
                    "recall_effect_vs_overall": "" if result["recall"] is None else f"{result['recall'] - overall['recall']:.8f}",
                    "fpr_effect_vs_overall": "" if result["fpr"] is None else f"{result['fpr'] - overall['fpr']:.8f}",
                    "interpretation": "controlled_generated_factor_effect_not_actual_region_effect",
                })
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"v0.8 factor analysis: {len(output_rows)} rows")


if __name__ == "__main__":
    main()
