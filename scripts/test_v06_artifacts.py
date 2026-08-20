#!/usr/bin/env python3
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1" / "data" / "validation" / "v06"
REPORTS = ROOT / "lightguard_v0_1" / "reports" / "v06"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    with (REPORTS / "coverage_uncertainty.csv").open(encoding="utf-8-sig", newline="") as handle:
        intervals = {row["stress_id"]: row for row in csv.DictReader(handle)}
    assert float(intervals["baseline"]["coverage_point"]) == 1.0
    assert 0.60 < float(intervals["baseline"]["wilson_95_lower"]) < 0.62
    assert float(intervals["gap_120m"]["coverage_point"]) == 0.0
    assert 0.38 < float(intervals["gap_120m"]["wilson_95_upper"]) < 0.40

    bootstrap = json.loads((DATA / "stationary_bootstrap.json").read_text(encoding="utf-8"))
    assert bootstrap["seed"] == 6062026
    assert bootstrap["replicates"] == 2000
    assert bootstrap["expected_block_days"] == 7
    assert bootstrap["candidate_density_95_lower"] <= bootstrap["candidate_density_point"] <= bootstrap["candidate_density_95_upper"]

    with (REPORTS / "factorial_design.csv").open(encoding="utf-8-sig", newline="") as handle:
        design = list(csv.DictReader(handle))
    with (REPORTS / "interaction_effects.csv").open(encoding="utf-8-sig", newline="") as handle:
        effects = list(csv.DictReader(handle))
    assert len(design) == 16
    assert len(effects) == 40
    assert all(row["promotion_policy"] == "diagnostic_only_no_retuning" for row in design)

    policy = json.loads((DATA / "abstention_policy.json").read_text(encoding="utf-8"))
    assert any("120" in row["condition"] and row["decision"] == "DATA_INSUFFICIENT" for row in policy["rules"])
    assert "coerce null to zero" in policy["never_do"]
    schema = json.loads((DATA / "field_outcome_schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["inspector_blinded_to_score"]["const"] is True
    assert "unable_to_adjudicate" in schema["properties"]["outcome"]["enum"]
    summary = json.loads((DATA / "v06_evidence_summary.json").read_text(encoding="utf-8"))
    assert summary["field_truth"] == {"available": False, "schema_ready": True, "blinded_adjudication_required": True}
    assert summary["interaction_diagnostic"]["frozen_configuration_changed"] is False

    manifest = json.loads((REPORTS / "reproducibility_manifest.json").read_text(encoding="utf-8"))
    for relative, expected in manifest["output_hashes"].items():
        assert digest(ROOT / relative) == expected, f"output hash drift: {relative}"
    print("v0.6 evidence hardening integrity: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
