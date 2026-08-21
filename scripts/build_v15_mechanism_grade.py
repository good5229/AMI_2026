#!/usr/bin/env python3
"""Conservative v0.15 necessity grading; singleton ablations cannot prove sufficiency."""
from __future__ import annotations
import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];R=ROOT/"lightguard_v0_1/reports/v15";N={"A1":"persistence","A2":"phase evidence","A3":"specificity/contradiction gate","A4":"Stage-A-only structure","A5":"baseline-relative evidence"}
def read(x):
    with (R/x).open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def stable(rows,endpoint,variant,positive):
    x=[r for r in rows if r["endpoint"]==endpoint and r["variant"]==variant and r["stability_status"]=="ADEQUATE_FOR_DIRECTION"]
    return bool(x) and all(float(r["paired_rd_full_minus_comparator"])>0 if positive else float(r["paired_rd_full_minus_comparator"])<0 for r in x)
def grade(row,meter,operator):
    if row["analysis_status"]!="EVALUABLE" or row["cluster_support"]!="OK":return "NOT_EVALUABLE"
    benign=row["endpoint"]=="B";rd=float(row["paired_rd_full_minus_comparator"]);lo=float(row["ci95_low"]);hi=float(row["ci95_high"]);ok=(rd<=-.03 and hi<0) if benign else (rd>=.05 and lo>0)
    direction_stable=stable(meter,row["endpoint"],row["variant"],not benign) and stable(operator,row["endpoint"],row["variant"],not benign)
    if ok and row["holm_reject"]=="1" and direction_stable:return "EMPIRICALLY_NECESSARY"
    adverse=(rd>=.03 and lo>0) if benign else (rd<=-.05 and hi<0)
    adverse_stable=stable(meter,row["endpoint"],row["variant"],benign) and stable(operator,row["endpoint"],row["variant"],benign)
    if adverse and row["holm_reject"]=="1" and adverse_stable:return "ADVERSE_CONTROLLED_BENIGN_ESCALATION" if benign else "ADVERSE_RECOVERY_SIGNAL"
    return "TARGET_DOMAIN_CONTRIBUTORY" if ok else "NO_EVIDENCE_OF_NECESSITY"
def main():
    rows,meter,operator=read("v15_full_vs_ablation_results.csv"),read("v15_meter_level_results.csv"),read("v15_operator_level_results.csv")
    out=["# v0.15 target-domain mechanism grades","","| Component | Endpoint | RD | Holm p | CI | Necessity grade | Sufficiency |","|---|---|---:|---:|---|---|---|"]
    for r in rows:
        if r["variant"] in N:out.append(f"| {N[r['variant']]} | {r['endpoint']} | {r['paired_rd_full_minus_comparator']} | {r['p_holm']} | [{r['ci95_low']}, {r['ci95_high']}] | {grade(r,meter,operator)} | NOT_ASSESSED_BY_SINGLETON_ABLATION |")
    out += ["","EMPIRICALLY_NECESSARY requires Holm, directional clustered CI, and adequate non-contradictory meter/operator strata. These are counterfactual-corpus results only, never field-fault, real-background FPR, accuracy, specificity, or probability claims."]
    (R/"v15_mechanism_grade.md").write_text("\n".join(out)+"\n",encoding="utf-8");print("v0.15 mechanism grades built")
if __name__=="__main__":main()
