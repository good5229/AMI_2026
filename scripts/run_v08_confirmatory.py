#!/usr/bin/env python3
"""Run frozen v0.8 candidates on the independent confirmatory holdout."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_v08_calibration import materialize  # noqa: E402
from v08_detector import candidate, frozen_v04, metrics  # noqa: E402

DESIGN = ROOT / "lightguard_v0_1/data/validation/v08_design_matrix.csv"
CONTEXT = ROOT / "lightguard_v0_1/data/validation/v07/regional_seasonal_context_2025.json"
FREEZE = ROOT / "lightguard_v0_1/data/validation/v08/v08_candidate_freeze.json"
HOLDOUT = ROOT / "lightguard_v0_1/data/validation/v08/v08_confirmatory_holdout.json"
SUMMARY = ROOT / "lightguard_v0_1/data/validation/v08/v08_confirmatory_summary.json"
RESULTS = ROOT / "lightguard_v0_1/reports/v08/v08_confirmatory_results.csv"
UNCERTAINTY = ROOT / "lightguard_v0_1/reports/v08/v08_uncertainty_summary.md"
WEATHER = ROOT / "lightguard_v0_1/reports/v08/v08_weather_candidate_decision.md"
DESIGN_SHA = "9fba439a9bd22d184e6a705af559a9b43a39fb4b9498cfa3d3a50c2f5853dbb0"
CANDIDATE_FREEZE_SHA = "12fdb827f3b3d553707b616425bbc9721405df7623d40c79a87169589eed2b35"
BOOTSTRAP_SEED = 20260820
BOOTSTRAP_RESAMPLES = 1000


def canonical_json(payload) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_holdout_design() -> list[dict]:
    if sha256(DESIGN) != DESIGN_SHA:
        raise ValueError("v0.8 design freeze mismatch")
    if sha256(FREEZE) != CANDIDATE_FREEZE_SHA:
        raise ValueError("candidate parameter freeze mismatch")
    with DESIGN.open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row["split"] == "confirmatory"]
    if len(rows) != 432 or any(row["split"] != "confirmatory" for row in rows):
        raise ValueError("Confirmatory boundary failure")
    return rows


def outcomes(cases: list[dict], model: str, config: dict) -> list[dict]:
    if model == "frozen_v04":
        return [frozen_v04(case) for case in cases]
    return [candidate(case, config, model) for case in cases]


def precision_at_k(cases: list[dict], values: list[dict], k: int) -> float:
    ranked = sorted(zip(cases, values), key=lambda pair: pair[1]["score"], reverse=True)[:k]
    return round(sum(case["label"] == "abnormal" for case, _ in ranked) / k, 8)


def ndcg_at_k(cases: list[dict], values: list[dict], k: int) -> float:
    ranked = sorted(zip(cases, values), key=lambda pair: pair[1]["score"], reverse=True)[:k]
    dcg = sum((1 if case["label"] == "abnormal" else 0) / math.log2(index + 2) for index, (case, _) in enumerate(ranked))
    positives = min(k, sum(case["label"] == "abnormal" for case in cases))
    ideal = sum(1 / math.log2(index + 2) for index in range(positives))
    return round(dcg / ideal, 8) if ideal else 0.0


def quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def bootstrap(cases: list[dict], configs: dict) -> dict:
    strata: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, case in enumerate(cases):
        strata[(case["cell_id"], case["label"])].append(index)
    rng = random.Random(BOOTSTRAP_SEED)
    deltas = {model: {metric: [] for metric in ("recall", "fpr", "average_precision")} for model in ("C1", "C2", "C3")}
    for _ in range(BOOTSTRAP_RESAMPLES):
        selected = []
        for indices in strata.values():
            selected.extend(rng.choice(indices) for _ in indices)
        sample = [cases[index] for index in selected]
        base = metrics(sample, outcomes(sample, "frozen_v04", {}))
        for model in ("C1", "C2", "C3"):
            result = metrics(sample, outcomes(sample, model, configs[model]))
            for metric in deltas[model]:
                deltas[model][metric].append(result[metric] - base[metric])
    return {
        "method": "cell_and_class_stratified_nonparametric_bootstrap",
        "seed": BOOTSTRAP_SEED,
        "resamples": BOOTSTRAP_RESAMPLES,
        "delta_vs_frozen_v04": {
            model: {
                metric: [round(quantile(values, 0.025), 8), round(quantile(values, 0.975), 8)]
                for metric, values in by_metric.items()
            }
            for model, by_metric in deltas.items()
        },
    }


def candidate_success(base: dict, result: dict) -> bool:
    return (
        result["recall"] > base["recall"]
        and result["fpr"] <= 0.05
        and result["hard_negative_fpr"] <= 0.05
        and result["weak_recall"] > base["weak_recall"]
        and (
            result["worst_cell_recall"] > base["worst_cell_recall"]
            or result["average_precision"] > base["average_precision"]
            or result["abstention_rate"] > 0
        )
    )


def main() -> None:
    design_rows = load_holdout_design()
    context_payload = json.loads(CONTEXT.read_text(encoding="utf-8"))
    context = {cell["cell_id"]: cell for cell in context_payload["cells"]}
    cases = []
    for row in design_rows:
        case = materialize(row, context[f"{row['region_id']}_{row['season']}"])
        case["split"] = "confirmatory"
        case["source"] = "v08_controlled_confirmatory_not_actual_ami"
        cases.append(case)
    holdout_payload = {
        "schema_version": "lightguard.v08-confirmatory.v1",
        "split": "confirmatory",
        "design_sha256": DESIGN_SHA,
        "candidate_freeze_sha256": CANDIDATE_FREEZE_SHA,
        "case_count": len(cases),
        "actual_ami": False,
        "post_result_retuning_permitted": False,
        "cases": cases,
    }
    HOLDOUT.parent.mkdir(parents=True, exist_ok=True)
    HOLDOUT.write_bytes(canonical_json(holdout_payload))
    holdout_sha = sha256(HOLDOUT)

    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    configs = {model: payload["config"] for model, payload in freeze["models"].items()}
    model_results = {}
    model_outcomes = {}
    for model in ("frozen_v04", "C1", "C2", "C3"):
        values = outcomes(cases, model, configs.get(model, {}))
        result = metrics(cases, values)
        result.update({
            "p_at_10": precision_at_k(cases, values, 10),
            "p_at_20": precision_at_k(cases, values, 20),
            "ndcg_at_20": ndcg_at_k(cases, values, 20),
        })
        model_results[model] = result
        model_outcomes[model] = values

    base = model_results["frozen_v04"]
    success = {model: candidate_success(base, model_results[model]) for model in ("C1", "C2", "C3")}
    eligible = [model for model, passed in success.items() if passed]
    selected = max(
        eligible,
        key=lambda model: (
            model_results[model]["recall"],
            model_results[model]["weak_recall"],
            model_results[model]["average_precision"],
            model_results[model]["abstention_rate"],
        ),
    ) if eligible else None
    weather_incremental = (
        model_results["C3"]["recall"] >= model_results["C2"]["recall"]
        and (
            model_results["C3"]["fpr"] < model_results["C2"]["fpr"]
            or model_results["C3"]["average_precision"] > model_results["C2"]["average_precision"]
        )
    )
    uncertainty = bootstrap(cases, configs)
    summary = {
        "schema_version": "lightguard.v08-confirmatory-summary.v1",
        "validation_kind": "independent_controlled_confirmatory_holdout",
        "holdout_sha256": holdout_sha,
        "candidate_freeze_sha256": CANDIDATE_FREEZE_SHA,
        "case_count": len(cases),
        "model_results": model_results,
        "candidate_success": success,
        "selected_candidate": selected,
        "weather_incremental_value": weather_incremental,
        "weather_policy": "candidate" if weather_incremental else "context_only",
        "uncertainty": uncertainty,
        "claim_boundary": "Generated controlled holdout only; no actual Gangneung or Chungju AMI performance claim.",
        "retuning_after_holdout": False,
    }
    SUMMARY.write_bytes(canonical_json(summary))

    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    fields = ["model", "recall", "fpr", "hard_negative_fpr", "weak_recall", "precision", "average_precision", "balanced_accuracy", "worst_cell_recall", "abstention_rate", "p_at_10", "p_at_20", "ndcg_at_20", "success"]
    with RESULTS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for model, result in model_results.items():
            writer.writerow({"model": model, **{field: result[field] for field in fields[1:-1]}, "success": success.get(model, "baseline")})

    UNCERTAINTY.write_text(
        "# v0.8 Confirmatory Uncertainty\n\n"
        f"- Holdout SHA-256: `{holdout_sha}`\n"
        f"- Cases: {len(cases)} controlled generated scenarios\n"
        f"- Bootstrap: {BOOTSTRAP_RESAMPLES} cell-and-class-stratified resamples, seed {BOOTSTRAP_SEED}\n\n"
        "## Wilson 95% intervals\n\n"
        + "\n".join(
            f"- {model}: recall {result['recall_wilson_95']}; FPR {result['fpr_wilson_95']}"
            for model, result in model_results.items()
        )
        + "\n\n## Bootstrap delta 95% intervals vs frozen v0.4\n\n"
        + "\n".join(
            f"- {model}: {values}"
            for model, values in uncertainty["delta_vs_frozen_v04"].items()
        )
        + "\n\nThese intervals quantify controlled generated-case uncertainty, not field AMI uncertainty.\n",
        encoding="utf-8",
    )
    WEATHER.write_text(
        "# v0.8 Weather Candidate Decision\n\n"
        f"- C2 recall/FPR/AP: {model_results['C2']['recall']:.4f} / {model_results['C2']['fpr']:.4f} / {model_results['C2']['average_precision']:.4f}\n"
        f"- C3 recall/FPR/AP: {model_results['C3']['recall']:.4f} / {model_results['C3']['fpr']:.4f} / {model_results['C3']['average_precision']:.4f}\n"
        f"- Incremental-value rule passed: {str(weather_incremental).lower()}\n"
        f"- Decision: **{'candidate weather modifier retained' if weather_incremental else 'weather remains context_only'}**\n\n"
        "KMA observations remain attached as official context. This controlled experiment does not establish a municipal weather policy.\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "holdout_cases": len(cases),
        "holdout_sha256": holdout_sha,
        "selected_candidate": selected,
        "weather_context_only": not weather_incremental,
        "metrics": model_results,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
