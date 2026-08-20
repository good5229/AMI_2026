#!/usr/bin/env python3
"""End-to-end artifact contracts for the v0.8 controlled experiment."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v08"
REPORTS = ROOT / "lightguard_v0_1/reports/v08"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def csv_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    calibration = load(DATA / "v08_calibration_set.json")
    holdout = load(DATA / "v08_confirmatory_holdout.json")
    freeze = load(DATA / "v08_candidate_freeze.json")
    summary = load(DATA / "v08_confirmatory_summary.json")
    features = load(DATA / "v08_feature_availability_cases.json")
    assert len(calibration["cases"]) == 288
    assert len(holdout["cases"]) == 432
    assert Counter(case["label"] for case in holdout["cases"]) == {"normal": 216, "abnormal": 216}
    for field in ("case_id", "random_seed", "factor_tuple_id", "signal_parameter_id", "asset_cabinet_uid"):
        left = {case[field] for case in calibration["cases"]}
        right = {case[field] for case in holdout["cases"]}
        assert not left & right, f"split leakage: {field}"
    assert hashlib.sha256(DATA.joinpath("v08_calibration_set.json").read_bytes()).hexdigest() == freeze["calibration_sha256"]
    assert hashlib.sha256(DATA.joinpath("v08_candidate_freeze.json").read_bytes()).hexdigest() == holdout["candidate_freeze_sha256"]
    assert freeze["confirmatory_seen"] is False
    assert freeze["threshold_policy"] == "fixed_at_0.55_not_lowered"
    assert holdout["post_result_retuning_permitted"] is False
    assert summary["retuning_after_holdout"] is False
    assert summary["selected_candidate"] is None
    assert summary["weather_policy"] == "context_only"
    assert summary["uncertainty"]["resamples"] == 1000
    base = summary["model_results"]["frozen_v04"]
    c1 = summary["model_results"]["C1"]
    assert c1["recall"] > base["recall"]
    assert c1["weak_recall"] > base["weak_recall"]
    assert c1["fpr"] > 0.05
    assert c1["hard_negative_fpr"] > 0.05
    assert summary["candidate_success"] == {"C1": False, "C2": False, "C3": False}
    assert features["case_count"] == 1728
    assert features["load_values_added"] is False
    assert all(case["imputation"] == "none" for case in features["cases"])
    factor_rows = csv_rows(REPORTS / "v08_factor_effects.csv")
    assert len(factor_rows) == 180
    assert all(row["interpretation"] == "controlled_generated_factor_effect_not_actual_region_effect" for row in factor_rows)
    app = load(ROOT / "lightguard_app/assets/data/context/v08_detector_summary.json")
    assert app["selected_candidate"] is None
    assert app["actual_external_regional_ami"] == "unavailable"
    assert app["chungju"]["imputation"] == "none"
    final_report = (REPORTS / "v08_final_summary.md").read_text(encoding="utf-8")
    assert "No candidate passed" in final_report
    assert "Claims Prohibited" in final_report
    audit = (REPORTS / "v08_independent_audit.md").read_text(encoding="utf-8")
    assert "PASS with non-critical residual risks" in audit
    assert "11" in audit
    manifest = load(REPORTS / "reproducibility_manifest.json")
    for relative, expected in manifest["files"].items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        assert actual == expected, relative
    print("v0.8 artifact contracts: PASS")


if __name__ == "__main__":
    main()
