#!/usr/bin/env python3
"""Episode-cluster bootstrap for frozen v0.9 confirmatory decisions."""

from __future__ import annotations

import csv
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

from v09_detector import average_precision


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v09"
REPORT = ROOT / "lightguard_v0_1/reports/v09/v09_episode_bootstrap.md"
EXPECTED_CONFIG_SHA = "b536f8ca68222662c717cd27a6af4c3c64a3330782b0545503df6e4aff3e6232"
ARCHITECTURES = ("H1", "H2", "H3", "threshold_only")
SEED = 20260901
RESAMPLES = 2000


def metric_values(rows: list[dict]) -> dict[str, float]:
    abnormal = [row for row in rows if row["label"] == "abnormal"]
    normal = [row for row in rows if row["label"] == "normal"]
    hard_normal = [row for row in normal if row["hard_negative"]]
    if not abnormal or not normal or not hard_normal:
        raise RuntimeError("each episode bootstrap sample must include abnormal, normal, and hard-negative normal cases")
    return {
        "recall": sum(row["decision"] == "anomaly" for row in abnormal) / len(abnormal),
        "fpr": sum(row["decision"] == "anomaly" for row in normal) / len(normal),
        "hard_negative_fpr": sum(row["decision"] == "anomaly" for row in hard_normal) / len(hard_normal),
        "average_precision": average_precision(
            [int(row["label"] == "abnormal") for row in rows], [float(row["score"]) for row in rows]
        ),
    }


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def frozen_episode_rows() -> dict[str, dict[str, list[dict]]]:
    calibration = json.loads((DATA / "v09_calibration_set.json").read_text(encoding="utf-8"))
    holdout = json.loads((DATA / "v09_confirmatory_holdout.json").read_text(encoding="utf-8"))
    config_path = DATA / "v09_candidate_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    summary = json.loads((DATA / "v09_confirmatory_summary.json").read_text(encoding="utf-8"))
    if hashlib.sha256(config_path.read_bytes()).hexdigest() != EXPECTED_CONFIG_SHA:
        raise RuntimeError("v0.9 candidate configuration SHA is not the frozen value")
    if config.get("selected_candidate") != "H1" or summary.get("selected_candidate") != "H1":
        raise RuntimeError("frozen selected candidate must remain H1")
    if summary.get("candidate_config_sha256") != EXPECTED_CONFIG_SHA or summary.get("retuning_after_holdout") is not False:
        raise RuntimeError("confirmatory freeze contract failed")
    if len(calibration.get("cases", [])) != 384 or len(holdout.get("cases", [])) != 576:
        raise RuntimeError("frozen v0.9 scenario sizes must be 384 calibration and 576 holdout")
    if any(case.get("source") != "v09_controlled_generated_case_not_actual_ami" for case in holdout["cases"]):
        raise RuntimeError("non-controlled source found in confirmatory holdout")

    decisions: dict[tuple[str, str], dict] = {}
    with (DATA / "v09_confirmatory_decisions.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            decisions[(row["architecture"], row["case_id"])] = row
    if len(decisions) != len(holdout["cases"]) * len(ARCHITECTURES):
        raise RuntimeError("frozen decision count does not cover every architecture and holdout case")

    by_architecture: dict[str, dict[str, list[dict]]] = {architecture: defaultdict(list) for architecture in ARCHITECTURES}
    for architecture in ARCHITECTURES:
        for case in holdout["cases"]:
            decision = decisions[(architecture, case["case_id"])]
            by_architecture[architecture][case["episode_id"]].append({**case, **decision})
    episode_ids = set(by_architecture["H1"])
    if len(episode_ids) != 24 or any(set(episodes) != episode_ids for episodes in by_architecture.values()):
        raise RuntimeError("confirmatory holdout must contain the same 24 complete episodes for every architecture")
    return by_architecture


def main() -> None:
    episodes = frozen_episode_rows()
    episode_ids = sorted(episodes["H1"])
    observed = {architecture: metric_values([row for episode in episode_ids for row in episodes[architecture][episode]])
                for architecture in ARCHITECTURES}
    deltas: dict[tuple[str, str], list[float]] = {(architecture, metric): [] for architecture in ARCHITECTURES[:-1]
                                                   for metric in observed["H1"]}
    rng = random.Random(SEED)
    for _ in range(RESAMPLES):
        sampled_ids = [episode_ids[rng.randrange(len(episode_ids))] for _ in episode_ids]
        sampled = {architecture: metric_values([row for episode in sampled_ids for row in episodes[architecture][episode]])
                   for architecture in ARCHITECTURES}
        for architecture in ARCHITECTURES[:-1]:
            for metric in observed[architecture]:
                deltas[(architecture, metric)].append(sampled[architecture][metric] - sampled["threshold_only"][metric])

    lines = [
        "# v0.9 episode-cluster bootstrap",
        "",
        "## Scope",
        "",
        "This is a controlled generated episode-separated confirmatory analysis only. It is not field AMI accuracy, fault truth, or a promotion retuning input.",
        "",
        "## Frozen inputs",
        "",
        f"- Selected candidate: `H1`",
        f"- Candidate configuration SHA-256: `{EXPECTED_CONFIG_SHA}`",
        f"- Confirmatory episodes: `{len(episode_ids)}`; cases: `576`",
        f"- Bootstrap resamples: `{RESAMPLES}`; fixed seed: `{SEED}`",
        "- Resampling unit: complete episode. Each resample draws 24 episode IDs with replacement and retains every case in each drawn episode.",
        "- Comparator: `threshold_only`; delta is candidate minus comparator. Lower deltas are favorable for FPR metrics, higher deltas are favorable for recall/AP.",
        "- No threshold, detector, configuration, scenario, or confirmatory result was changed.",
        "",
        "## Observed metrics and bootstrap delta intervals",
        "",
        "| Candidate | Metric | Observed candidate | Observed threshold_only | Observed delta | Bootstrap mean delta | 2.5% | 97.5% |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for architecture in ARCHITECTURES[:-1]:
        for metric in ("recall", "fpr", "hard_negative_fpr", "average_precision"):
            values = deltas[(architecture, metric)]
            observed_delta = observed[architecture][metric] - observed["threshold_only"][metric]
            lines.append(
                f"| {architecture} | {metric} | {observed[architecture][metric]:.8f} | "
                f"{observed['threshold_only'][metric]:.8f} | {observed_delta:.8f} | "
                f"{sum(values) / len(values):.8f} | {percentile(values, .025):.8f} | {percentile(values, .975):.8f} |"
            )
    lines.extend([
        "",
        "## Interpretation boundary",
        "",
        "The percentile intervals quantify variation across resampled generated episodes under the frozen confirmatory decisions. They do not establish generalization to unobserved field AMI data or causal weather effects. Weather remains context-only with weight `0.0`.",
        "",
    ])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"episodes": len(episode_ids), "resamples": RESAMPLES, "seed": SEED, "selected_candidate": "H1"}))


if __name__ == "__main__":
    main()
