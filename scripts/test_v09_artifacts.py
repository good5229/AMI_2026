#!/usr/bin/env python3
"""Release contracts for the LightGuard v0.9 evidence package."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v09"
REPORTS = ROOT / "lightguard_v0_1/reports/v09"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    freeze = load(DATA / "v08_freeze_manifest.json")
    assert freeze["frozen_git_sha"] == "8772c2759d16ed7a6e669b940880e10cb242d1d6"
    for relative, expected in freeze["v08_hashes"].items():
        mapping = {"calibration_set": "v08_calibration_set.json", "confirmatory_holdout": "v08_confirmatory_holdout.json", "candidate_freeze": "v08_candidate_freeze.json"}
        actual = hashlib.sha256((ROOT / "lightguard_v0_1/data/validation/v08" / mapping[relative]).read_bytes()).hexdigest()
        assert actual == expected
    episode = load(DATA / "v09_episode_manifest.json")
    assert len(episode["episodes"]) == 48 and episode["scenario_generation_gate"]["status"] == "open"
    assert all(row["episode_status"] == "ready_for_scenario_generation" for row in episode["episodes"])
    assert set(Counter((row["cell_id"], row["split"]) for row in episode["episodes"]).values()) == {2}
    cal_ep = [row for row in episode["episodes"] if row["split"] == "calibration"]
    con_ep = [row for row in episode["episodes"] if row["split"] == "confirmatory"]
    assert not {row["episode_id"] for row in cal_ep} & {row["episode_id"] for row in con_ep}
    assert not {row["date"] for row in cal_ep} & {row["date"] for row in con_ep}
    assert not {(row["kma"]["station_id"], row["date"]) for row in cal_ep} & {(row["kma"]["station_id"], row["date"]) for row in con_ep}
    calibration = load(DATA / "v09_calibration_set.json")
    holdout = load(DATA / "v09_confirmatory_holdout.json")
    assert calibration["case_count"] == 384 and holdout["case_count"] == 576
    for payload, per_label in ((calibration, 8), (holdout, 12)):
        counts = Counter((case["episode_id"], case["label"]) for case in payload["cases"])
        assert set(counts.values()) == {per_label}
        assert all(case["weather_weight"] == 0 and case["load_imputation"] == "none" for case in payload["cases"])
    for field in ("case_id", "episode_id", "date", "signal_parameter_id", "asset_cabinet_uid"):
        assert not {row[field] for row in calibration["cases"]} & {row[field] for row in holdout["cases"]}, field
    config = load(DATA / "v09_candidate_config.json")
    summary = load(DATA / "v09_confirmatory_summary.json")
    assert config["confirmatory_seen"] is False and config["post_confirmatory_retuning_permitted"] is False
    assert config["weather_weight"] == 0 and config["load_imputation"] == "none"
    assert summary["retuning_after_holdout"] is False and summary["weather_weight"] == 0 and summary["load_imputation"] == "none"
    selected = summary["selected_candidate"]
    if selected is not None:
        metric = summary["model_results"][selected]
        assert metric["recall"] >= .70 and metric["fpr"] <= .05 and metric["hard_negative_fpr"] <= .05 and metric["worst_cell_recall"] >= .55
    assert {row["solar_margin_bin_minutes"] for row in rows(REPORTS / "v09_solar_boundary_analysis.csv")} >= {"0-15", "15-30", "30-60", "60-120", ">120"}
    assert {row["feature_availability"] for row in rows(REPORTS / "v09_missing_feature_results.csv")} >= {"full", "load_missing", "phase_missing", "both_missing"}
    bootstrap = (REPORTS / "v09_episode_bootstrap.md").read_text(encoding="utf-8")
    assert "2000" in bootstrap and "20260901" in bootstrap and "episode" in bootstrap.lower()
    actual = rows(REPORTS / "v09_actual_ami_regression.csv")
    assert len(actual) == 6 and all(row["field_truth_label"] == "unavailable" and row["promotion_gate_input"] == "false" for row in actual)
    app = load(ROOT / "lightguard_app/assets/data/context/v09_specificity_summary.json")
    assert app["confirmatory_cases"] == 576 and app["confirmatory_episodes"] == 24
    assert app["episode_overlap"] == app["date_overlap"] == app["kma_observation_overlap"] == 0
    assert app["actual_ami_is_truth"] is False
    audit = (REPORTS / "v09_independent_audit.md").read_text(encoding="utf-8")
    assert "PASS" in audit and "Critical" in audit
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.splitlines()
    forbidden = [name for name in tracked if name == ".env" or name.startswith(("harness_docs/", "official_docs/")) or name.lower().endswith((".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"))]
    assert not forbidden, forbidden
    reproducibility = load(REPORTS / "reproducibility_manifest.json")
    for relative, expected in reproducibility["files"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected, relative
    print("v0.9 artifact contracts: PASS")


if __name__ == "__main__":
    main()
