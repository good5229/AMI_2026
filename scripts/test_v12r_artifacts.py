#!/usr/bin/env python3
"""Validate v0.12R literature, evidence, blindness, and claim contracts."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v12r"
REPORTS = ROOT / "lightguard_v0_1/reports/v12r"


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def main() -> None:
    required = [
        DATA / "v11_freeze_manifest.json", DATA / "v12r_reference_registry.json",
        DATA / "v12r_literature_evidence_matrix.csv", DATA / "v12r_case_evidence_matrix.csv",
        DATA / "v12r_review_manifest.json", DATA / "v12r_review_results.csv",
        DATA / "v12r_consensus_labels.csv",
        REPORTS / "v12r_literature_search_protocol.md", REPORTS / "v12r_literature_search_log.csv",
        REPORTS / "v12r_domain_evidence_review.md", REPORTS / "v12r_claim_evidence_matrix.md",
        REPORTS / "v12r_canonical_six_evidence.md", REPORTS / "v12r_review_protocol.md",
        REPORTS / "v12r_blindness_audit.md", REPORTS / "v12r_human_review_analysis.md",
        REPORTS / "v12r_final_summary.md", REPORTS / "reproducibility_manifest.json",
    ]
    require(all(path.exists() and path.stat().st_size > 0 for path in required), "required v12r artifact missing")
    freeze = json.loads((DATA / "v11_freeze_manifest.json").read_text())
    require(freeze["v11_release_commit"] == "b25b168250ede29b5c5bbcadab918c455d61ba74", "v11 release changed")
    require(all(sha(ROOT / item["path"]) == item["sha256"] for item in freeze["files"]), "v11 frozen file changed")
    protocol = freeze["literature_search_protocol"]
    require(protocol["frozen_before_screening"] and sha(ROOT / protocol["path"]) == protocol["sha256"], "search protocol freeze invalid")

    registry = json.loads((DATA / "v12r_reference_registry.json").read_text())
    require(len(registry) == 21 and len({row["source_id"] for row in registry}) == 21, "reference registry count/identity failed")
    require(sum(row["quality_grade"] == "A" for row in registry) == 19, "A-grade count changed")
    require(all(row["URL"].startswith("https://") and row["quality_grade"] in ("A", "B") for row in registry), "registry URL/quality invalid")
    matrix = rows(DATA / "v12r_literature_evidence_matrix.csv")
    require(len({row["source_id"] for row in matrix}) == 21, "matrix registry mismatch")
    require({row["support_grade"] for row in matrix} <= {"L0", "L1", "L2", "L3"}, "invalid support grade")
    require(any(row["support_grade"] == "L0" for row in matrix), "null/limitation evidence was hidden")
    require(all(row["prohibited_claim"].strip() for row in matrix), "prohibited claim boundary missing")
    require(all("confirmed fault" not in row["allowed_claim"].lower() and "fault probability" not in row["allowed_claim"].lower() for row in matrix), "allowed claim overstates literature")

    cases = rows(DATA / "v12r_case_evidence_matrix.csv")
    require(len(cases) == 765, "proxy-high literature mapping changed")
    by_pattern = {}
    for row in cases:
        by_pattern.setdefault(row["pattern_id"], set()).add(row["literature_evidence_grade"])
    require(all(len(grades) == 1 for grades in by_pattern.values()), "literature grade depends on detector outcome")
    require(all(row["field_confirmation"] == "unavailable" for row in cases), "field confirmation fabricated")

    review = json.loads((DATA / "v12r_review_manifest.json").read_text())
    require(review["human_review_status"] == "HUMAN_REVIEW_PENDING", "human review status overstated")
    require(review["selected"] == {"S1_ALGORITHM_LITERATURE": 6, "S2_PROXY_LITERATURE": 18, "S3_SINGLETON_LITERATURE": 18, "S4_MATCHED_RANDOM": 20}, "review strata changed")
    require(len(review["key_rows"]) == 62 and len({row["sample_id"] for row in review["key_rows"]}) == 62, "review packet uniqueness failed")
    packet = (REPORTS / "v12r_blind_review_packet.html").read_text()
    for hidden in ("S1_ALGORITHM", "S2_PROXY", "S3_SINGLETON", "S4_MATCHED", "EVIDENCE_A", "EVIDENCE_B", "canonical", "proxy_family_count"):
        require(hidden not in packet, f"review packet leaks {hidden}")
    require(len(rows(DATA / "v12r_review_results.csv")) == 0 and len(rows(DATA / "v12r_consensus_labels.csv")) == 0, "AI/human labels fabricated")
    require("HUMAN_REVIEW_PENDING" in (REPORTS / "v12r_human_review_analysis.md").read_text(), "pending human analysis boundary missing")

    app = json.loads((ROOT / "lightguard_app/assets/data/context/v12r_literature_summary.json").read_text())
    require(app["sources"] == 21 and app["proxy_high_mapped"] == 765, "app evidence summary mismatch")
    require(app["maximum_current_claim_level"] == 3 and app["fault_probability_available"] is False, "app claim ladder invalid")
    reproducibility = json.loads((REPORTS / "reproducibility_manifest.json").read_text())
    require(all(sha(ROOT / item["path"]) == item["sha256"] for item in reproducibility["files"]), "reproducibility manifest mismatch")
    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    require(not any(path == ".env" or path.startswith("official_docs/") or path.startswith("harness_docs/") for path in tracked), "protected source tracked")
    print(json.dumps({"status": "PASS", "sources": len(registry), "matrix_rows": len(matrix), "proxy_high": len(cases), "review_cases": len(review["key_rows"]), "human_labels": 0}))


if __name__ == "__main__":
    main()
