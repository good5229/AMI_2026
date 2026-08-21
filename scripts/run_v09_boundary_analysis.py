#!/usr/bin/env python3
"""Produce deterministic descriptive analyses from frozen v0.9 decisions only."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from v09_detector import average_precision, wilson


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v09"
REPORTS = ROOT / "lightguard_v0_1/reports/v09"
EXPECTED_CONFIG_SHA = "b536f8ca68222662c717cd27a6af4c3c64a3330782b0545503df6e4aff3e6232"
ARCHITECTURES = ("H1", "H2", "H3", "threshold_only")
CLAIM_BOUNDARY = "Controlled generated episode-separated holdout only; not field AMI accuracy or fault truth."


def decimal(value: float | None) -> str:
    return "" if value is None else f"{value:.8f}"


def interval(successes: int, total: int) -> str:
    if total == 0:
        return ""
    low, high = wilson(successes, total)
    return f"[{low:.8f}, {high:.8f}]"


def metric_row(rows: list[dict]) -> dict[str, str | int]:
    abnormal = [row for row in rows if row["label"] == "abnormal"]
    normal = [row for row in rows if row["label"] == "normal"]
    hard_normal = [row for row in normal if row["hard_negative"]]
    tp = sum(row["decision"] == "anomaly" for row in abnormal)
    fp = sum(row["decision"] == "anomaly" for row in normal)
    hard_fp = sum(row["decision"] == "anomaly" for row in hard_normal)
    scores = [float(row["score"]) for row in rows]
    labels = [int(row["label"] == "abnormal") for row in rows]
    return {
        "cases": len(rows),
        "abnormal_cases": len(abnormal),
        "normal_cases": len(normal),
        "hard_negative_normal_cases": len(hard_normal),
        "true_positives": tp,
        "false_positives": fp,
        "hard_negative_false_positives": hard_fp,
        "recall": decimal(tp / len(abnormal)) if abnormal else "",
        "recall_wilson_95": interval(tp, len(abnormal)),
        "normal_fpr": decimal(fp / len(normal)) if normal else "",
        "normal_fpr_wilson_95": interval(fp, len(normal)),
        "hard_negative_fpr": decimal(hard_fp / len(hard_normal)) if hard_normal else "",
        "hard_negative_fpr_wilson_95": interval(hard_fp, len(hard_normal)),
        "average_precision": decimal(average_precision(labels, scores)) if abnormal else "",
        "abstentions": sum(row["decision"] == "abstain" for row in rows),
    }


def solar_bin(minutes: float) -> str:
    if minutes < 15:
        return "0-15"
    if minutes < 30:
        return "15-30"
    if minutes < 60:
        return "30-60"
    if minutes < 120:
        return "60-120"
    return ">120"


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def frozen_rows() -> tuple[list[dict], dict]:
    calibration = json.loads((DATA / "v09_calibration_set.json").read_text(encoding="utf-8"))
    holdout = json.loads((DATA / "v09_confirmatory_holdout.json").read_text(encoding="utf-8"))
    config_path = DATA / "v09_candidate_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    summary = json.loads((DATA / "v09_confirmatory_summary.json").read_text(encoding="utf-8"))
    config_sha = hashlib.sha256(config_path.read_bytes()).hexdigest()
    if config_sha != EXPECTED_CONFIG_SHA:
        raise RuntimeError("v0.9 candidate configuration SHA is not the frozen value")
    if config.get("selected_candidate") != "H1" or summary.get("selected_candidate") != "H1":
        raise RuntimeError("frozen selected candidate must remain H1")
    if summary.get("candidate_config_sha256") != EXPECTED_CONFIG_SHA:
        raise RuntimeError("confirmatory summary config SHA mismatch")
    if summary.get("retuning_after_holdout") is not False:
        raise RuntimeError("confirmatory summary indicates post-holdout retuning")
    if len(calibration.get("cases", [])) != 384 or len(holdout.get("cases", [])) != 576:
        raise RuntimeError("frozen v0.9 scenario sizes must be 384 calibration and 576 holdout")
    if any(case.get("source") != "v09_controlled_generated_case_not_actual_ami" for case in holdout["cases"]):
        raise RuntimeError("non-controlled source found in confirmatory holdout")

    decisions: dict[tuple[str, str], dict] = {}
    with (DATA / "v09_confirmatory_decisions.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            decisions[(row["architecture"], row["case_id"])] = row
    expected = len(holdout["cases"]) * len(ARCHITECTURES)
    if len(decisions) != expected:
        raise RuntimeError("frozen decision count does not cover every architecture and holdout case")

    rows: list[dict] = []
    for architecture in ARCHITECTURES:
        for case in holdout["cases"]:
            decision = decisions[(architecture, case["case_id"])]
            rows.append({**case, **decision, "architecture": architecture})
    return rows, summary


def grouped_rows(rows: list[dict], key_name: str, key_fn) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["architecture"], str(key_fn(row)))].append(row)
    output: list[dict] = []
    for (architecture, level), members in sorted(grouped.items()):
        output.append({"architecture": architecture, key_name: level, **metric_row(members), "claim_boundary": CLAIM_BOUNDARY})
    return output


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    rows, _summary = frozen_rows()
    fields = [
        "architecture", "hard_negative_family", "cases", "abnormal_cases", "normal_cases",
        "hard_negative_normal_cases", "true_positives", "false_positives", "hard_negative_false_positives",
        "recall", "recall_wilson_95", "normal_fpr", "normal_fpr_wilson_95", "hard_negative_fpr",
        "hard_negative_fpr_wilson_95", "average_precision", "abstentions", "claim_boundary",
    ]
    hard_rows = [row for row in rows if row["label"] == "normal" and row["hard_negative"]]
    hard_results = grouped_rows(hard_rows, "hard_negative_family", lambda row: row["scenario_type"])
    for architecture in ARCHITECTURES:
        members = [row for row in hard_rows if row["architecture"] == architecture]
        hard_results.append({"architecture": architecture, "hard_negative_family": "overall", **metric_row(members), "claim_boundary": CLAIM_BOUNDARY})
    write_csv(REPORTS / "v09_hard_negative_results.csv", hard_results, fields)

    solar_groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        solar_groups[(row["architecture"], solar_bin(float(row["solar_margin_min"])), row["solar_side"])].append(row)
    solar_rows = []
    for (architecture, bucket, side), members in sorted(solar_groups.items()):
        solar_rows.append({"architecture": architecture, "solar_margin_bin_minutes": bucket, "solar_side": side,
                           **metric_row(members), "claim_boundary": CLAIM_BOUNDARY})
    solar_fields = ["architecture", "solar_margin_bin_minutes", "solar_side", *fields[2:]]
    write_csv(REPORTS / "v09_solar_boundary_analysis.csv", solar_rows, solar_fields)

    def availability(row: dict) -> str:
        load_missing = row["load_evidence"] is None
        phase_missing = row["phase_evidence"] is None
        if load_missing and phase_missing:
            return "both_missing"
        if load_missing:
            return "load_missing"
        if phase_missing:
            return "phase_missing"
        return "full"

    missing_rows = grouped_rows(rows, "feature_availability", availability)
    missing_fields = ["architecture", "feature_availability", *fields[2:]]
    write_csv(REPORTS / "v09_missing_feature_results.csv", missing_rows, missing_fields)

    effect_specs = (
        ("region", lambda row: row["region_id"]),
        ("season", lambda row: row["season"]),
        ("weather_regime", lambda row: row["weather_regime"]),
        ("episode", lambda row: row["episode_id"]),
        ("region_season", lambda row: f"{row['region_id']}:{row['season']}"),
    )
    effect_rows = []
    for family, key_fn in effect_specs:
        for row in grouped_rows(rows, "effect_level", key_fn):
            effect_rows.append({"effect_family": family, **row})
    effect_fields = ["effect_family", "architecture", "effect_level", *fields[2:]]
    write_csv(REPORTS / "v09_episode_effects.csv", effect_rows, effect_fields)
    print(json.dumps({"controlled_holdout_cases": len(rows) // len(ARCHITECTURES), "reports": 4, "selected_candidate": "H1"}))


if __name__ == "__main__":
    main()
