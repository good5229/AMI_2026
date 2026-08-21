#!/usr/bin/env python3
"""Frozen candidate equations and metrics for LightGuard v0.9."""

from __future__ import annotations

import math
from collections import defaultdict

THRESHOLDS = (0.525, 0.55, 0.575, 0.60)
WEIGHTS = {"solar": 0.30, "persistence": 0.25, "load": 0.20, "phase": 0.15, "policy": 0.10}
WEATHER_WEIGHT = 0.0


def clip(value: float) -> float:
    return max(0.0, min(1.0, value))


def wilson(successes: int, total: int) -> list[float]:
    if total == 0:
        return [0.0, 1.0]
    z = 1.959963984540054
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    radius = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return [round(max(0.0, centre - radius), 8), round(min(1.0, centre + radius), 8)]


def average_precision(labels: list[int], scores: list[float]) -> float:
    positives = sum(labels)
    if not positives:
        return 0.0
    ranked = sorted(zip(scores, labels), key=lambda pair: (-pair[0], -pair[1]))
    found = 0
    total = 0.0
    for rank, (_, label) in enumerate(ranked, start=1):
        if label:
            found += 1
            total += found / rank
    return total / positives


def stage_a(case: dict) -> float:
    activation = float(case["activation_evidence"])
    duration = min(float(case["continuous_on_minutes"]) / 90.0, 1.0)
    score = 0.60 * activation + 0.25 * duration + 0.60 * activation * duration
    if case.get("load_mismatch") is not None:
        score += 0.35 * float(case["load_mismatch"])
    if case.get("phase_selectivity") is not None:
        score += 0.30 * float(case["phase_selectivity"])
    if case.get("near_solar_boundary"):
        score -= 0.20
    if case.get("transient"):
        score -= 0.20
    if case.get("normal_partial_policy"):
        score -= 0.20
    return clip(score)


def evidence(case: dict, availability_aware: bool) -> dict:
    values = {
        "solar": case.get("solar_evidence"),
        "persistence": case.get("persistence_evidence"),
        "load": case.get("load_evidence"),
        "phase": case.get("phase_evidence"),
        "policy": case.get("policy_evidence"),
    }
    available = {name: value is not None for name, value in values.items()}
    available_weight = sum(WEIGHTS[name] for name, present in available.items() if present)
    if availability_aware:
        positive = sum(WEIGHTS[name] * float(values[name]) for name in WEIGHTS if available[name])
        positive = positive / available_weight if available_weight else 0.0
    else:
        positive = sum(WEIGHTS[name] * float(values[name]) for name in WEIGHTS if available[name])
    contradiction = max(float(case.get(name, 0.0)) for name in (
        "boundary_conflict", "transient_conflict", "policy_conflict", "load_phase_conflict"
    ))
    return {
        "score": clip(positive - 0.20 * contradiction),
        "availability": available_weight,
        "available_families": sum(available.values()),
        "required_available": available["solar"] and available["persistence"],
        "contradiction": contradiction,
        "components": values,
    }


def decide(case: dict, architecture: str, config: dict) -> dict:
    a_score = stage_a(case)
    t_a = float(config["stage_a_threshold"])
    t_b = float(config.get("specificity_threshold", 0.0))
    reasons = []
    if a_score < t_a:
        reasons.append("STAGE_A_BELOW_THRESHOLD")
    if case.get("near_solar_boundary"):
        reasons.append("SOLAR_BOUNDARY")
    if case.get("normal_partial_policy"):
        reasons.append("ALLOWED_PARTIAL")
    if case.get("load_evidence") is None:
        reasons.append("LOAD_UNAVAILABLE")
    if case.get("phase_evidence") is None:
        reasons.append("PHASE_UNAVAILABLE")
    if case.get("transient"):
        reasons.append("INSUFFICIENT_PERSISTENCE")

    if architecture == "threshold_only":
        decision = "anomaly" if a_score >= t_a else "normal"
        return {"decision": decision, "action": "inspect" if decision == "anomaly" else "normal", "score": a_score,
                "stage_a_score": a_score, "specificity_score": None, "queue_score": None, "reason_codes": reasons}

    availability_aware = architecture in {"H2", "H3"}
    gate = evidence(case, availability_aware)
    if gate["contradiction"] >= 0.75:
        reasons.append("CONTRADICTORY_EVIDENCE")
    if gate["available_families"] < 2:
        reasons.append("INSUFFICIENT_INDEPENDENT_EVIDENCE")
    stage_a_pass = a_score >= t_a
    gate_pass = gate["score"] >= t_b and gate["available_families"] >= 2
    allowed = bool(case.get("normal_partial_policy"))
    high_conflict = gate["contradiction"] >= 0.75

    if availability_aware and (not gate["required_available"] or gate["availability"] < 0.60):
        action = "abstain"
        decision = "abstain"
    elif stage_a_pass and gate_pass and not allowed and not high_conflict:
        action = "inspect"
        decision = "anomaly"
    elif stage_a_pass and (case.get("load_evidence") is None and case.get("phase_evidence") is None):
        action = "data_check_required"
        decision = "normal"
    elif stage_a_pass:
        action = "observe"
        decision = "normal"
    else:
        action = "normal"
        decision = "normal"

    completeness = gate["availability"]
    queue_score = None
    if architecture == "H3" and action in {"inspect", "data_check_required"}:
        queue_score = clip(
            0.40 * gate["score"]
            + 0.20 * float(case["recurrence"])
            + 0.15 * float(case["asset_criticality"])
            + 0.15 * float(case["age_since_last_review"])
            + 0.10 * completeness
        )
    score = clip(a_score * gate["score"])
    return {"decision": decision, "action": action, "score": score, "stage_a_score": a_score,
            "specificity_score": gate["score"], "queue_score": queue_score, "reason_codes": sorted(set(reasons)),
            "availability_score": gate["availability"], "contradiction_score": gate["contradiction"],
            "components": gate["components"]}


def metrics(cases: list[dict], outcomes: list[dict]) -> dict:
    rows = [{**case, **outcome} for case, outcome in zip(cases, outcomes)]
    abnormal = [row for row in rows if row["label"] == "abnormal"]
    normal = [row for row in rows if row["label"] == "normal"]
    hard = [row for row in normal if row["hard_negative"]]
    tp = sum(row["decision"] == "anomaly" for row in abnormal)
    fp = sum(row["decision"] == "anomaly" for row in normal)
    hard_fp = sum(row["decision"] == "anomaly" for row in hard)
    abstain = sum(row["decision"] == "abstain" for row in rows)
    by_cell: dict[str, list[dict]] = defaultdict(list)
    by_type: dict[str, list[dict]] = defaultdict(list)
    for row in abnormal:
        by_cell[row["cell_id"]].append(row)
        by_type[row["scenario_type"]].append(row)
    cell_recall = {key: sum(row["decision"] == "anomaly" for row in values) / len(values) for key, values in sorted(by_cell.items())}
    type_recall = {key: sum(row["decision"] == "anomaly" for row in values) / len(values) for key, values in sorted(by_type.items())}
    labels = [int(row["label"] == "abnormal") for row in rows]
    scores = [float(row["score"]) for row in rows]
    return {
        "recall": round(tp / len(abnormal), 8),
        "fpr": round(fp / len(normal), 8),
        "hard_negative_fpr": round(hard_fp / len(hard), 8),
        "average_precision": round(average_precision(labels, scores), 8),
        "worst_cell_recall": round(min(cell_recall.values()), 8),
        "abstention_rate": round(abstain / len(rows), 8),
        "recall_wilson_95": wilson(tp, len(abnormal)),
        "fpr_wilson_95": wilson(fp, len(normal)),
        "hard_negative_fpr_wilson_95": wilson(hard_fp, len(hard)),
        "per_cell_recall": cell_recall,
        "per_type_recall": type_recall,
        "counts": {"tp": tp, "fp": fp, "hard_fp": hard_fp, "abnormal": len(abnormal), "normal": len(normal), "hard_normal": len(hard), "abstain": abstain},
    }
