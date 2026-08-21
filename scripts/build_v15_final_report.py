#!/usr/bin/env python3
"""Build aggregate-only v0.15 reports from TERRA A outputs and paired artifacts."""
from __future__ import annotations
import csv, json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];D=ROOT/"lightguard_v0_1/data/validation/v15";R=ROOT/"lightguard_v0_1/reports/v15"
def read_csv(path):
    with path.open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def maybe_json(names):
    for name in names:
        p=D/name
        if p.is_file():return json.loads(p.read_text(encoding="utf-8")),p
    return {},None
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest() if path and path.is_file() else "NOT_AVAILABLE"
def main():
    results=read_csv(R/"v15_full_vs_ablation_results.csv");meter=read_csv(R/"v15_meter_level_results.csv");operator=read_csv(R/"v15_operator_level_results.csv");shadow=read_csv(D/"v15_natural_shadow_results.csv")
    holdout,holdout_path=maybe_json(("v15_background_holdout_manifest.json","v15_counterfactual_holdout.json"));holdout_meta={k:v for k,v in holdout.items() if k!="pairs"};registry=json.loads((D/"v15_active_mechanism_registry.json").read_text(encoding="utf-8"));grades=(R/"v15_mechanism_grade.md").read_text(encoding="utf-8")
    active=[x["name"] for x in registry["components"] if x["runtime_available"]]
    synthesis="""# v0.15 external and target-domain synthesis

- v0.13 MAD is frozen `FROZEN_NEGATIVE_NON_EVALUABLE`.
- v0.14 London remains `PRIMARY_BLOCKED_PROVENANCE`; CoDEx-VFD remains `NOT_REPLICATED`; SustDataED2 remains `INCONCLUSIVE`.
- v0.15 can describe paired, target-domain counterfactual mechanism contribution only. It cannot replace, rehabilitate, or erase the external findings.
- Natural shadow is truth-free target-side action density and disagreement only.
"""
    lines=["# LightGuard v0.15 final summary","","## Predecessor freeze",synthesis,"## Active mechanisms",*([f"- {x}" for x in active] or ["- NOT_AVAILABLE"]),"","## Holdout distribution and hash",f"- Manifest: {holdout_path.name if holdout_path else 'NOT_AVAILABLE'}",f"- SHA-256: {digest(holdout_path)}",f"- Frozen metadata: `{json.dumps(holdout_meta, sort_keys=True)}`","","## Operators","- Operator assignment and class are sealed in `v15_pair_results.csv`; all assigned operators are reported below through paired strata.","","## Full versus Z1","| Endpoint | RD Full-Z1 | Status |","|---|---:|---|"]
    for x in results:
        if x["variant"]=="Z1":lines.append(f"| {x['endpoint']} | {x['paired_rd_full_minus_comparator']} | {x['analysis_status']} |")
    lines += ["","## Ablation","| Endpoint | Variant | RD | Holm p | Status |","|---|---|---:|---:|---|"]
    for x in results:
        if x["variant"]!="Z1":lines.append(f"| {x['endpoint']} | {x['variant']} | {x['paired_rd_full_minus_comparator']} | {x['p_holm']} | {x['analysis_status']} |")
    lines += ["","## Meter stability",f"- Rows reported: {len(meter)}","","## Operator stability",f"- Rows reported: {len(operator)}","","## Mechanism grade",grades,"## Natural shadow",f"- Truth-free target-side density rows: {len(shadow)}","","## Canonical six","- Canonical cases remain references, not target truth; see `v15_case_evidence_matrix.csv`.","","## Interpretation route","- Use paired counterfactual results for target-domain mechanism contribution, then route candidate actions to human review. Do not infer a confirmed fault or field rate.","","## Human review","- Inspect evidence, AMI completeness, source/target lineage, and operational context before maintenance action.","","## Claim boundary","- No field-fault accuracy, fault recall, real-background FPR, field specificity, or fault probability claim is permitted."]
    (R/"v15_external_target_synthesis.md").write_text(synthesis,encoding="utf-8");(R/"v15_final_summary.md").write_text("\n".join(lines)+"\n",encoding="utf-8");print("v0.15 final reports built")
if __name__=="__main__":main()
