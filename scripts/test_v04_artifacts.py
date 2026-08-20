#!/usr/bin/env python3
"""Fail fast when v0.4 validation provenance or determinism is broken."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import date, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V03_SHA = "935bc5ea7d70e878f15113dc08d11dfee7ebcbb350d90d421f46a7704cf27368"


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    context = ROOT / "lightguard_v0_1" / "data" / "context"
    validation = ROOT / "lightguard_v0_1" / "data" / "validation"
    reports = ROOT / "lightguard_v0_1" / "reports"
    frozen = json.loads((context / "controlled_validation_frozen_2026.json").read_text(encoding="utf-8"))
    assert frozen["frozen_set_sha256"] == V03_SHA == canonical_hash(frozen["cases"]), "v0.3 frozen SHA changed"
    calibration = json.loads((validation / "v04_calibration_set.json").read_text(encoding="utf-8"))
    holdout = json.loads((validation / "v04_confirmatory_holdout.json").read_text(encoding="utf-8"))
    assert calibration["set_sha256"] == canonical_hash(calibration["cases"]), "calibration SHA is not deterministic"
    assert holdout["set_sha256"] == canonical_hash(holdout["cases"]), "holdout SHA is not deterministic"
    assert not ({row["cabinet_uid"] for row in calibration["cases"]} &
                {row["cabinet_uid"] for row in holdout["cases"]}), "asset overlap"
    assert not ({row["timestamp"] for row in calibration["cases"]} &
                {row["timestamp"] for row in holdout["cases"]}), "timing/weather overlap"
    regimes = json.loads((context / "kma_weather_regimes_2026.json").read_text(encoding="utf-8"))
    assert regimes["future_dates_excluded"] is True
    assert date.fromisoformat(regimes["requested_end"]) < date.today()
    for regime in regimes["regimes"]:
        for row in regime["representative_hours"]:
            assert row["source"] == "KMA_ASOS_HOURLY_OFFICIAL", "non-official weather"
            assert datetime.fromisoformat(row["timestamp"]).date() < date.today(), "future observation"
    with (reports / "v04_confirmatory_results.csv").open(encoding="utf-8-sig", newline="") as handle:
        assert len(list(csv.DictReader(handle))) == 4
    summary = json.loads((context / "v04_validation_summary.json").read_text(encoding="utf-8"))
    assert summary["candidate_reduction_vs_M0"] == (
        summary["holdout_m0"]["inspection_candidate_count"]
        - summary["best_v04"]["inspection_candidate_count"]
    ), "candidate reduction must use the same holdout"
    assert summary["false_positive_reduction_vs_M0"] == (
        summary["holdout_m0"]["normal_false_positive_count"]
        - summary["best_v04"]["normal_false_positive_count"]
    ), "false-positive reduction must use the same holdout"
    with (ROOT / "lightguard_app" / "assets" / "data" / "ami_event_windows" / "replay_manifest.json").open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    replay_files = sorted((ROOT / "lightguard_app" / "assets" / "data" / "ami_event_windows").glob("*.csv"))
    assert len(manifest["events"]) == len(replay_files) == 6, "actual AMI window count changed"
    with (reports / "actual_ami_replay_regression.csv").open(encoding="utf-8-sig", newline="") as handle:
        replay = list(csv.DictReader(handle))
    assert len(replay) == 6 and all(row["context_join"] == "none" for row in replay)
    decomposition = list(csv.DictReader((reports / "v03_score_decomposition.csv").open(encoding="utf-8-sig", newline="")))
    for model in ("M0", "M1", "M2", "M3"):
        rows = [row for row in decomposition if row["model"] == model]
        expected = sorted(rows, key=lambda row: (-float(row["total_score"]), row["case_id"]))
        assert [row["case_id"] for row in sorted(rows, key=lambda row: int(row["rank"]))] == [row["case_id"] for row in expected], "non-deterministic tie-break"
    print("v0.4 artifact integrity: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
