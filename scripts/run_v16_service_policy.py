#!/usr/bin/env python3
"""Run frozen H1 through unguarded and guarded service-action lanes."""
from datetime import date, datetime, timedelta

from run_v15_ablation import find_segment, graft
from v09_detector import decide
from v10_counterfactual import baseline, feature_case
from v15_common import group_days, load_rows, measured_phases
from v16_common import CLAIM_BOUNDARY, DATA, load_json, require, write_csv, write_json, canonical_sha

FIELDS = ["pair_id", "meter_id", "local_date", "operator", "operator_class", "corpus_role", "expected_phase_count", "measured_phase_count", "policy", "status", "control_h1_action", "injected_h1_action", "control_lane", "injected_lane", "anomaly_dispatch_capture", "benign_dispatch_escalation", "collapsed_non_normal_escalation", "threshold_same", "claim_boundary"]


def evidence(case, name):
    value = case.get(name)
    return None if value is None else float(value)


def p0_lane(action):
    if action == "normal": return "NO_ACTION"
    return "FIELD_INSPECTION_CANDIDATE"


def p1_lane(action, case, expected_phases, measured_count, boundary):
    if measured_count < expected_phases:
        return "DATA_QUALITY_REVIEW"
    if action == "normal": return "NO_ACTION"
    if action == "data_check_required": return "DATA_QUALITY_REVIEW"
    required = [evidence(case, "activation_evidence"), evidence(case, "persistence_evidence")]
    if expected_phases == 3:
        required.append(evidence(case, "phase_evidence"))
    return "FIELD_INSPECTION_CANDIDATE" if all(value is not None and value >= boundary for value in required) else "REMOTE_MONITOR"


def main() -> None:
    freeze = load_json(DATA / "v16_protocol_freeze.json")
    holdout = load_json(DATA / "v16_service_holdout_manifest.json")
    assets = {row["meter_id"]: row for row in load_json(DATA / "v16_asset_scope_registry.json")["eligible_assets"]}
    require(holdout["protocol_freeze_sha256"] == freeze["freeze_sha256"], "BLOCKED_PROTOCOL_DRIFT")
    threshold = freeze["h1_candidate"]["config"]
    boundary = float(freeze["confirmation_boundary"])
    rows_by_meter = load_rows()
    out = []
    for pair in holdout["pairs"]:
        meter = pair["meter_id"]
        day = date.fromisoformat(pair["local_date"])
        meter_rows = rows_by_meter[meter]
        phases = measured_phases(meter_rows)
        history = [row for row in meter_rows if datetime.combine(day - timedelta(days=30), datetime.min.time()) <= row["timestamp"] < datetime.combine(day, datetime.min.time())]
        base = baseline(history, phases)
        target = find_segment(group_days(meter_rows)[day], pair["target_start"], pair["target_rows_sha256"])
        source = target if pair["identity_noop"] else find_segment(history, pair["source_start"], pair["source_rows_sha256"])
        injected = graft(target, source, base, phases, pair["operator"])
        control_case, injected_case = feature_case(target, base, phases), feature_case(injected, base, phases)
        control_h1, injected_h1 = decide(control_case, "H1", threshold), decide(injected_case, "H1", threshold)
        expected = int(assets[meter]["expected_phase_count"])
        for policy in ("P0_COLLAPSED_NON_NORMAL", "P1_GUARDED_LANES"):
            if policy == "P0_COLLAPSED_NON_NORMAL":
                control_lane, injected_lane = p0_lane(control_h1["action"]), p0_lane(injected_h1["action"])
            else:
                control_lane = p1_lane(control_h1["action"], control_case, expected, len(phases), boundary)
                injected_lane = p1_lane(injected_h1["action"], injected_case, expected, len(phases), boundary)
            field = "FIELD_INSPECTION_CANDIDATE"
            out.append({
                "pair_id": pair["pair_id"], "meter_id": meter, "local_date": pair["local_date"], "operator": pair["operator"], "operator_class": pair["operator_class"], "corpus_role": pair["corpus_role"],
                "expected_phase_count": expected, "measured_phase_count": len(phases), "policy": policy, "status": "OK", "control_h1_action": control_h1["action"], "injected_h1_action": injected_h1["action"],
                "control_lane": control_lane, "injected_lane": injected_lane,
                "anomaly_dispatch_capture": pair["operator_class"] == "anomaly" and injected_lane == field and control_lane != field,
                "benign_dispatch_escalation": pair["operator_class"] == "benign" and injected_lane == field and control_lane != field,
                "collapsed_non_normal_escalation": pair["operator_class"] == "benign" and injected_h1["action"] != "normal",
                "threshold_same": True, "claim_boundary": CLAIM_BOUNDARY,
            })
    write_csv(DATA / "v16_service_policy_results.csv", FIELDS, out)
    write_json(DATA / "v16_service_policy_results_manifest.json", {"status": "OUTCOME_GENERATED", "row_count": len(out), "pair_count": len(holdout["pairs"]), "results_sha256": canonical_sha(out), "threshold_same": True, "raw_ami_written": False})


if __name__ == "__main__":
    main()
