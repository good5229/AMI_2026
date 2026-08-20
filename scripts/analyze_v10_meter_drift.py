#!/usr/bin/env python3
"""Summarize meter-month shadow drift and the B-L-12 case without labels."""

import csv
import statistics
from collections import defaultdict
from pathlib import Path

from v10_ami import ROOT

INPUT = ROOT / "lightguard_v0_1/data/validation/v10/v10_shadow_replay.csv"
OUTPUT = ROOT / "lightguard_v0_1/reports/v10/v10_meter_drift.csv"
CASE = ROOT / "lightguard_v0_1/reports/v10/v10_b_l_12_case_study.md"

with INPUT.open(encoding="utf-8", newline="") as handle: rows = list(csv.DictReader(handle))
groups = defaultdict(list)
for row in rows: groups[(row["meter_id"], row["local_date"][:7])].append(row)
out = []
for (meter, month), values in sorted(groups.items()):
    evaluable = [row for row in values if row["state"] == "evaluable"]
    nums = lambda key: [float(row[key]) for row in evaluable if row[key] != ""]
    out.append({"meter_id": meter, "month": month, "observed_days": sum(int(row["source_rows"]) > 0 for row in values), "evaluable_days": len(evaluable), "warmup_or_quality_days": len(values)-len(evaluable), "median_off_baseline_a": round(statistics.median(nums("off_baseline_a")), 6) if nums("off_baseline_a") else "", "median_on_baseline_a": round(statistics.median(nums("on_baseline_a")), 6) if nums("on_baseline_a") else "", "median_activation_separation_a": round(statistics.median(nums("activation_separation_a")), 6) if nums("activation_separation_a") else "", "candidate_count": sum(int(row["candidate_count"]) for row in evaluable), "inspect_count": sum(int(row["inspect_count"]) for row in evaluable), "observe_count": sum(int(row["observe_count"]) for row in evaluable), "mean_data_coverage": round(statistics.mean(float(row["data_coverage"]) for row in values), 8), "interpretation": "descriptive_shadow_behavior_not_fault_rate"})
with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(out[0])); writer.writeheader(); writer.writerows(out)
b12 = [row for row in out if row["meter_id"] == "B-L-12"]
CASE.write_text("# B-L-12 Real-Background Case Study\n\nB-L-12 retains its observed daytime base load and missing rows; neither is normalized to another meter or filled.\n\n| month | off A | on A | separation A | candidates | inspect | observe | coverage |\n|---|---:|---:|---:|---:|---:|---:|---:|\n" + "\n".join(f"| {r['month']} | {r['median_off_baseline_a']} | {r['median_on_baseline_a']} | {r['median_activation_separation_a']} | {r['candidate_count']} | {r['inspect_count']} | {r['observe_count']} | {r['mean_data_coverage']} |" for r in b12) + "\n\nInterpretation is meter-relative shadow behavior, not a fault rate or field accuracy.\n", encoding="utf-8")
print({"meter_month_rows": len(out), "b_l_12_months": len(b12)})
