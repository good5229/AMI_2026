#!/usr/bin/env python3
"""Preregistered v0.15 paired analysis for TERRA A's long result schema."""
from __future__ import annotations
import csv, math, random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D, R = ROOT / "lightguard_v0_1/data/validation/v15", ROOT / "lightguard_v0_1/reports/v15"
IN, SEED, B = D / "v15_pair_results.csv", 202615, 10_000
REQ = {"pair_id","meter_id","local_date","operator","operator_class","variant","status","control_action","injected_action","control_score","injected_score","recovered","benign_escalated","threshold_same","action_scale_comparable","source_start","target_start","claim_boundary"}
MAP = {"A0":"A0","A0_FULL_H1":"A0","FULL_H1":"A0","A1":"A1","MINUS_PERSISTENCE":"A1","A2":"A2","MINUS_PHASE_EVIDENCE":"A2","A3":"A3","MINUS_SPECIFICITY_CONTRADICTION_GATE":"A3","A4":"A4","STAGE_A_ONLY":"A4","A5":"A5","MINUS_BASELINE_RELATIVE_EVIDENCE":"A5","Z1":"Z1","Z1_ROBUST_Z":"Z1"}
PRIMARY = ("A1","A2","A3","A4","A5")
def die(x): raise SystemExit(f"v0.15 paired statistics: {x}")
def one(x): return int(x.strip().lower() in {"1","true","yes","inspect","observe","inspect_or_observe","escalated"})
def eligible(x): return x["status"].upper()=="OK" and one(x["threshold_same"]) and one(x["action_scale_comparable"])
def exact(a,b):
    n=a+b
    return 1.0 if not n else min(1.0,2*sum(math.comb(n,k) for k in range(min(a,b)+1))/2**n)
def q(xs,p):
    xs.sort(); position=(len(xs)-1)*p; lo,hi=int(position),math.ceil(position)
    return xs[lo] if lo==hi else xs[lo]+(xs[hi]-xs[lo])*(position-lo)
def cluster_ci(pairs, offset):
    by_meter=defaultdict(list)
    for p in pairs: by_meter[p[0]].append(p)
    meters=sorted(by_meter)
    if len(meters)<3:return "","","INSUFFICIENT_CLUSTER_SUPPORT"
    rng=random.Random(SEED+offset); draws=[]
    for _ in range(B):
        draw=[]
        for meter in (rng.choice(meters) for _ in meters):
            group=by_meter[meter]; draw.extend(rng.choice(group) for _ in group)
        draws.append(sum(a-b for _,a,b in draw)/len(draw))
    return f"{q(draws,.025):.8f}",f"{q(draws,.975):.8f}","OK"
def holm(rows):
    running=0.; keep=True; ordered=sorted(rows,key=lambda x:float(x["p_exact"]))
    for i,row in enumerate(ordered):
        p=float(row["p_exact"]); running=max(running,min(1.,p*(len(ordered)-i))); keep=keep and p<=.05/(len(ordered)-i)
        row["p_holm"]=f"{running:.8f}";row["holm_reject"]=str(int(keep))
def write(path,rows,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def main():
    if not IN.is_file():die("missing v15_pair_results.csv")
    with IN.open(newline="",encoding="utf-8") as f: raw=list(csv.DictReader(f))
    if not raw or not REQ.issubset(raw[0]):die("TERRA A long schema is incomplete")
    table={}
    for row in raw:
        row=dict(row);row["variant"]=MAP.get(row["variant"].strip().upper(),row["variant"].strip().upper());key=(row["pair_id"],row["variant"])
        if key in table:die(f"duplicate pair/variant {key}")
        table[key]=row
    pair_ids=sorted({x[0] for x in table});results=[];meter_rows=[];operator_rows=[];families={"R":[],"B":[]}
    for endpoint,column in (("R","recovered"),("B","benign_escalated")):
        operator_class = "anomaly" if endpoint == "R" else "benign"
        assigned=[p for p in pair_ids if (p,"A0") in table and table[(p,"A0")]["operator_class"].lower() == operator_class]
        for variant in (*PRIMARY,"Z1"):
            pairs=[];excluded=0
            for p in assigned:
                full,comp=table.get((p,"A0")),table.get((p,variant))
                if not full or not comp or not eligible(full) or not eligible(comp):excluded+=1;continue
                pairs.append((full["meter_id"],full["operator"],one(full[column]),one(comp[column])))
            n=len(pairs);n11=sum(a and b for _,_,a,b in pairs);n10=sum(a and not b for _,_,a,b in pairs);n01=sum(not a and b for _,_,a,b in pairs);n00=n-n11-n10-n01
            lo,hi,support=cluster_ci([(m,a,b) for m,_,a,b in pairs],len(results)+1) if n else ("","","INSUFFICIENT_CLUSTER_SUPPORT")
            row={"endpoint":endpoint,"variant":variant,"comparison":f"A0_vs_{variant}","assigned_pairs":str(len(assigned)),"valid_pairs":str(n),"excluded_or_noncomparable_pairs":str(excluded),"coverage":f"{n/len(assigned) if assigned else 0:.8f}","n11":str(n11),"n10":str(n10),"n01":str(n01),"n00":str(n00),"paired_rd_full_minus_comparator":f"{(n10-n01)/n if n else 0:.8f}","p_exact":f"{exact(n10,n01):.8f}","p_holm":"","holm_reject":"","ci95_low":lo,"ci95_high":hi,"cluster_support":support,"analysis_status":"EVALUABLE" if n and n/len(assigned)>=.90 and support=="OK" else "NOT_EVALUABLE_INCOMPLETE_COVERAGE","inference_family":endpoint if variant in PRIMARY else "SECONDARY_UNADJUSTED"}
            results.append(row)
            if variant in PRIMARY:families[endpoint].append(row)
            for field,index,sink in (("meter_id",0,meter_rows),("operator",1,operator_rows)):
                for value in sorted({x[index] for x in pairs}):
                    g=[x for x in pairs if x[index]==value];rd=sum(a-b for _,_,a,b in g)/len(g)
                    sink.append({"endpoint":endpoint,field:value,"variant":variant,"valid_pairs":str(len(g)),"full_event_rate":f"{sum(a for _,_,a,_ in g)/len(g):.8f}","comparator_event_rate":f"{sum(b for _,_,_,b in g)/len(g):.8f}","paired_rd_full_minus_comparator":f"{rd:.8f}","n10":str(sum(a and not b for _,_,a,b in g)),"n01":str(sum(not a and b for _,_,a,b in g)),"stability_status":"ADEQUATE_FOR_DIRECTION" if len(g)>=5 and any(a!=b for _,_,a,b in g) else "INSUFFICIENT_STRATUM"})
    for family in families.values():holm(family)
    fields=list(results[0]);write(R/"v15_full_vs_ablation_results.csv",results,fields)
    shared=["endpoint","variant","valid_pairs","full_event_rate","comparator_event_rate","paired_rd_full_minus_comparator","n10","n01","stability_status"]
    write(R/"v15_meter_level_results.csv",meter_rows,["meter_id",*shared]);write(R/"v15_operator_level_results.csv",operator_rows,["operator",*shared]);write(R/"v15_benign_results.csv",[x for x in results if x["endpoint"]=="B"],fields)
    print("v0.15 paired statistics complete")
if __name__=="__main__":main()
