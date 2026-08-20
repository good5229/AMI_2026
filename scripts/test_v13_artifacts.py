#!/usr/bin/env python3
"""Fail-closed integrity checks for the v0.13 release contract."""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1" / "data" / "validation" / "v13"
REPORTS = ROOT / "lightguard_v0_1" / "reports" / "v13"
APP = ROOT / "lightguard_app" / "assets" / "data" / "context" / "v13_external_validation_summary.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def empirical_grade(status: str) -> str:
    return {
        "PASS": "EV-A_AUTHOR_SPLIT_LIMITED",
        "FAIL": "NO_EV_GRADE_NOT_SUPPORTED",
        "NOT_EVALUABLE_INCOMPLETE_COVERAGE": "NO_EV_GRADE_NOT_EVALUABLE",
    }[status]


def main() -> None:
    v12 = load(DATA / "v12r_freeze_manifest.json")
    v12_report = ROOT / v12["v12r_reproducibility_manifest"]
    require(v12_report.is_file(), "v12R reproducibility manifest missing")
    require(sha(v12_report) == v12["v12r_reproducibility_manifest_sha256"], "v12R freeze hash mismatch")
    raw = load(DATA / "v13_raw_external_manifest.json")
    seal = load(DATA / "v13_preconfirmatory_config_seal.json")
    threshold = load(DATA / "v13_mad_threshold_seal.json")
    require(raw["phase"] == "PRE_CONFIRMATORY", "raw manifest phase changed")
    require(seal["phase"] == "PRE_CONFIRMATORY" and threshold["phase"] == "PRE_CONFIRMATORY", "pre-test seals invalid")
    require(raw["datasets"]["MAD"]["mad_npz_sha256"] == seal["input_sha256"]["raw_mad_npz"], "raw MAD/seal hash mismatch")
    require(threshold["raw_mad_npz_sha256"] == seal["input_sha256"]["raw_mad_npz"], "threshold/raw hash mismatch")
    require(seal["lg_s3_status"] == "UNAVAILABLE_NORMALIZATION_PROVENANCE", "LG-S3 gate weakened")
    require(raw["datasets"]["MAD"]["track_b"] == "NOT_ASSESSABLE", "Track B improperly enabled")
    mad, refit, ucr = rows(REPORTS / "v13_mad_confirmatory_results.csv"), rows(REPORTS / "v13_refit_results.csv"), rows(REPORTS / "v13_ucr_results.csv")
    primary = [row for row in mad if row.get("candidate") == "SC3 primary gate"]
    require(len(primary) == 1 and primary[0].get("status") in {"PASS", "FAIL", "NOT_EVALUABLE_INCOMPLETE_COVERAGE"}, "primary gate missing or dishonest")
    require(all(not row.get("status", "").startswith("PRE_CONFIRMATORY") for row in mad + refit + ucr), "result placeholder remains after execution")
    require(all(row.get("status", "").startswith("BLOCKED") for row in refit), "REFIT block weakened")
    require(all(row.get("status") == "WITHHELD_LICENSE_UNKNOWN" for row in ucr), "UCR licence-withheld gate weakened")
    registry = load(DATA / "v13_external_dataset_registry.json")
    pseudo = next(record for record in registry["records"] if "PSEUDO" in record["dataset_id"])
    require(pseudo["included_primary"] is False and pseudo["included_secondary"] is False, "pseudo-label exclusion weakened")
    canonical = rows(DATA / "v13_case_evidence_matrix.csv")
    expected_fields = ["event_id", "pattern", "literature_grade", "external_empirical_grade", "H1_action", "proxy_grade", "human_review_if_any", "field_confirmation", "final_claim"]
    require(len(canonical) == 6 and list(canonical[0]) == expected_fields, "canonical-six CSV schema mismatch")
    forbidden = {"probability", "accuracy", "recall", "precision", "fpr", "specificity"}
    require(not (forbidden & {key.lower() for key in canonical[0]}), "canonical CSV contains prohibited metric/probability column")
    app = load(APP)
    require(app["external_ev_grade"] == empirical_grade(primary[0]["status"]), "app empirical grade differs from truthful result mapping")
    require(app["human_review_status"] == "PENDING", "human review state changed")
    require(app["streetlight_field_accuracy_available"] is False and app["actual_fault_probability_available"] is False, "streetlight claim gate weakened")
    require(app["primary_dataset"]["status"] == primary[0]["status"], "app primary status differs from result CSV")
    require([entry["id"] for entry in app["signal_mechanisms"]] == ["LG-S1", "LG-S2", "LG-S3", "LG-S4", "LG-S5"], "app signal mechanism contract changed")
    require(app["signal_mechanisms"][2]["external_ev_grade"] == "UNAVAILABLE_NORMALIZATION_PROVENANCE", "LG-S3 availability changed")
    reproducibility = load(REPORTS / "reproducibility_manifest.json")
    for item in reproducibility["files"]:
        path = ROOT / item["path"]
        require(path.is_file() and sha(path) == item["sha256"], f"reproducibility hash mismatch: {item['path']}")
    tracked = subprocess.run(["git", "ls-files", "official_docs/external_benchmarks"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    require(not tracked, "raw external benchmark data must remain untracked")
    print("v0.13 artifact contract PASS")


if __name__ == "__main__":
    main()
