#!/usr/bin/env python3
import json
import re

from v21_submission_lib import DATA, REPORT, ROOT, SUBMISSION, sha, verify_freezes


def main():
    verify_freezes()
    required_data = ["v21_claim_registry.json", "v21_rubric.json", "v21_evidence_manifest.json", "v21_metric_registry.json"]
    required_reports = ["v21_rubric_mapping.md", "v21_evidence_traceability.md", "v21_judge_red_team.md", "v21_claim_audit.md", "v21_internal_rubric_stress_test.md", "v21_final_readiness.md"]
    required_submission = ["01_one_page_summary.md", "02_problem_evidence.md", "03_solution_architecture.md", "04_validation_evidence.md", "05_municipal_operations_evidence.md", "06_claim_boundaries.md", "07_demo_script.md", "08_judge_qna.md", "evidence_manifest.json"]
    assert all((DATA / name).is_file() for name in required_data)
    assert all((REPORT / name).is_file() for name in required_reports)
    assert all((SUBMISSION / name).is_file() for name in required_submission)
    claims = json.loads((DATA / "v21_claim_registry.json").read_text())
    assert len({c["claim_id"] for c in claims}) == len(claims)
    assert {c["claim_level"] for c in claims} == {"GREEN", "YELLOW", "RED"}
    assert all((ROOT / c["source_file"]).is_file() and sha(ROOT / c["source_file"]) == c["source_hash"] for c in claims)
    assert all(c["qualification"] for c in claims if c["claim_level"] == "YELLOW")
    assert all(not c["allowed"] for c in claims if c["claim_level"] == "RED")
    rubric = json.loads((DATA / "v21_rubric.json").read_text())
    items = rubric["stage_1"] + rubric["stage_2"]
    assert len(items) == 9 and all(r["official_weight"] is None and not r["score_is_official"] for r in items)
    assert all(r["primary_claim_id"] in {c["claim_id"] for c in claims} for r in items)
    qna = (SUBMISSION / "08_judge_qna.md").read_text()
    assert len(re.findall(r"^## Q\d+\.", qna, re.M)) >= 20
    manifest = json.loads((DATA / "v21_evidence_manifest.json").read_text())
    assert manifest["status"] == "SR-A" and manifest["release_snapshot"] == "ARTIFACT_HASH_FREEZE"
    assert manifest["predictive_retuning_count"] == 0 and manifest["privacy"] == "NO_RAW_DATA"
    covered = {artifact["path"] for artifact in manifest["artifacts"]}
    required_release_surfaces = {
        "lightguard_app/README.md",
        "lightguard_app/lib/features/ami_validation/ami_validation_screen.dart",
        "lightguard_app/lib/features/ami_validation/submission_readiness_card.dart",
        "lightguard_app/test/unit/v21_submission_readiness_test.dart",
        "scripts/v21_submission_lib.py",
        "scripts/v21_preflight.sh",
    }
    assert required_release_surfaces <= covered
    for artifact in manifest["artifacts"]:
        assert sha(ROOT / artifact["path"]) == artifact["sha256"], artifact["path"]
    submission_manifest = json.loads((SUBMISSION / "evidence_manifest.json").read_text())
    assert submission_manifest["raw_data_included"] is False and len(submission_manifest["files"]) == 8
    for artifact in submission_manifest["files"]:
        assert sha(ROOT / artifact["path"]) == artifact["sha256"], artifact["path"]
    assert "SR-A" in (REPORT / "v21_final_readiness.md").read_text()
    print("v0.21 submission contract: PASS")


if __name__ == "__main__":
    main()
