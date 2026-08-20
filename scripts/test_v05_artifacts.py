#!/usr/bin/env python3
"""Assert v0.5 frozen, causal, robustness, replay, and provenance invariants."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1" / "data" / "validation" / "v05"
REPORTS = ROOT / "lightguard_v0_1" / "reports" / "v05"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    summary = json.loads((ROOT / "lightguard_v0_1" / "data" / "context" / "v04_validation_summary.json").read_text(encoding="utf-8"))
    assert summary["v03_frozen_set_sha256"] == "935bc5ea7d70e878f15113dc08d11dfee7ebcbb350d90d421f46a7704cf27368"
    assert summary["calibration_sha256"] == "8fe85425f6ca3b9bc2517a137da96d3edc22bbf387209b53efd933364496032e"
    assert summary["confirmatory_holdout_sha256"] == "1be716621da5b53bce11a748d9b05e63d4aa329e7d62b8f16e606b2ccff09831"
    assert summary["frozen_weights"] == {"activation": .6, "duration": .25, "load": .25, "phase": .2,
                                           "solar_penalty": .2, "transient_penalty": .2, "policy_penalty": .2,
                                           "weather": 0, "threshold": .55}
    with (DATA / "causal_walkforward_results.csv").open(encoding="utf-8-sig", newline="") as handle:
        walk = list(csv.DictReader(handle))
    assert {row["baseline_window"] for row in walk} == {"7d", "14d", "30d", "expanding"}
    assert any(row["status"] == "not_evaluable_warmup" for row in walk)
    for row in walk:
        if row.get("baseline_history_end"):
            assert datetime.fromisoformat(row["baseline_history_end"]).replace(tzinfo=None) < datetime.fromisoformat(row["evaluation_date"]), "future leakage"
        if row["status"] == "candidate":
            assert datetime.fromisoformat(row["latest_consumed_availability_time"]) < datetime.fromisoformat(row["decision_time"]), "observation availability leakage"
        assert row["truth_label"] == "unavailable_known_detector_candidate_only"
    causal = json.loads((DATA / "causal_walkforward_summary.json").read_text(encoding="utf-8"))
    for window in ("7d", "14d", "30d", "expanding"):
        assert causal[window]["canonical_event_covered_count"] == 6
    stress = json.loads((DATA / "stress_suite_cases.json").read_text(encoding="utf-8"))
    assert stress["deterministic_seed"] == 5052026
    assert "never coerced to zero" in stress["null_policy"]
    assert len(stress["stresses"]) == 15
    assert stress["timestamp_lattice_policy"].startswith("missingness, gaps, and downsampling preserve")
    assert stress["duplicate_policy"] == "exact duplicates collapse; conflicting duplicates become unavailable and are counted"
    with (REPORTS / "robustness_results.csv").open(encoding="utf-8-sig", newline="") as handle:
        robustness = {row["stress_id"]: row for row in csv.DictReader(handle)}
    assert int(robustness["duplicate_conflict"]["actual_duplicate_conflict_count"]) > 0
    assert int(robustness["missing_20pct"]["actual_unavailable_sample_count"]) > 0
    assert int(robustness["missing_20pct"]["actual_total_sample_count"]) > int(robustness["missing_20pct"]["actual_unavailable_sample_count"])
    sensitivity = json.loads((DATA / "sensitivity_grid.json").read_text(encoding="utf-8"))
    assert sensitivity["frozen_weights"] == summary["frozen_weights"]
    assert sensitivity["grid_policy"] == "one parameter at a time; diagnostic only; holdout never retuned"
    profiles = json.loads((DATA / "temporal_meter_profiles.json").read_text(encoding="utf-8"))
    assert set(profiles) == {"B-L-9", "B-L-12", "B-L-13", "B-L-14", "B-L-35"}
    assert all(len(profile["monthly"]) == 3 for profile in profiles.values())
    with (REPORTS / "peak_consistency_forensics.csv").open(encoding="utf-8-sig", newline="") as handle:
        peak = list(csv.DictReader(handle))
    assert len(peak) == 6
    assert sum(row["legacy_v04_peak_consistent"] == "True" for row in peak) == 2
    assert sum(row["adjudicated_peak_consistent"] == "True" for row in peak) == 6
    assert all(row["primary_cause"] == "AGGREGATION_DEFINITION" for row in peak)
    assert all(row["context_join"] == "none" for row in peak)
    manifest = json.loads((REPORTS / "reproducibility_manifest.json").read_text(encoding="utf-8"))
    for relative, digest in manifest["output_hashes"].items():
        assert sha256(ROOT / relative) == digest, f"output hash drift: {relative}"
    for note in ("sol_goal_orchestrator.md", "terra_causal_methodology.md", "terra_ami_forensics.md", "luna_operations_economics.md"):
        assert (ROOT / "docs" / "agent_learning" / note).is_file()
    print("v0.5 artifact integrity: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
