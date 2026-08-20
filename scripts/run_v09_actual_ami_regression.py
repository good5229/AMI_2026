#!/usr/bin/env python3
"""Replay six anonymized AMI candidates through frozen v0.8/v0.9 decisions."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from v09_detector import decide, stage_a

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ROOT / "lightguard_app/assets/data/ami_events.csv"
WINDOWS = ROOT / "lightguard_app/assets/data/ami_event_windows"
CONFIG = ROOT / "lightguard_v0_1/data/validation/v09/v09_candidate_config.json"
OUTPUT = ROOT / "lightguard_v0_1/reports/v09/v09_actual_ami_regression.csv"


def main() -> None:
    freeze = json.loads(CONFIG.read_text(encoding="utf-8"))
    selected = freeze["selected_candidate"]
    if selected is None:
        architecture = "H1"
        config = freeze["architecture_best"][architecture]["config"]
    else:
        architecture = selected
        config = freeze["selected_config"]
    manifest = json.loads((WINDOWS / "replay_manifest.json").read_text(encoding="utf-8"))
    file_by_key = {(row["meter_id"], row["date"]): row["file"] for row in manifest["events"]}
    rows = []
    with EVENTS.open(encoding="utf-8-sig", newline="") as handle:
        for event in csv.DictReader(handle):
            phases = [value for value in event["active_phases"].split(",") if value]
            phase = 1.0 if len(phases) == 1 else .5 if len(phases) == 2 else 0.0
            duration = float(event["estimated_duration_min"])
            persistence = .6 * max(0.0, min(1.0, (duration - 10.0) / 50.0)) + .4 * min(1.0, duration / 60.0)
            case = {
                "activation_evidence": float(event["max_activation"]), "continuous_on_minutes": duration,
                "load_mismatch": None, "phase_selectivity": phase, "near_solar_boundary": False,
                "transient": duration <= 15, "normal_partial_policy": False,
                "solar_evidence": 1.0, "persistence_evidence": persistence, "load_evidence": None,
                "phase_evidence": phase, "policy_evidence": None,
                "boundary_conflict": 0.0, "transient_conflict": 1.0 if duration <= 15 else 0.0,
                "policy_conflict": 0.0, "load_phase_conflict": 0.0,
                "recurrence": 0.0, "asset_criticality": 0.0, "age_since_last_review": 0.0,
            }
            previous_score = stage_a(case)
            previous = "anomaly" if previous_score >= .55 else "normal"
            outcome = decide(case, architecture, config)
            replay_file = file_by_key[(event["meter_id"], event["first_sample"][:10])]
            rows.append({
                "event_id": event["event_id"], "meter_id": event["meter_id"], "event_type": event["event_type"],
                "replay_file": replay_file, "replay_sha256": hashlib.sha256((WINDOWS / replay_file).read_bytes()).hexdigest(),
                "field_truth_label": "unavailable", "promotion_gate_input": "false",
                "previous_model": "v08_C1_regression_reference", "previous_decision": previous,
                "previous_score": f"{previous_score:.8f}", "new_model": architecture,
                "new_decision": outcome["decision"], "new_action": outcome["action"],
                "observe": str(outcome["action"] == "observe").lower(), "abstain": str(outcome["decision"] == "abstain").lower(),
                "new_score": f"{outcome['score']:.8f}", "specificity_score": f"{outcome['specificity_score']:.8f}",
                "reason_codes": ";".join(outcome["reason_codes"]),
                "rated_load_link": "unavailable_no_imputation", "claim_boundary": "technical_replay_not_fault_truth",
            })
    if len(rows) != 6:
        raise AssertionError(f"expected six actual AMI replay events, got {len(rows)}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"events": len(rows), "new_actions": {action: sum(row["new_action"] == action for row in rows) for action in sorted({row["new_action"] for row in rows})}}))


if __name__ == "__main__":
    main()
