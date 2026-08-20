#!/usr/bin/env python3
"""Harden v0.5 evidence without retuning the frozen detector."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import random
from collections import defaultdict
from pathlib import Path

from run_v04_validation import metrics, rank_rows, v04_score


ROOT = Path(__file__).resolve().parents[1]
V05_DATA = ROOT / "lightguard_v0_1" / "data" / "validation" / "v05"
V05_REPORTS = ROOT / "lightguard_v0_1" / "reports" / "v05"
V06_DATA = ROOT / "lightguard_v0_1" / "data" / "validation" / "v06"
V06_REPORTS = ROOT / "lightguard_v0_1" / "reports" / "v06"
APP_CONTEXT = ROOT / "lightguard_app" / "assets" / "data" / "context"
SEED = 6062026
BOOTSTRAP_REPLICATES = 2000
FACTORS = ("activation", "duration", "load", "phase")
FROZEN = {
    "activation": .6, "duration": .25, "load": .25, "phase": .2,
    "solar_penalty": .2, "transient_penalty": .2, "policy_penalty": .2,
    "weather": 0.0, "threshold": .55,
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total <= 0:
        raise ValueError("Wilson interval requires a positive denominator")
    point = successes / total
    denominator = 1 + z * z / total
    center = (point + z * z / (2 * total)) / denominator
    radius = z * math.sqrt(point * (1 - point) / total + z * z / (4 * total * total)) / denominator
    return max(0.0, center - radius), min(1.0, center + radius)


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return ordered[low]
    return ordered[low] * (high - position) + ordered[high] * (position - low)


def stationary_sample(series: list[int], rng: random.Random, expected_block: int = 7) -> list[int]:
    if not series:
        return []
    restart_probability = 1 / expected_block
    index = rng.randrange(len(series))
    result = []
    for _ in series:
        result.append(series[index])
        if rng.random() < restart_probability:
            index = rng.randrange(len(series))
        else:
            index = (index + 1) % len(series)
    return result


def uncertainty_rows() -> tuple[list[dict], dict]:
    robustness = read_csv(V05_REPORTS / "robustness_results.csv")
    rows = []
    for item in robustness:
        point = float(item["actual_canonical_event_coverage"])
        successes = round(point * 6)
        lower, upper = wilson(successes, 6)
        rows.append({
            "stress_id": item["stress_id"],
            "candidate_covered": successes,
            "candidate_total": 6,
            "coverage_point": round(point, 6),
            "wilson_95_lower": round(lower, 6),
            "wilson_95_upper": round(upper, 6),
            "interpretation": "known-candidate coverage uncertainty; not field recall",
        })

    causal = read_csv(V05_DATA / "causal_walkforward_results.csv")
    evaluable: dict[str, list[str]] = defaultdict(list)
    candidates = set()
    for row in causal:
        if row["baseline_window"] != "30d":
            continue
        key = (row["meter_id"], row["evaluation_date"])
        if row["status"] == "evaluable":
            evaluable[row["meter_id"]].append(row["evaluation_date"])
        elif row["status"] == "candidate":
            candidates.add(key)
    series_by_meter = {
        meter: [1 if (meter, day) in candidates else 0 for day in sorted(days)]
        for meter, days in sorted(evaluable.items())
    }
    observed = sum(map(sum, series_by_meter.values())) / sum(map(len, series_by_meter.values()))
    rng = random.Random(SEED)
    draws = []
    for _ in range(BOOTSTRAP_REPLICATES):
        sampled = [stationary_sample(series, rng) for series in series_by_meter.values()]
        draws.append(sum(map(sum, sampled)) / sum(map(len, sampled)))
    bootstrap = {
        "method": "stationary bootstrap over ordered daily candidate indicators within meter",
        "seed": SEED,
        "replicates": BOOTSTRAP_REPLICATES,
        "expected_block_days": 7,
        "meter_count": len(series_by_meter),
        "evaluable_meter_days": sum(map(len, series_by_meter.values())),
        "candidate_density_point": round(observed, 8),
        "candidate_density_95_lower": round(percentile(draws, .025), 8),
        "candidate_density_95_upper": round(percentile(draws, .975), 8),
        "claim_scope": "descriptive detector-candidate density; not fault prevalence",
    }
    return rows, bootstrap


def interaction_diagnostics() -> tuple[list[dict], list[dict]]:
    holdout = json.loads((ROOT / "lightguard_v0_1" / "data" / "validation" / "v04_confirmatory_holdout.json").read_text(encoding="utf-8"))
    cases = holdout["cases"]
    design = []
    for signs in itertools.product((-1, 1), repeat=len(FACTORS)):
        weights = dict(FROZEN)
        for factor, sign in zip(FACTORS, signs):
            weights[factor] = FROZEN[factor] * (1 + .10 * sign)
        ranked = rank_rows(cases, lambda case: v04_score(case, weights, False))
        result = metrics(ranked)
        design.append({
            "run_id": len(design) + 1,
            **{f"{factor}_level": sign for factor, sign in zip(FACTORS, signs)},
            **{f"{factor}_weight": weights[factor] for factor in FACTORS},
            "anomaly_recall": result["anomaly_recall"],
            "normal_fpr": result["normal_fpr"],
            "precision_at_20": result["precision_at_20"],
            "candidate_count": result["inspection_candidate_count"],
            "promotion_policy": "diagnostic_only_no_retuning",
        })

    effects = []
    terms = [(factor,) for factor in FACTORS] + list(itertools.combinations(FACTORS, 2))
    for term in terms:
        for metric in ("anomaly_recall", "normal_fpr", "precision_at_20", "candidate_count"):
            positive = []
            negative = []
            for row in design:
                sign = math.prod(row[f"{factor}_level"] for factor in term)
                (positive if sign > 0 else negative).append(float(row[metric]))
            effects.append({
                "term": ":".join(term),
                "order": len(term),
                "metric": metric,
                "effect_high_minus_low": round(sum(positive) / len(positive) - sum(negative) / len(negative), 8),
                "design": "2^4 full factorial at frozen weight x {0.9,1.1}",
                "claim_scope": "interaction diagnostic only; no selection or retuning",
            })
    return design, effects


def main() -> int:
    V06_DATA.mkdir(parents=True, exist_ok=True)
    V06_REPORTS.mkdir(parents=True, exist_ok=True)
    APP_CONTEXT.mkdir(parents=True, exist_ok=True)

    intervals, bootstrap = uncertainty_rows()
    design, effects = interaction_diagnostics()
    write_csv(V06_REPORTS / "coverage_uncertainty.csv", intervals)
    write_json(V06_DATA / "stationary_bootstrap.json", bootstrap)
    write_csv(V06_REPORTS / "factorial_design.csv", design)
    write_csv(V06_REPORTS / "interaction_effects.csv", effects)

    abstention = {
        "schema_version": "lightguard-v0.6-abstention-policy",
        "default": "TECHNICAL_CANDIDATE_ONLY",
        "rules": [
            {"condition": "available_channel_count == 0", "decision": "DATA_INSUFFICIENT", "reason": "no measured current channel"},
            {"condition": "max_contiguous_gap_minutes >= 120", "decision": "DATA_INSUFFICIENT", "reason": "v0.5 stress coverage collapsed to 0/6"},
            {"condition": "duplicate_conflict_count > 0", "decision": "DATA_INSUFFICIENT_AT_CONFLICT", "reason": "conflicting samples cannot be silently selected"},
            {"condition": "sampling_interval_minutes > 60", "decision": "DATA_INSUFFICIENT", "reason": "outside tested resolution envelope"},
            {"condition": "sampling_interval_minutes == 60", "decision": "REDUCED_TEMPORAL_RESOLUTION", "reason": "candidate coverage survived but interval IoU degraded"},
        ],
        "never_do": ["coerce null to zero", "impute an event across an abstained gap", "report abstention as a normal result"],
    }
    write_json(V06_DATA / "abstention_policy.json", abstention)

    field_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://good5229.github.io/AMI_2026/schema/field-outcome-v1.json",
        "title": "LightGuard blinded field inspection outcome",
        "type": "object",
        "required": ["inspection_id", "cabinet_uid", "inspection_started_at", "inspector_blinded_to_score", "outcome", "evidence"],
        "properties": {
            "inspection_id": {"type": "string", "minLength": 1},
            "candidate_event_id": {"type": ["string", "null"]},
            "cabinet_uid": {"type": "string", "minLength": 1},
            "inspection_started_at": {"type": "string", "format": "date-time"},
            "inspector_blinded_to_score": {"const": True},
            "outcome": {"enum": ["confirmed_fault", "normal_operation", "maintenance_related", "unable_to_adjudicate"]},
            "fault_type": {"type": ["string", "null"]},
            "repair_action": {"type": ["string", "null"]},
            "post_repair_verified": {"type": ["boolean", "null"]},
            "evidence": {"type": "array", "minItems": 1, "items": {"type": "string"}},
            "adjudicator": {"type": ["string", "null"]},
            "adjudicated_at": {"type": ["string", "null"], "format": "date-time"},
        },
        "additionalProperties": False,
    }
    write_json(V06_DATA / "field_outcome_schema.json", field_schema)

    largest = max((row for row in effects if row["order"] == 2 and row["metric"] == "normal_fpr"), key=lambda row: abs(row["effect_high_minus_low"]))
    baseline_interval = next(row for row in intervals if row["stress_id"] == "baseline")
    gap_interval = next(row for row in intervals if row["stress_id"] == "gap_120m")
    product = {
        "schema_version": "lightguard-v0.6-evidence-hardening",
        "claim_scope": "uncertainty and data-quality evidence; actual AMI remains unlabeled",
        "known_candidate_coverage": baseline_interval,
        "gap_120m_coverage": gap_interval,
        "candidate_density": bootstrap,
        "interaction_diagnostic": {
            "design_runs": len(design),
            "largest_two_factor_fpr_term": largest["term"],
            "largest_two_factor_fpr_effect": largest["effect_high_minus_low"],
            "frozen_configuration_changed": False,
            "promotion_policy": "diagnostic_only_no_retuning",
        },
        "abstention": {"rule_count": len(abstention["rules"]), "policy": "DATA_INSUFFICIENT is distinct from normal"},
        "field_truth": {"available": False, "schema_ready": True, "blinded_adjudication_required": True},
    }
    write_json(V06_DATA / "v06_evidence_summary.json", product)
    write_json(APP_CONTEXT / "v06_evidence_summary.json", product)

    references = """# v0.6 Academic Basis and Gap Closure Plan

## Applied basis

- Hyndman and Athanasopoulos, time-series cross-validation: training observations must precede each rolling origin. https://otexts.com/fpp3/tscv.html
- Politis and Romano, stationary bootstrap: dependent stationary observations require dependence-preserving resampling for uncertainty. https://doi.org/10.1080/01621459.1994.10476870
- Wilson, score interval: a point estimate such as 6/6 must retain small-sample uncertainty. https://doi.org/10.1080/01621459.1927.10502953
- Kim et al., rigorous TAD evaluation: point-adjustment can overstate anomaly performance, so this project uses event overlap without point-adjusted recall. https://doi.org/10.1609/AAAI.V36I7.20680
- Goswami et al., unlabeled model selection: synthetic injection is a surrogate when labels are scarce, not a substitute for field truth. https://openreview.net/forum?id=gOZ_pKANaPW
- NIST factorial effects: two-factor effects should be measured explicitly rather than inferred from OAT neighbors. https://www.itl.nist.gov/div898/handbook/pri/section5/pri597.htm
- NIST information quality policy: quantitative results should carry uncertainty and reproducibility evidence. https://www.nist.gov/director/nist-information-quality-standards

## Closure decisions

- Candidate coverage receives Wilson 95% intervals and is never renamed recall.
- Daily candidate density receives a deterministic stationary-bootstrap interval with meter-local ordering preserved.
- A 2^4 factorial diagnostic measures main and two-factor effects at frozen weights x 0.9/1.1; no run selects a new configuration.
- Known failure envelopes produce an explicit abstention instead of interpolation or a normal classification.
- Field accuracy remains unavailable until blinded inspections populate the versioned outcome schema.
"""
    (V06_REPORTS / "academic_basis.md").write_text(references, encoding="utf-8")
    protocol = """# Blinded Field Validation Protocol

1. Freeze the detector and candidate list before dispatch assignment.
2. Sample candidate and non-candidate cabinets using a predeclared stratified design; do not let inspectors see scores or candidate rank.
3. Record every visit with `field_outcome_schema.json`, including unable-to-adjudicate outcomes and evidence references.
4. Lock outcomes before joining them to detector results through `candidate_event_id`.
5. Report the sampling frame, exclusions, abstentions, unresolved outcomes, and confidence intervals.
6. Estimate field recall only when the sampled frame contains independently inspected candidate and non-candidate units with a defensible denominator.
7. Keep repair savings, dispatch costs, and ROI separate until same-scope official cost denominators exist.
"""
    (V06_REPORTS / "field_validation_protocol.md").write_text(protocol, encoding="utf-8")

    inputs = [
        V05_DATA / "causal_walkforward_results.csv",
        V05_REPORTS / "robustness_results.csv",
        ROOT / "lightguard_v0_1" / "data" / "validation" / "v04_confirmatory_holdout.json",
    ]
    outputs = [
        V06_REPORTS / "coverage_uncertainty.csv", V06_DATA / "stationary_bootstrap.json",
        V06_REPORTS / "factorial_design.csv", V06_REPORTS / "interaction_effects.csv",
        V06_DATA / "abstention_policy.json", V06_DATA / "field_outcome_schema.json",
        V06_DATA / "v06_evidence_summary.json", APP_CONTEXT / "v06_evidence_summary.json",
        V06_REPORTS / "academic_basis.md", V06_REPORTS / "field_validation_protocol.md",
    ]
    manifest = {
        "schema_version": "lightguard-v0.6-reproducibility",
        "seed": SEED,
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "frozen_config": FROZEN,
        "commands": ["python3 scripts/run_v05_all.py", "python3 scripts/run_v06_evidence_hardening.py", "python3 scripts/test_v06_artifacts.py"],
        "input_hashes": {str(path.relative_to(ROOT)): sha256(path) for path in inputs},
        "output_hashes": {str(path.relative_to(ROOT)): sha256(path) for path in outputs},
    }
    write_json(V06_REPORTS / "reproducibility_manifest.json", manifest)
    print(json.dumps({"wilson_rows": len(intervals), "factorial_runs": len(design), "effects": len(effects), "abstention_rules": len(abstention["rules"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
