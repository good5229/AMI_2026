#!/usr/bin/env python3
"""Execute only after all v0.15 freeze/config artifacts exist; writes aggregate pair results."""
from __future__ import annotations

import statistics
from datetime import date, datetime, timedelta

from v09_detector import decide
from v10_counterfactual import activation, baseline, feature_case
from v15_common import CLAIM_BOUNDARY, DATA, HOLDOUT_MANIFEST, INJECTION_MANIFEST, PREDECESSOR_FREEZE, RESULT_FIELDS, VARIANT_FIELDS, canonical_json_sha, group_days, load_json, load_rows, measured_phases, require, severity, write_csv, write_json


def contiguous(rows, length):
    return [rows[index:index + length] for index in range(len(rows) - length + 1) if all(right["timestamp"] - left["timestamp"] == timedelta(minutes=15) for left, right in zip(rows[index:index + length], rows[index + 1:index + length]))]


def find_segment(rows, start, expected_hash):
    for length in range(2, 17):
        for segment in contiguous(rows, length):
            if segment[0]["timestamp"].isoformat(sep=" ") == start and canonical_json_sha([row["row_sha256"] for row in segment]) == expected_hash: return segment
    raise RuntimeError("BLOCKED_FROZEN_SEGMENT_NOT_FOUND")


def graft(target, source, base, phases, operator):
    injected = [{**row, "currents": dict(row["currents"])} for row in target]
    selected = list(phases)
    if operator == "OP5": selected = [phases[int(canonical_json_sha([target[0]["meter_id"], target[0]["timestamp"].isoformat()]), 16) % len(phases)]]
    if operator == "B4": return injected
    for index, row in enumerate(injected):
        for phase in selected:
            residual = max(0.0, source[index]["currents"][phase] - base["phase"][phase]["off"])
            row["currents"][phase] += residual
    return injected


def ablate(case, variant):
    item = dict(case)
    if variant == "A1": item["persistence_evidence"] = None
    if variant == "A2": item["phase_evidence"] = None; item["phase_selectivity"] = None
    if variant == "A5": item["activation_evidence"] = 0.0
    return item


def robust_z(rows, history, phases, threshold):
    medians, scales = {}, {}
    for phase in phases:
        values = [row["currents"][phase] for row in history if row["currents"][phase] is not None]
        medians[phase] = statistics.median(values)
        mad = statistics.median(abs(value - medians[phase]) for value in values)
        scales[phase] = max(1.4826 * mad, 1e-9)
    score = max(abs(row["currents"][phase] - medians[phase]) / scales[phase] for row in rows for phase in phases if row["currents"][phase] is not None)
    score = min(1.0, score / 8.0)
    return {"action": "inspect" if score >= float(threshold["stage_a_threshold"]) else "normal", "score": score}


def main() -> None:
    freeze, holdout, injection, config = load_json(PREDECESSOR_FREEZE), load_json(HOLDOUT_MANIFEST), load_json(INJECTION_MANIFEST), load_json(DATA / "v15_ablation_configs.json")
    require(config["predecessor_freeze_sha256"] == freeze["freeze_sha256"], "BLOCKED_FREEZE_DRIFT")
    rows_by_meter, results = load_rows(), []
    for pair in holdout["pairs"]:
        meter, day = pair["meter_id"], date.fromisoformat(pair["local_date"])
        meter_rows = rows_by_meter[meter]; phases = measured_phases(meter_rows)
        history = [row for row in meter_rows if datetime.combine(day - timedelta(days=30), datetime.min.time()) <= row["timestamp"] < datetime.combine(day, datetime.min.time())]
        base = baseline(history, phases); day_rows = group_days(meter_rows)[day]
        target = find_segment(day_rows, pair["target_start"], pair["target_rows_sha256"])
        source = target if pair["identity_noop"] else find_segment(history, pair["source_start"], pair["source_rows_sha256"])
        require(pair["identity_noop"] or not ({row["timestamp"] for row in target} & {row["timestamp"] for row in source}), "BLOCKED_SOURCE_TARGET_OVERLAP")
        injected = graft(target, source, base, phases, pair["operator"])
        control_case, injected_case = feature_case(target, base, phases), feature_case(injected, base, phases)
        for variant in VARIANT_FIELDS:
            spec = config["variants"][variant]
            status = "OK"; comparable = True
            if variant == "A1" and control_case.get("persistence_evidence") is None: status, comparable = "NOT_EVALUABLE_INACTIVE_MECHANISM", False
            if variant == "A2" and len(phases) != 3: status, comparable = "NOT_EVALUABLE_PHASE_GATE", False
            if variant == "A5" and not pair.get("baseline_gate", True): status, comparable = "NOT_EVALUABLE_INACTIVE_MECHANISM", False
            if status != "OK": control = injected_out = {"action": "", "score": ""}
            elif variant == "Z1": control, injected_out = robust_z(target, history, phases, spec["threshold"]), robust_z(injected, history, phases, spec["threshold"])
            else:
                architecture = spec["runtime"]
                control = decide(ablate(control_case, variant), architecture, spec["threshold"])
                injected_out = decide(ablate(injected_case, variant), architecture, spec["threshold"])
                comparable = architecture == "H1" or variant in {"A3", "A4", "Z1"}
            results.append({"pair_id": pair["pair_id"], "meter_id": meter, "local_date": day.isoformat(), "operator": pair["operator"], "operator_class": pair["operator_class"], "variant": variant, "status": status, "control_action": control["action"], "injected_action": injected_out["action"], "control_score": control["score"], "injected_score": injected_out["score"], "recovered": status == "OK" and severity(injected_out["action"]) > severity(control["action"]), "benign_escalated": status == "OK" and pair["operator_class"] == "benign" and severity(injected_out["action"]) > 0, "threshold_same": True, "action_scale_comparable": comparable, "source_start": pair["source_start"], "target_start": pair["target_start"], "claim_boundary": CLAIM_BOUNDARY})
    write_csv(DATA / "v15_pair_results.csv", RESULT_FIELDS, results)
    write_json(DATA / "v15_pair_results_manifest.json", {"status": "OUTCOME_GENERATED", "pair_result_schema": RESULT_FIELDS, "injection_manifest_sha256": injection["manifest_sha256"], "config_sha256": config["config_sha256"], "pair_count": len(holdout["pairs"]), "row_count": len(results), "results_sha256": canonical_json_sha(results), "raw_values_written": False})


if __name__ == "__main__":
    main()
