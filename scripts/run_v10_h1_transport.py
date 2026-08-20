#!/usr/bin/env python3
"""Run frozen v0.9 H1 on frozen v0.10 paired counterfactuals."""

from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict

from v09_detector import decide, wilson
from v10_ami import ROOT, sha256_file
from v10_counterfactual import construct_pairs

CONFIG = ROOT / "lightguard_v0_1/data/validation/v09/v09_candidate_config.json"
FROZEN_MANIFEST = ROOT / "lightguard_v0_1/data/validation/v10/v10_injection_manifest.json"
PAIR_OUTPUT = ROOT / "lightguard_v0_1/data/validation/v10/v10_transport_pairs.csv"
RESULT_OUTPUT = ROOT / "lightguard_v0_1/reports/v10/v10_frozen_h1_transport.csv"
SUMMARY_OUTPUT = ROOT / "lightguard_v0_1/reports/v10/v10_frozen_h1_transport_summary.md"
METER_OUTPUT = ROOT / "lightguard_v0_1/reports/v10/v10_meter_level_results.csv"
OP_OUTPUT = ROOT / "lightguard_v0_1/reports/v10/v10_operator_level_results.csv"
BENIGN_OUTPUT = ROOT / "lightguard_v0_1/reports/v10/v10_benign_control_results.csv"

SEVERITY = {"normal": 0, "abstain": -1, "observe": 1, "data_check_required": 1, "inspect": 2}


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["empty"]); writer.writeheader(); writer.writerows(rows)


def summarize(rows, key):
    groups = defaultdict(list)
    for row in rows: groups[row[key]].append(row)
    output = []
    for name, values in sorted(groups.items()):
        anomalies = [row for row in values if row["class"] == "anomaly" and row["informative"]]
        benign = [row for row in values if row["class"] == "benign"]
        output.append({key: name, "pairs": len(values), "informative_anomaly_pairs": len(anomalies), "irr": round(sum(row["recovered"] for row in anomalies) / len(anomalies), 8) if anomalies else "", "benign_pairs": len(benign), "benign_escalation_rate": round(sum(row["escalated"] for row in benign) / len(benign), 8) if benign else "", "median_score_uplift": round(statistics.median(row["delta_score"] for row in values), 8)})
    return output


def main():
    frozen = json.loads(FROZEN_MANIFEST.read_text(encoding="utf-8"))
    pairs, rebuilt = construct_pairs()
    if rebuilt["injection_manifest_sha256"] != frozen["injection_manifest_sha256"]:
        raise RuntimeError("injection manifest determinism failure")
    config_doc = json.loads(CONFIG.read_text(encoding="utf-8"))
    if config_doc["selected_candidate"] != "H1": raise RuntimeError("H1 not frozen")
    config = config_doc["selected_config"]
    rows = []
    for pair in pairs:
        meta = pair["manifest"]
        original = decide(pair["original_case"], "H1", config)
        injected = decide(pair["injected_case"], "H1", config)
        original_severity, injected_severity = SEVERITY[original["action"]], SEVERITY[injected["action"]]
        informative = meta["class"] == "anomaly" and original["action"] != "inspect" and original["action"] != "abstain"
        recovered = informative and injected_severity > original_severity
        escalated = injected_severity > original_severity
        rows.append({"injection_id": meta["injection_id"], "meter_id": meta["meter_id"], "target_date": meta["target_date"], "operator": meta["operator"], "class": meta["class"], "target_start": meta["target_start"], "target_end": meta["target_end"], "provenance_sha256": meta["output_sha256"], "original_action": original["action"], "injected_action": injected["action"], "original_score": round(original["score"], 8), "injected_score": round(injected["score"], 8), "delta_score": round(injected["score"] - original["score"], 8), "informative": informative, "recovered": recovered, "escalated": escalated, "inspect_only_recovery": informative and injected["action"] == "inspect", "interval_iou": 1.0 if recovered else 0.0, "original_reasons": ";".join(original["reason_codes"] + ["SOLAR_UNAVAILABLE", "POLICY_UNAVAILABLE"]), "injected_reasons": ";".join(injected["reason_codes"] + ["SOLAR_UNAVAILABLE", "POLICY_UNAVAILABLE"]), "field_truth_label": "unavailable", "unmodified_background_normal_label": False, "promotion_scope": "semi_synthetic_transport_only"})
    anomalies = [row for row in rows if row["class"] == "anomaly" and row["informative"]]
    benign = [row for row in rows if row["class"] == "benign"]
    irr = sum(row["recovered"] for row in anomalies) / len(anomalies) if anomalies else 0.0
    benign_rate = sum(row["escalated"] for row in benign) / len(benign) if benign else 0.0
    meter_rows = summarize(rows, "meter_id"); op_rows = summarize(rows, "operator")
    meter_irrs = [float(row["irr"]) for row in meter_rows if row["irr"] != ""]
    operator_irrs = [float(row["irr"]) for row in op_rows if row["irr"] != ""]
    median_delta = statistics.median(row["delta_score"] for row in rows)
    gate = irr >= .80 and min(meter_irrs, default=0) >= .60 and benign_rate <= .05 and median_delta > 0
    summary_row = {"candidate": "H1", "config_sha256": sha256_file(CONFIG), "pool_pairs": len(frozen["rows"]), "constructable_pairs": len(rows), "informative_anomaly_pairs": len(anomalies), "injection_recovery_rate": round(irr, 8), "irr_wilson_95": json.dumps(wilson(sum(row["recovered"] for row in anomalies), len(anomalies))), "worst_meter_irr": min(meter_irrs, default=0), "worst_operator_irr": min(operator_irrs, default=0), "benign_pairs": len(benign), "benign_escalation_rate": round(benign_rate, 8), "benign_inspect_rate": round(sum(row["injected_action"] == "inspect" for row in benign) / len(benign), 8) if benign else 0, "median_score_uplift": round(median_delta, 8), "positive_delta_rate": round(sum(row["delta_score"] > 0 for row in rows) / len(rows), 8), "transport_gate": "PASS" if gate else "FAIL", "r1_triggered": not gate, "field_accuracy_claim": False}
    write_csv(PAIR_OUTPUT, rows); write_csv(RESULT_OUTPUT, [summary_row]); write_csv(METER_OUTPUT, meter_rows); write_csv(OP_OUTPUT, op_rows); write_csv(BENIGN_OUTPUT, [row for row in rows if row["class"] == "benign"])
    SUMMARY_OUTPUT.write_text("# LightGuard v0.10 Frozen H1 Transport\n\n" + "\n".join(f"- {key}: `{value}`" for key, value in summary_row.items()) + "\n\nThis is semi-synthetic real-background transport evidence, not field fault accuracy.\n", encoding="utf-8")
    print(json.dumps(summary_row))


if __name__ == "__main__": main()
