#!/usr/bin/env python3
"""Audit suitability before any v0.14 outcome execution and freeze v0.13."""
from __future__ import annotations

from v14_common import CLAIM, DATA, V13_REPORTS, frozen, load_json, require, sha256, write_json


def main() -> None:
    registry = load_json(DATA / "v14_dataset_registry.json")
    records = registry.get("records", [])
    require(len(records) == 4, "exactly four candidate records required")
    decisions = {row["dataset_id"]: row for row in records}
    require(any("CODEX" in key and row.get("suitability_grade") in {"SG-A", "SG-B"} for key, row in decisions.items()), "CoDEx is not eligible")
    require(any("THREEPHASE" in key and row.get("suitability_grade") == "SG-X" for key, row in decisions.items()), "3PhaseInsight must remain reference-only")
    for name in ("v14_physical_feature_mapping.json", "v14_track_a_config.json", "v14_track_b_config.json", "v14_track_c_config.json"):
        frozen(DATA / name)
    predecessor = V13_REPORTS / "reproducibility_manifest.json"
    v13 = load_json(predecessor)
    require(v13.get("primary_gate") == "NOT_EVALUABLE_INCOMPLETE_COVERAGE", "v0.13 primary result changed")
    write_json(DATA / "v13_freeze_manifest.json", {
        "schema_version": "lightguard.v14.v13-freeze.1", "status": "FROZEN_NEGATIVE_NON_EVALUABLE",
        "claim_boundary": CLAIM, "path": str(predecessor.relative_to(predecessor.parents[3])),
        "sha256": sha256(predecessor), "primary_gate": v13["primary_gate"],
        "mad_sc3_balanced_accuracy": 0.52004485, "z_score_balanced_accuracy": 0.66598258,
        "external_empirical_grade": "NO_EV_GRADE_NOT_EVALUABLE",
    })
    print("v0.14 suitability and v0.13 freeze PASS")


if __name__ == "__main__":
    main()

