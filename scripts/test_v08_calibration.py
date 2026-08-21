#!/usr/bin/env python3
"""Verify v0.8 calibration freeze and split isolation."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "lightguard_v0_1/data/validation/v08_design_matrix.csv"
CALIBRATION = ROOT / "lightguard_v0_1/data/validation/v08/v08_calibration_set.json"
FREEZE = ROOT / "lightguard_v0_1/data/validation/v08/v08_candidate_freeze.json"


def main() -> None:
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    with DESIGN.open(encoding="utf-8", newline="") as handle:
        design = list(csv.DictReader(handle))
    cases = calibration["cases"]
    assert calibration["split"] == "calibration"
    assert calibration["v07_cases_ingested"] is False
    assert calibration["actual_ami"] is False
    assert len(cases) == 288
    assert {case["split"] for case in cases} == {"calibration"}
    calibration_ids = {case["case_id"] for case in cases}
    expected_ids = {row["case_id"] for row in design if row["split"] == "calibration"}
    confirmatory_ids = {row["case_id"] for row in design if row["split"] == "confirmatory"}
    assert calibration_ids == expected_ids
    assert not calibration_ids & confirmatory_ids
    assert hashlib.sha256(CALIBRATION.read_bytes()).hexdigest() == freeze["calibration_sha256"]
    assert freeze["confirmatory_seen"] is False
    assert freeze["threshold_policy"] == "fixed_at_0.55_not_lowered"
    assert set(freeze["models"]) == {"frozen_v04", "C1", "C2", "C3"}
    for name in ("C1", "C2", "C3"):
        assert freeze["models"][name]["config"]["threshold"] == 0.55
    assert freeze["models"]["C1"]["metrics"]["fpr"] <= 0.05
    assert freeze["models"]["C2"]["metrics"]["hard_negative_fpr"] <= 0.05
    assert all(
        case["rated_load_w"] is None and case["load_mismatch"] is None
        for case in cases
        if case["region_id"] == "chungju"
    )
    print("v0.8 calibration freeze: PASS")


if __name__ == "__main__":
    main()
