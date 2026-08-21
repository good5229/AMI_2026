#!/usr/bin/env python3
"""Shared v0.8 detector scoring and metric utilities.

The module contains no file I/O and does not tune parameters. Callers must keep
calibration and confirmatory data boundaries explicit.
"""

from __future__ import annotations

import math
from collections import defaultdict
from statistics import mean

THRESHOLD = 0.55
BASELINE = {
    "activation_weight": 0.60,
    "duration_weight": 0.25,
    "load_weight": 0.25,
    "phase_weight": 0.20,
    "solar_penalty": 0.20,
    "transient_penalty": 0.20,
    "policy_penalty": 0.20,
    "threshold": THRESHOLD,
}


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _optional(value) -> float | None:
    return None if value is None else float(value)


def frozen_v04(case: dict) -> dict:
    """Apply the frozen v0.4 equation to physical activation inputs."""
    load = _optional(case.get("load_mismatch"))
    phase = _optional(case.get("phase_selectivity"))
    raw = (
        BASELINE["activation_weight"] * float(case["activation_fraction"])
        + BASELINE["duration_weight"] * min(float(case["duration_min"]) / 90.0, 1.0)
        + BASELINE["load_weight"] * (load or 0.0)
        + BASELINE["phase_weight"] * (phase or 0.0)
    )
    if case["near_solar_boundary"]:
        raw -= BASELINE["solar_penalty"]
    if case["transient"]:
        raw -= BASELINE["transient_penalty"]
    if case["normal_partial_policy"]:
        raw -= BASELINE["policy_penalty"]
    value = clamp(raw)
    return {"score": value, "decision": "anomaly" if value >= THRESHOLD else "normal"}


def candidate(case: dict, config: dict, variant: str) -> dict:
    load = _optional(case.get("load_mismatch"))
    phase = _optional(case.get("phase_selectivity"))
    activation = float(case["activation_evidence"])
    duration = min(float(case["duration_min"]) / 90.0, 1.0)
    positive = (
        0.60 * activation
        + 0.25 * duration
        + float(config["interaction_weight"]) * activation * duration
    )
    if load is not None:
        positive += float(config["load_weight"]) * load
    if phase is not None:
        positive += float(config["phase_weight"]) * phase

    if variant in {"C2", "C3"}:
        missing_count = int(load is None) + int(phase is None)
        positive *= 1.0 + float(config.get("availability_boost", 0.0)) * missing_count

    raw = positive
    if case["near_solar_boundary"]:
        raw -= 0.20
    if case["transient"]:
        raw -= 0.20
    if case["normal_partial_policy"]:
        raw -= 0.20
    if variant == "C3" and case.get("weather_available"):
        raw -= float(config.get("weather_weight", 0.0)) * float(case["weather_uncertainty"])

    value = clamp(raw)
    decision = "anomaly" if value >= THRESHOLD else "normal"
    if variant in {"C2", "C3"} and (load is None or phase is None):
        lower = THRESHOLD - float(config.get("abstain_margin", 0.0))
        upper = THRESHOLD + 0.05
        if lower <= value <= upper:
            decision = "abstain"
    return {"score": value, "decision": decision}


def average_precision(labels: list[int], scores: list[float]) -> float:
    positives = sum(labels)
    if positives == 0:
        return 0.0
    ranked = sorted(zip(scores, labels), key=lambda pair: pair[0], reverse=True)
    true_positive = 0
    total = 0.0
    for rank, (_, label) in enumerate(ranked, start=1):
        if label:
            true_positive += 1
            total += true_positive / rank
    return total / positives


def wilson(successes: int, total: int) -> list[float]:
    if total == 0:
        return [0.0, 1.0]
    z = 1.959963984540054
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    radius = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return [round(max(0.0, centre - radius), 8), round(min(1.0, centre + radius), 8)]


def metrics(cases: list[dict], outcomes: list[dict]) -> dict:
    rows = [{**case, **outcome} for case, outcome in zip(cases, outcomes)]
    anomalies = [row for row in rows if row["label"] == "abnormal"]
    normals = [row for row in rows if row["label"] == "normal"]
    hard_normals = [row for row in normals if row["scenario_type"] != "normal_full_operation"]
    tp = sum(row["decision"] == "anomaly" for row in anomalies)
    fp = sum(row["decision"] == "anomaly" for row in normals)
    hard_fp = sum(row["decision"] == "anomaly" for row in hard_normals)
    abstain = sum(row["decision"] == "abstain" for row in rows)
    evaluable_anomalies = [row for row in anomalies if row["decision"] != "abstain"]
    evaluable_normals = [row for row in normals if row["decision"] != "abstain"]
    recall = tp / len(anomalies)
    fpr = fp / len(normals)
    tnr = 1.0 - fpr
    labels = [int(row["label"] == "abnormal") for row in rows]
    scores = [float(row["score"]) for row in rows]
    by_cell: dict[str, list[dict]] = defaultdict(list)
    by_type: dict[str, list[dict]] = defaultdict(list)
    for row in anomalies:
        by_cell[f"{row['region_id']}_{row['season']}"] .append(row)
        by_type[row["scenario_type"]].append(row)
    cell_recall = {
        key: sum(row["decision"] == "anomaly" for row in values) / len(values)
        for key, values in sorted(by_cell.items())
    }
    type_recall = {
        key: sum(row["decision"] == "anomaly" for row in values) / len(values)
        for key, values in sorted(by_type.items())
    }
    weak = [row for row in anomalies if row["severity"] == "weak"]
    return {
        "recall": round(recall, 8),
        "fpr": round(fpr, 8),
        "hard_negative_fpr": round(hard_fp / len(hard_normals), 8),
        "precision": round(tp / (tp + fp), 8) if tp + fp else 0.0,
        "average_precision": round(average_precision(labels, scores), 8),
        "balanced_accuracy": round((recall + tnr) / 2.0, 8),
        "weak_recall": round(sum(row["decision"] == "anomaly" for row in weak) / len(weak), 8),
        "worst_cell_recall": round(min(cell_recall.values()), 8),
        "cell_recall_variance": round(mean((value - mean(cell_recall.values())) ** 2 for value in cell_recall.values()), 8),
        "abstention_rate": round(abstain / len(rows), 8),
        "recall_evaluable": round(sum(row["decision"] == "anomaly" for row in evaluable_anomalies) / len(evaluable_anomalies), 8) if evaluable_anomalies else 0.0,
        "fpr_evaluable": round(sum(row["decision"] == "anomaly" for row in evaluable_normals) / len(evaluable_normals), 8) if evaluable_normals else 0.0,
        "recall_wilson_95": wilson(tp, len(anomalies)),
        "fpr_wilson_95": wilson(fp, len(normals)),
        "per_type_recall": type_recall,
        "per_cell_recall": cell_recall,
        "counts": {"tp": tp, "fp": fp, "anomalies": len(anomalies), "normals": len(normals), "abstain": abstain},
    }
