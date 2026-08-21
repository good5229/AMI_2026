#!/usr/bin/env python3
"""Carry v0.13/v0.14 limitations into v0.15 without treating canonical cases as truth."""
from __future__ import annotations
import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];IN=ROOT/"lightguard_v0_1/data/validation/v13/v13_case_evidence_matrix.csv";OUT=ROOT/"lightguard_v0_1/data/validation/v15/v15_case_evidence_matrix.csv"
def main():
    with IN.open(newline="",encoding="utf-8") as f:source=list(csv.DictReader(f))
    fields=["event_id","pattern","v13_external_empirical_grade","v14_external_status","v15_role","field_confirmation","claim_boundary"]
    out=[{"event_id":x["event_id"],"pattern":x["pattern"],"v13_external_empirical_grade":x["external_empirical_grade"],"v14_external_status":"FROZEN_NEGATIVE_OR_INCONCLUSIVE","v15_role":"CANONICAL_REFERENCE_NOT_TARGET_TRUTH","field_confirmation":x["field_confirmation"],"claim_boundary":"NO_FIELD_FAULT_ACCURACY_OR_PROBABILITY"} for x in source]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open("w",newline="",encoding="utf-8") as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    print("v0.15 evidence matrix built")
if __name__=="__main__":main()
