#!/usr/bin/env python3
"""Paired feature-removal experiment for the frozen C2 candidate."""

from __future__ import annotations

import copy
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from v08_detector import candidate  # noqa: E402

HOLDOUT = ROOT / "lightguard_v0_1/data/validation/v08/v08_confirmatory_holdout.json"
FREEZE = ROOT / "lightguard_v0_1/data/validation/v08/v08_candidate_freeze.json"
CASES_OUT = ROOT / "lightguard_v0_1/data/validation/v08/v08_feature_availability_cases.json"
RESULTS_OUT = ROOT / "lightguard_v0_1/reports/v08/v08_feature_availability_results.csv"
STATES = ("as_observed", "load_unavailable", "weather_unavailable", "phase_unavailable")


def remove_feature(source: dict, state: str) -> dict:
    case = copy.deepcopy(source)
    if state == "load_unavailable":
        case["load_mismatch"] = None
        case["rated_load_w"] = None
        case["rated_load_status"] = "unavailable_no_imputation"
    elif state == "weather_unavailable":
        case["weather_available"] = False
        case["official_weather_context"] = None
    elif state == "phase_unavailable":
        case["phase_selectivity"] = None
    return case


def completeness(case: dict) -> float:
    available = sum((case.get("load_mismatch") is not None, case.get("phase_selectivity") is not None, bool(case.get("weather_available"))))
    return available / 3.0


def main() -> None:
    source_cases = json.loads(HOLDOUT.read_text(encoding="utf-8"))["cases"]
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    config = freeze["models"]["C2"]["config"]
    experiment_cases = []
    result_rows = []
    for source in source_cases:
        base_outcome = candidate(source, config, "C2")
        for state in STATES:
            case = remove_feature(source, state)
            outcome = candidate(case, config, "C2")
            experiment_cases.append({
                "availability_case_id": f"{source['case_id']}::{state}",
                "base_case_id": source["case_id"],
                "state": state,
                "region_id": source["region_id"],
                "season": source["season"],
                "label": source["label"],
                "scenario_type": source["scenario_type"],
                "load_available": case.get("load_mismatch") is not None,
                "phase_available": case.get("phase_selectivity") is not None,
                "weather_available": bool(case.get("weather_available")),
                "evidence_completeness": completeness(case),
                "imputation": "none",
                "source": "paired_feature_removal_controlled_not_actual_ami",
            })
            result_rows.append({
                "base_case_id": source["case_id"],
                "state": state,
                "region_id": source["region_id"],
                "season": source["season"],
                "label": source["label"],
                "scenario_type": source["scenario_type"],
                "score": f"{outcome['score']:.8f}",
                "decision": outcome["decision"],
                "abstained": str(outcome["decision"] == "abstain").lower(),
                "score_delta_vs_observed": f"{outcome['score'] - base_outcome['score']:.8f}",
                "decision_changed": str(outcome["decision"] != base_outcome["decision"]).lower(),
                "evidence_completeness": f"{completeness(case):.8f}",
                "imputation": "none",
            })
    payload = {
        "schema_version": "lightguard.v08-feature-availability.v1",
        "experiment_kind": "paired_feature_removal_only",
        "base_case_count": len(source_cases),
        "case_count": len(experiment_cases),
        "states": list(STATES),
        "load_values_added": False,
        "actual_ami": False,
        "cases": experiment_cases,
    }
    CASES_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    RESULTS_OUT.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result_rows[0]))
        writer.writeheader()
        writer.writerows(result_rows)
    changes = sum(row["decision_changed"] == "true" for row in result_rows if row["state"] != "as_observed")
    abstentions = sum(row["abstained"] == "true" for row in result_rows)
    print(json.dumps({"base_cases": len(source_cases), "paired_cases": len(experiment_cases), "decision_changes": changes, "abstentions": abstentions, "imputation": "none"}))


if __name__ == "__main__":
    main()
