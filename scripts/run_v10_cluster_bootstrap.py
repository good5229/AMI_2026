#!/usr/bin/env python3
"""Meter-day clustered uncertainty for frozen H1 transport pairs."""

import csv
import random
import statistics
from collections import defaultdict

from v10_ami import ROOT

INPUT = ROOT / "lightguard_v0_1/data/validation/v10/v10_transport_pairs.csv"
OUTPUT = ROOT / "lightguard_v0_1/reports/v10/v10_cluster_bootstrap.md"
SEED, REPLICATES = 20261020, 2000

with INPUT.open(encoding="utf-8", newline="") as handle: rows = list(csv.DictReader(handle))
for row in rows:
    for key in ("informative", "recovered", "escalated"): row[key] = row[key].lower() == "true"
    row["delta_score"] = float(row["delta_score"])

def stats(sample):
    anomaly = [row for row in sample if row["class"] == "anomaly" and row["informative"]]
    benign = [row for row in sample if row["class"] == "benign"]
    return (sum(row["recovered"] for row in anomaly) / len(anomaly) if anomaly else None,
            sum(row["escalated"] for row in benign) / len(benign) if benign else None,
            statistics.median(row["delta_score"] for row in sample) if sample else None)

def interval(values):
    values = sorted(value for value in values if value is not None)
    return (values[int(.025 * (len(values)-1))], values[int(.975 * (len(values)-1))])

rng = random.Random(SEED); draws = []
for _ in range(REPLICATES): draws.append(stats([rng.choice(rows) for _ in rows]))
point = stats(rows)
loo = {}
for meter in sorted({row["meter_id"] for row in rows}): loo[meter] = stats([row for row in rows if row["meter_id"] != meter])
labels = ("IRR", "Benign escalation", "Median score uplift")
lines = ["# LightGuard v0.10 Meter-Day Cluster Bootstrap", "", f"- seed: `{SEED}`", f"- replicates: `{REPLICATES}`", f"- whole-pair clusters: `{len(rows)}`", "- 15-minute row bootstrap: `prohibited`", "", "| metric | point | percentile 95% |", "|---|---:|---:|"]
for index, label in enumerate(labels):
    ci = interval([draw[index] for draw in draws]); lines.append(f"| {label} | {point[index]:.8f} | [{ci[0]:.8f}, {ci[1]:.8f}] |")
lines.extend(["", "## Leave-one-meter-out", "", "| omitted meter | IRR | benign escalation | median uplift |", "|---|---:|---:|---:|"])
for meter, value in loo.items(): lines.append(f"| {meter} | {value[0]:.8f} | {value[1]:.8f} | {value[2]:.8f} |")
lines.extend(["", "Intervals describe the frozen semi-synthetic paired sample; they do not establish field-fault uncertainty."])
OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print({"clusters": len(rows), "replicates": REPLICATES, "irr_ci": interval([draw[0] for draw in draws])})
