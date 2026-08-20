#!/usr/bin/env python3
"""Evaluate deterministic data-quality robustness and frozen-score sensitivity."""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

from run_v04_validation import metrics, rank_rows, v04_score


ROOT = Path(__file__).resolve().parents[1]
V05_DATA = ROOT / "lightguard_v0_1" / "data" / "validation" / "v05"
V05_REPORTS = ROOT / "lightguard_v0_1" / "reports" / "v05"
REPLAY_DIR = ROOT / "lightguard_app" / "assets" / "data" / "ami_event_windows"
SEED = 5052026
FROZEN_WEIGHTS = {
    "activation": .6, "duration": .25, "load": .25, "phase": .2,
    "solar_penalty": .2, "transient_penalty": .2, "policy_penalty": .2,
    "weather": 0.0, "threshold": .55,
}


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_holdout() -> list[dict]:
    path = ROOT / "lightguard_v0_1" / "data" / "validation" / "v04_confirmatory_holdout.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    expected = "1be716621da5b53bce11a748d9b05e63d4aa329e7d62b8f16e606b2ccff09831"
    if payload["set_sha256"] != expected:
        raise RuntimeError("v0.4 holdout SHA changed")
    return payload["cases"]


def stable_fraction(case_id: str, seed: int) -> float:
    raw = hashlib.sha256(f"{seed}|{case_id}".encode()).digest()
    return int.from_bytes(raw[:8], "big") / 2**64


def controlled_variant(cases: list[dict], stress: dict) -> tuple[list[dict], set[str]]:
    result = copy.deepcopy(cases)
    unavailable = set()
    kind = stress["kind"]
    for case in result:
        fraction = stable_fraction(case["case_id"], stress["seed"])
        if kind == "random_missingness" and fraction < stress["rate"]:
            unavailable.add(case["case_id"])
        elif kind == "contiguous_gap":
            if case["duration_min"] <= stress["minutes"] and fraction < .5:
                case["duration_min"] = max(0, case["duration_min"] - stress["minutes"])
                if case["duration_min"] == 0:
                    unavailable.add(case["case_id"])
        elif kind == "downsample":
            interval = stress["minutes"]
            if case["duration_min"] < interval and fraction < .75:
                unavailable.add(case["case_id"])
            else:
                case["duration_min"] = max(interval, math.ceil(case["duration_min"] / interval) * interval)
        elif kind == "phase_dropout":
            if case["phase_selectivity"] > 0 and fraction < .5:
                case["phase_selectivity"] *= .5
        elif kind == "duplicate_timestamp":
            # Robust policy deduplicates by timestamp before feature extraction.
            pass
        elif kind == "measurement_channel_missing" and fraction < stress["rate"]:
            unavailable.add(case["case_id"])
    return result, unavailable


def controlled_rank(cases: list[dict], unavailable: set[str]) -> list[dict]:
    def scorer(case: dict) -> dict:
        if case["case_id"] in unavailable:
            return {"total_score": -1.0, "candidate": False}
        return v04_score(case, FROZEN_WEIGHTS, False)
    return rank_rows(cases, scorer)


def load_replay() -> tuple[list[dict], dict[str, list[dict]]]:
    manifest = json.loads((REPLAY_DIR / "replay_manifest.json").read_text(encoding="utf-8"))
    events = []
    with (ROOT / "lightguard_app" / "assets" / "data" / "ami_events.csv").open(encoding="utf-8-sig", newline="") as handle:
        canonical = {(row["meter_id"], row["first_sample"][:10]): row for row in csv.DictReader(handle)}
    windows = {}
    for item in manifest["events"]:
        event = canonical[(item["meter_id"], item["date"])]
        event = {**event, "file": item["file"]}
        events.append(event)
        with (REPLAY_DIR / item["file"]).open(encoding="utf-8-sig", newline="") as handle:
            rows = []
            for row in csv.DictReader(handle):
                rows.append({
                    "timestamp": datetime.fromisoformat(row["timestamp"]),
                    "i1": float(row["i1"]) if row["i1"] else None,
                    "i2": float(row["i2"]) if row["i2"] else None,
                    "i3": float(row["i3"]) if row["i3"] else None,
                })
            windows[item["file"]] = rows
    return events, windows


def perturb_rows(rows: list[dict], event: dict, stress: dict) -> list[dict]:
    result = copy.deepcopy(rows)
    kind = stress["kind"]
    rng = random.Random(stress["seed"] + int(hashlib.sha1(event["event_id"].encode()).hexdigest()[:8], 16))
    if kind == "random_missingness":
        for row in result:
            if rng.random() < stress["rate"]:
                row["i1"] = row["i2"] = row["i3"] = None
    elif kind == "contiguous_gap":
        start = datetime.fromisoformat(event["first_sample"])
        end = start + timedelta(minutes=stress["minutes"])
        for row in result:
            if start <= row["timestamp"] < end:
                row["i1"] = row["i2"] = row["i3"] = None
    elif kind == "downsample":
        factor = stress["minutes"] // 15
        for index, row in enumerate(result):
            if index % factor != 0:
                row["i1"] = row["i2"] = row["i3"] = None
    elif kind == "phase_dropout":
        for row in result:
            row[stress["phase"]] = None
    elif kind == "duplicate_timestamp" and result:
        duplicate = copy.deepcopy(result[len(result) // 2])
        result.insert(len(result) // 2, duplicate)
    elif kind == "duplicate_conflict" and result:
        duplicate = copy.deepcopy(result[len(result) // 2])
        for phase in ("i1", "i2", "i3"):
            if duplicate[phase] is not None:
                duplicate[phase] += 1.0
                break
        result.insert(len(result) // 2, duplicate)
    elif kind == "measurement_channel_missing":
        start, end = datetime.fromisoformat(event["first_sample"]), datetime.fromisoformat(event["last_sample"]) + timedelta(minutes=15)
        for row in result:
            if start <= row["timestamp"] < end:
                row["i1"] = row["i2"] = row["i3"] = None
    return result


def deduplicate(rows: list[dict]) -> tuple[list[dict], int]:
    by_time: dict[datetime, list[dict]] = {}
    for row in rows:
        by_time.setdefault(row["timestamp"], []).append(row)
    result = []
    conflict_count = 0
    for timestamp in sorted(by_time):
        group = by_time[timestamp]
        signatures = {tuple(row[key] for key in ("i1", "i2", "i3")) for row in group}
        selected = copy.deepcopy(group[0])
        if len(signatures) > 1:
            conflict_count += 1
            selected["i1"] = selected["i2"] = selected["i3"] = None
        result.append(selected)
    return result, conflict_count


def interval_iou(left: tuple[datetime, datetime] | None, right: tuple[datetime, datetime]) -> float:
    if left is None:
        return 0.0
    intersection = max(0.0, (min(left[1], right[1]) - max(left[0], right[0])).total_seconds())
    union = (max(left[1], right[1]) - min(left[0], right[0])).total_seconds()
    return intersection / union if union else 1.0


def detect_replay(rows: list[dict], event: dict) -> tuple[list[tuple[datetime, datetime]], set[str], int]:
    rows, conflict_count = deduplicate(rows)
    off = float(event["off_baseline_a"])
    on = float(event["on_baseline_a"])
    if on <= off:
        return [], set(), conflict_count
    points = []
    phase_present = set()
    for row in rows:
        measured = [row[key] for key in ("i1", "i2", "i3") if row[key] is not None]
        if not measured:
            continue
        activation = (sum(measured) - off) / (on - off)
        if activation >= .2:
            points.append(row["timestamp"])
            phase_present.update(key for key in ("i1", "i2", "i3") if row[key] is not None)
    if not points:
        return [], phase_present, conflict_count
    groups = [[points[0]]]
    for timestamp in points[1:]:
        if (timestamp - groups[-1][-1]).total_seconds() / 60 > 30:
            groups.append([timestamp])
        else:
            groups[-1].append(timestamp)
    cadence = 15 if len(rows) < 2 else int(statistics_median_gaps(rows))
    intervals = [(group[0], group[-1] + timedelta(minutes=cadence)) for group in groups]
    return intervals, phase_present, conflict_count


def statistics_median_gaps(rows: list[dict]) -> float:
    values = sorted({row["timestamp"] for row in rows})
    gaps = sorted((right - left).total_seconds() / 60 for left, right in zip(values, values[1:]) if right > left)
    return gaps[len(gaps) // 2] if gaps else 15


def actual_metrics(events: list[dict], windows: dict[str, list[dict]], stress: dict) -> dict:
    covered = 0
    ious = []
    phase_consistent = 0
    detection_vector = []
    unavailable_samples = 0
    total_samples = 0
    duplicate_conflicts = 0
    transform_hashes = {}
    for event in events:
        rows = perturb_rows(windows[event["file"]], event, stress)
        total_samples += len(rows)
        unavailable_samples += sum(all(row[key] is None for key in ("i1", "i2", "i3")) for row in rows)
        serializable = [
            {**row, "timestamp": row["timestamp"].isoformat()}
            for row in rows
        ]
        transform_hashes[event["event_id"]] = hashlib.sha256(
            json.dumps(serializable, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        detected_intervals, measured_phases, conflicts = detect_replay(rows, event)
        duplicate_conflicts += conflicts
        expected = (datetime.fromisoformat(event["first_sample"]),
                    datetime.fromisoformat(event["last_sample"]) + timedelta(minutes=15))
        iou = max((interval_iou(detected, expected) for detected in detected_intervals), default=0.0)
        is_covered = iou > 0
        covered += is_covered
        ious.append(iou)
        detection_vector.append(is_covered)
        expected_phases = set(filter(None, event["active_phases"].split(",")))
        phase_consistent += bool(expected_phases & measured_phases) if expected_phases else True
    return {
        "canonical_event_covered_count": covered,
        "canonical_event_replay_coverage": covered / len(events),
        "mean_interval_iou": sum(ious) / len(ious),
        "phase_consistency": phase_consistent / len(events),
        "detection_vector": detection_vector,
        "unavailable_sample_count": unavailable_samples,
        "total_sample_count": total_samples,
        "duplicate_conflict_count": duplicate_conflicts,
        "transform_hashes": transform_hashes,
    }


def jaccard_bool(left: list[bool], right: list[bool]) -> float:
    intersection = sum(a and b for a, b in zip(left, right))
    union = sum(a or b for a, b in zip(left, right))
    return intersection / union if union else 1.0


def ranks(rows: list[dict]) -> dict[str, int]:
    return {row["case_id"]: index for index, row in enumerate(rows, 1)}


def spearman(left: dict[str, int], right: dict[str, int]) -> float:
    n = len(left)
    delta = sum((left[key] - right[key]) ** 2 for key in left)
    return 1 - 6 * delta / (n * (n * n - 1))


def kendall(left: dict[str, int], right: dict[str, int]) -> float:
    keys = sorted(left)
    concordant = discordant = 0
    for index, first in enumerate(keys):
        for second in keys[index + 1:]:
            product = (left[first] - left[second]) * (right[first] - right[second])
            concordant += product > 0
            discordant += product < 0
    total = concordant + discordant
    return (concordant - discordant) / total if total else 1.0


def sensitivity(cases: list[dict]) -> tuple[list[dict], dict]:
    baseline_rows = rank_rows(cases, lambda case: v04_score(case, FROZEN_WEIGHTS, False))
    baseline_metrics = metrics(baseline_rows)
    baseline_ranks = ranks(baseline_rows)
    baseline_top20 = {row["case_id"] for row in baseline_rows[:20]}
    configs = []
    for threshold in (.50, .525, .55, .575, .60):
        configs.append(("threshold", threshold, {**FROZEN_WEIGHTS, "threshold": threshold}))
    for key, value in FROZEN_WEIGHTS.items():
        if key in ("threshold", "weather") or value == 0:
            continue
        for factor in (.8, .9, 1.0, 1.1, 1.2):
            configs.append((key, round(factor, 2), {**FROZEN_WEIGHTS, key: value * factor}))
    rows = []
    for parameter, setting, weights in configs:
        ranked = rank_rows(cases, lambda case, w=weights: v04_score(case, w, False))
        result = metrics(ranked)
        variant_ranks = ranks(ranked)
        top20 = {row["case_id"] for row in ranked[:20]}
        rows.append({
            "parameter": parameter, "setting": setting,
            "anomaly_recall": result["anomaly_recall"], "normal_fpr": result["normal_fpr"],
            "precision_at_10": result["precision_at_10"], "precision_at_20": result["precision_at_20"],
            "candidate_count": result["inspection_candidate_count"],
            "spearman_rho": spearman(baseline_ranks, variant_ranks),
            "kendall_tau": kendall(baseline_ranks, variant_ranks),
            "top20_overlap": len(baseline_top20 & top20) / 20,
            "frozen_baseline": parameter == "threshold" and setting == .55 or setting == 1.0,
            "promotion_policy": "diagnostic_only_no_retuning",
        })
    deviations = [row for row in rows if not row["frozen_baseline"]]
    most_sensitive = min(deviations, key=lambda row: (row["kendall_tau"], row["spearman_rho"], row["top20_overlap"]))
    stable = all(
        abs(row["anomaly_recall"] - baseline_metrics["anomaly_recall"]) <= .05
        and abs(row["normal_fpr"] - baseline_metrics["normal_fpr"]) <= .03
        and row["top20_overlap"] >= .8
        for row in deviations
    )
    return rows, {"classification": "Stable" if stable else "Knife-edge or locally sensitive",
                  "criteria": "all one-at-a-time neighbors: recall delta <= .05, FPR delta <= .03, Top-20 overlap >= .80",
                  "most_sensitive": most_sensitive, "baseline_metrics": baseline_metrics}


def main() -> int:
    cases = load_holdout()
    events, windows = load_replay()
    stresses = [
        {"stress_id": "baseline", "kind": "none", "seed": SEED},
        *({"stress_id": f"missing_{int(rate*100)}pct", "kind": "random_missingness", "rate": rate, "seed": SEED + index}
          for index, rate in enumerate((.05, .10, .20), 1)),
        *({"stress_id": f"gap_{minutes}m", "kind": "contiguous_gap", "minutes": minutes, "seed": SEED + 10 + index}
          for index, minutes in enumerate((30, 60, 120), 1)),
        *({"stress_id": f"downsample_{minutes}m", "kind": "downsample", "minutes": minutes, "seed": SEED + 20 + index}
          for index, minutes in enumerate((30, 60), 1)),
        *({"stress_id": f"drop_{phase}", "kind": "phase_dropout", "phase": phase, "seed": SEED + 30 + index}
          for index, phase in enumerate(("i1", "i2", "i3"), 1)),
        {"stress_id": "duplicate_timestamp", "kind": "duplicate_timestamp", "seed": SEED + 40},
        {"stress_id": "duplicate_conflict", "kind": "duplicate_conflict", "seed": SEED + 41},
        {"stress_id": "measurement_channel_missing", "kind": "measurement_channel_missing", "rate": .10, "seed": SEED + 50},
    ]
    write_json(V05_DATA / "stress_suite_cases.json", {
        "schema_version": "lightguard-v0.5-stress-suite",
        "deterministic_seed": SEED,
        "null_policy": "missing measurement remains null and becomes not-evaluable; never coerced to zero",
        "timestamp_lattice_policy": "missingness, gaps, and downsampling preserve source timestamps and set unavailable channels to null",
        "duplicate_policy": "exact duplicates collapse; conflicting duplicates become unavailable and are counted",
        "stresses": stresses,
    })
    baseline_actual = actual_metrics(events, windows, stresses[0])
    results = []
    for stress in stresses:
        transformed, unavailable = controlled_variant(cases, stress)
        controlled = metrics(controlled_rank(transformed, unavailable))
        actual = actual_metrics(events, windows, stress)
        results.append({
            "stress_id": stress["stress_id"], "kind": stress["kind"], "seed": stress["seed"],
            "controlled_anomaly_recall": controlled["anomaly_recall"],
            "controlled_normal_fpr": controlled["normal_fpr"],
            "controlled_precision_at_10": controlled["precision_at_10"],
            "controlled_precision_at_20": controlled["precision_at_20"],
            "controlled_candidate_count": controlled["inspection_candidate_count"],
            "controlled_evaluable_rate": (len(cases) - len(unavailable)) / len(cases),
            "actual_canonical_event_coverage": actual["canonical_event_replay_coverage"],
            "actual_interval_iou": actual["mean_interval_iou"],
            "actual_phase_consistency": actual["phase_consistency"],
            "actual_candidate_jaccard": jaccard_bool(baseline_actual["detection_vector"], actual["detection_vector"]),
            "actual_candidate_count_drift": actual["canonical_event_covered_count"] - baseline_actual["canonical_event_covered_count"],
            "actual_unavailable_sample_count": actual["unavailable_sample_count"],
            "actual_total_sample_count": actual["total_sample_count"],
            "actual_duplicate_conflict_count": actual["duplicate_conflict_count"],
            "actual_transform_hashes": json.dumps(actual["transform_hashes"], sort_keys=True),
            "claim_scope": "technical robustness; actual AMI has no truth labels",
        })
    write_csv(V05_REPORTS / "robustness_results.csv", results)

    sensitivity_rows, sensitivity_summary = sensitivity(cases)
    write_csv(V05_REPORTS / "parameter_sensitivity.csv", sensitivity_rows)
    write_json(V05_DATA / "sensitivity_grid.json", {
        "schema_version": "lightguard-v0.5-frozen-sensitivity",
        "frozen_weights": FROZEN_WEIGHTS,
        "grid_policy": "one parameter at a time; diagnostic only; holdout never retuned",
        "rows": sensitivity_rows,
        "summary": sensitivity_summary,
    })
    robustness_lines = [
        "# LightGuard v0.5 Data-Quality Robustness", "",
        "Controlled metrics and actual replay metrics are reported separately. Actual six-event coverage is not field recall or accuracy.", "",
        "| stress | controlled recall | FPR | P@20 | actual coverage | interval IoU | phase consistency | candidate Jaccard |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in results:
        robustness_lines.append(
            f"| {row['stress_id']} | {row['controlled_anomaly_recall']:.6f} | {row['controlled_normal_fpr']:.6f} | "
            f"{row['controlled_precision_at_20']:.6f} | {row['actual_canonical_event_coverage']:.6f} | "
            f"{row['actual_interval_iou']:.6f} | {row['actual_phase_consistency']:.6f} | {row['actual_candidate_jaccard']:.6f} |"
        )
    robustness_lines += ["", "Missing channels are never interpreted as zero current. Stress outcomes measure technical replay stability only."]
    (V05_REPORTS / "robustness_summary.md").write_text("\n".join(robustness_lines) + "\n", encoding="utf-8")
    sensitive = sensitivity_summary["most_sensitive"]
    (V05_REPORTS / "parameter_sensitivity_summary.md").write_text(
        "# LightGuard v0.5 Frozen Parameter Sensitivity\n\n"
        f"- Classification: **{sensitivity_summary['classification']}**\n"
        f"- Precommitted criterion: {sensitivity_summary['criteria']}\n"
        f"- Most sensitive neighbor: `{sensitive['parameter']}={sensitive['setting']}`\n"
        f"- Spearman rho: {sensitive['spearman_rho']:.6f}\n"
        f"- Kendall tau: {sensitive['kendall_tau']:.6f}\n"
        f"- Top-20 overlap: {sensitive['top20_overlap']:.6f}\n"
        "- No sensitivity result changes the frozen v0.4 configuration.\n",
        encoding="utf-8")
    print(json.dumps({"stress_count": len(results), "sensitivity_count": len(sensitivity_rows),
                      "sensitivity": sensitivity_summary}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
