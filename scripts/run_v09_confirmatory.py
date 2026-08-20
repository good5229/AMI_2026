#!/usr/bin/env python3
"""Evaluate calibration-frozen v0.9 candidates on untouched episode holdout."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from v09_detector import decide, metrics

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v09"
REPORT = ROOT / "lightguard_v0_1/reports/v09/v09_confirmatory_results.csv"


def promoted(result: dict) -> bool:
    return result["recall"] >= .70 and result["fpr"] <= .05 and result["hard_negative_fpr"] <= .05 and result["worst_cell_recall"] >= .55


def main() -> None:
    holdout_path = DATA / "v09_confirmatory_holdout.json"
    config_path = DATA / "v09_candidate_config.json"
    holdout = json.loads(holdout_path.read_text(encoding="utf-8"))
    freeze = json.loads(config_path.read_text(encoding="utf-8"))
    if freeze["confirmatory_seen"] is not False or freeze["post_confirmatory_retuning_permitted"] is not False:
        raise RuntimeError("candidate configuration is not pre-confirmatory frozen")
    if holdout["episode_manifest_sha256"] != freeze["episode_manifest_sha256"]:
        raise RuntimeError("episode manifest mismatch")
    cases = holdout["cases"]
    model_results = {}
    decision_rows = []
    for architecture, frozen in freeze["architecture_best"].items():
        outcomes = [decide(case, architecture, frozen["config"]) for case in cases]
        model_results[architecture] = metrics(cases, outcomes)
        for case, outcome in zip(cases, outcomes):
            decision_rows.append({"architecture": architecture, "case_id": case["case_id"], "episode_id": case["episode_id"],
                                  "label": case["label"], "scenario_type": case["scenario_type"], "decision": outcome["decision"],
                                  "action": outcome["action"], "score": outcome["score"], "stage_a_score": outcome["stage_a_score"],
                                  "specificity_score": outcome.get("specificity_score"), "reason_codes": ";".join(outcome["reason_codes"])})
    calibration_selected = freeze["selected_candidate"]
    selected = calibration_selected if calibration_selected and promoted(model_results[calibration_selected]) else None
    summary = {
        "schema_version": "lightguard.v09-confirmatory-summary.v1",
        "validation_kind": "episode_separated_controlled_confirmatory_holdout",
        "case_count": len(cases), "holdout_sha256": hashlib.sha256(holdout_path.read_bytes()).hexdigest(),
        "candidate_config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "calibration_selected_candidate": calibration_selected,
        "selected_candidate": selected,
        "promotion_passed": selected is not None,
        "model_results": model_results,
        "retuning_after_holdout": False,
        "weather_policy": "context_only", "weather_weight": 0.0, "load_imputation": "none",
        "claim_boundary": "Controlled generated episode-separated holdout only; not field AMI accuracy or fault truth.",
    }
    (DATA / "v09_confirmatory_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    fields = ["architecture", "recall", "fpr", "hard_negative_fpr", "average_precision", "worst_cell_recall", "abstention_rate",
              "recall_wilson_95", "fpr_wilson_95", "hard_negative_fpr_wilson_95", "promotion_passed"]
    with REPORT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
        for name, result in model_results.items():
            writer.writerow({"architecture": name, **{field: result[field] for field in fields[1:-1]},
                             "promotion_passed": name == selected})
    with (DATA / "v09_confirmatory_decisions.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(decision_rows[0])); writer.writeheader(); writer.writerows(decision_rows)
    print(json.dumps({"confirmatory_cases": len(cases), "calibration_selected": calibration_selected, "selected_candidate": selected}))


if __name__ == "__main__":
    main()
