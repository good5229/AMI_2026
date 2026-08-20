#!/usr/bin/env python3
"""Select and freeze v0.9 candidate configurations using calibration only."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
from pathlib import Path

from v09_detector import THRESHOLDS, WEATHER_WEIGHT, decide, metrics

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v09"
REPORT = ROOT / "lightguard_v0_1/reports/v09/v09_calibration_results.csv"


def feasible(result: dict) -> bool:
    return (result["recall"] >= .70 and result["fpr"] <= .05 and result["hard_negative_fpr"] <= .05
            and result["worst_cell_recall"] >= .55 and result["average_precision"] >= .90
            and result["abstention_rate"] <= .10)


def main() -> None:
    path = DATA / "v09_calibration_set.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    cases = payload["cases"]
    rows = []
    configs = []
    for threshold in THRESHOLDS:
        configs.append(("threshold_only", {"stage_a_threshold": threshold}))
    for architecture in ("H1", "H2", "H3"):
        for stage_a_threshold, specificity_threshold in itertools.product(THRESHOLDS, repeat=2):
            configs.append((architecture, {"stage_a_threshold": stage_a_threshold, "specificity_threshold": specificity_threshold,
                                           "weather_weight": WEATHER_WEIGHT, "availability_floor": .60 if architecture in {"H2", "H3"} else None}))
    best = {}
    for architecture, config in configs:
        outcomes = [decide(case, architecture, config) for case in cases]
        result = metrics(cases, outcomes)
        row = {"architecture": architecture, **config, **{key: result[key] for key in (
            "recall", "fpr", "hard_negative_fpr", "average_precision", "worst_cell_recall", "abstention_rate")},
               "feasible": feasible(result) if architecture != "threshold_only" else False,
               "metrics_json": json.dumps(result, sort_keys=True, separators=(",", ":"))}
        rows.append(row)
        current = best.get(architecture)
        rank = (result["fpr"] <= .05, result["hard_negative_fpr"] <= .05, result["recall"], result["average_precision"],
                result["worst_cell_recall"], -result["abstention_rate"], -config.get("stage_a_threshold", 0), -config.get("specificity_threshold", 0))
        if current is None or rank > current[0]:
            best[architecture] = (rank, config, result)
    eligible = [(name, value) for name, value in best.items() if name != "threshold_only" and feasible(value[2])]
    selected = max(eligible, key=lambda item: (item[1][2]["recall"], item[1][2]["average_precision"],
                                                item[1][2]["worst_cell_recall"], -item[1][2]["abstention_rate"], item[0])) if eligible else None
    freeze = {
        "schema_version": "lightguard.v09-candidate-config.v1",
        "calibration_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "episode_manifest_sha256": payload["episode_manifest_sha256"],
        "confirmatory_seen": False,
        "weather_weight": 0.0,
        "load_imputation": "none",
        "threshold_grid": list(THRESHOLDS),
        "selection_gates": {"recall_min": .70, "fpr_max": .05, "hard_negative_fpr_max": .05,
                            "worst_cell_recall_min": .55, "average_precision_min": .90, "abstention_rate_max": .10},
        "architecture_best": {name: {"config": value[1], "metrics": value[2]} for name, value in best.items()},
        "selected_candidate": selected[0] if selected else None,
        "selected_config": selected[1][1] if selected else None,
        "post_confirmatory_retuning_permitted": False,
    }
    config_path = DATA / "v09_candidate_config.json"
    config_path.write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    fields = ["architecture", "stage_a_threshold", "specificity_threshold", "weather_weight", "availability_floor",
              "recall", "fpr", "hard_negative_fpr", "average_precision", "worst_cell_recall", "abstention_rate", "feasible", "metrics_json"]
    with REPORT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"calibration_cases": len(cases), "selected_candidate": freeze["selected_candidate"],
                      "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main()
