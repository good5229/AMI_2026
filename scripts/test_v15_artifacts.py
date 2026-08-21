#!/usr/bin/env python3
"""Fail-closed v0.15 schema, freeze, pairing, claim, and raw-data hygiene contract."""
from __future__ import annotations
import csv, hashlib, json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];D=ROOT/"lightguard_v0_1/data/validation/v15";R=ROOT/"lightguard_v0_1/reports/v15"
def need(x,msg):
    if not x:raise SystemExit(f"v0.15 artifact contract: {msg}")
def read(path):
    need(path.is_file(),f"missing {path.relative_to(ROOT)}")
    with path.open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def manifest():
    for name in ("v15_background_holdout_manifest.json","v15_counterfactual_holdout.json"):
        p=D/name
        if p.is_file():return json.loads(p.read_text(encoding="utf-8"))
    raise SystemExit("v0.15 artifact contract: missing TERRA A holdout manifest")
def main():
    pair=read(D/"v15_pair_results.csv");required={"pair_id","meter_id","local_date","operator","operator_class","variant","status","control_action","injected_action","control_score","injected_score","recovered","benign_escalated","threshold_same","action_scale_comparable","source_start","target_start","claim_boundary"};need(required.issubset(pair[0]),"actual long schema incomplete")
    m=manifest();need(m.get("v10_overlap_count",m.get("v0_10_overlap_count"))==0,"v0.10 overlap is nonzero");need(m.get("canonical_overlap_count")==0,"canonical overlap is nonzero")
    if "pair_results_sha256" in m:need(sha(D/"v15_pair_results.csv")==m["pair_results_sha256"],"pair result hash mismatch")
    if "deterministic_ids_sha256" in m:need(bool(m["deterministic_ids_sha256"]),"deterministic ID hash absent")
    day_operator={}
    for x in pair:
        key=x["meter_id"],x["local_date"];day_operator.setdefault(key,x["operator"]);need(day_operator[key]==x["operator"],f"one operator/day violated: {key}");need(x["operator"].upper()=="B4" or x["source_start"]!=x["target_start"],f"source/target overlap: {x['pair_id']}")
        if x["operator"].upper()=="B4":need(x["source_start"]==x["target_start"] and x["control_action"]==x["injected_action"] and x["control_score"]==x["injected_score"],"B4 identity exception changed")
    registry=json.loads((D/"v15_active_mechanism_registry.json").read_text(encoding="utf-8"));active={x["component_id"] for x in registry["components"] if x["runtime_available"]};aliases={"A1":"duration_persistence","A2":"native_phase_selectivity","A3":"h1_evidence_gate","A4":"h1_evidence_gate","A5":"baseline_meter_relative_30d"}
    for variant,component in aliases.items():
        if any(x["variant"].upper().startswith(variant) for x in pair):need(component in active,f"inactive ablation present: {variant}")
    full=[x for x in pair if x["variant"].upper() in {"A0","A0_FULL_H1","FULL_H1"}];need(full and all(x["threshold_same"].lower() in {"1","true","yes"} for x in full),"Full H1 threshold contract changed")
    results=read(R/"v15_full_vs_ablation_results.csv")
    need(all(int(x["valid_pairs"]) > 0 for x in results),"paired statistics contain zero valid pairs")
    for endpoint in ("R","B"):need({x["variant"] for x in results if x["endpoint"]==endpoint and x["inference_family"]==endpoint}=={"A1","A2","A3","A4","A5"},f"Holm family {endpoint} incomplete")
    expected=[R/"v15_meter_level_results.csv",R/"v15_operator_level_results.csv",R/"v15_benign_results.csv",R/"v15_mechanism_grade.md",R/"v15_external_target_synthesis.md",R/"v15_final_summary.md",D/"v15_natural_shadow_results.csv",D/"v15_case_evidence_matrix.csv"]
    text="\n".join(p.read_text(encoding="utf-8") for p in expected);final=(R/"v15_final_summary.md").read_text(encoding="utf-8").lower()
    if any(x["endpoint"]=="B" and x["holm_reject"]=="1" and float(x["paired_rd_full_minus_comparator"])>0 for x in results):need("ADVERSE_CONTROLLED_BENIGN_ESCALATION" in text,"adverse benign direction mislabeled")
    need("manifest: not_available" not in final and "frozen metadata: `{}`" not in final,"holdout metadata missing from final report");need("no field-fault accuracy" in final and "real-background fpr" in final and "field specificity" in final and "fault probability claim is permitted" in final,"claim-boundary prohibition missing");need("FROZEN_NEGATIVE_NON_EVALUABLE" in text and "NOT_REPLICATED" in text and "INCONCLUSIVE" in text,"predecessor freeze missing")
    shadow=read(D/"v15_natural_shadow_results.csv");need(not {"truth","recovery","fpr","accuracy"}.intersection(shadow[0]),"natural shadow has forbidden columns")
    tracked=subprocess.run(["git","ls-files","official_docs","data/raw"],cwd=ROOT,text=True,capture_output=True,check=True).stdout;need(not tracked.strip(),"raw AMI tracked")
    print("v0.15 artifact contract PASS")
if __name__=="__main__":main()
