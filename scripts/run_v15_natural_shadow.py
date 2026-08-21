#!/usr/bin/env python3
"""Truth-free original target-side action density and A0 disagreement."""
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];D=ROOT/"lightguard_v0_1/data/validation/v15";IN,OUT=D/"v15_pair_results.csv",D/"v15_natural_shadow_results.csv"
def one(x):return int(x.strip().lower() not in {"","normal"})
def main():
    with IN.open(newline="",encoding="utf-8") as f:rows=list(csv.DictReader(f))
    need={"pair_id","meter_id","local_date","variant","status","control_action"}
    if not rows or not need.issubset(rows[0]):raise SystemExit("v0.15 natural shadow: invalid TERRA A long schema")
    rows=[r for r in rows if r["status"].upper()=="OK"];a0={r["pair_id"]:one(r["control_action"]) for r in rows if r["variant"].upper() in {"A0","A0_FULL_H1","FULL_H1"}}
    groups=defaultdict(list)
    for r in rows:groups[(r["meter_id"],r["variant"])].append(r)
    fields=["meter_id","variant","target_side_days","target_action_density","a0_target_action_disagreement_density","interpretation"];out=[]
    for (meter,variant),g in sorted(groups.items()):out.append({"meter_id":meter,"variant":variant,"target_side_days":str(len({r['local_date'] for r in g})),"target_action_density":f"{sum(one(r['control_action']) for r in g)/len(g):.8f}","a0_target_action_disagreement_density":f"{sum(one(r['control_action'])!=a0.get(r['pair_id'],one(r['control_action'])) for r in g)/len(g):.8f}","interpretation":"TRUTH_FREE_ORIGINAL_TARGET_SIDE_DESCRIPTIVE"})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open("w",newline="",encoding="utf-8") as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    print("v0.15 natural shadow complete")
if __name__=="__main__":main()
