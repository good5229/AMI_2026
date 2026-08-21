#!/usr/bin/env python3
import csv
import subprocess

from v16_common import DATA, REPORT, ROOT, load_json, require


def read(path):
    with path.open(newline="", encoding="utf-8") as stream: return list(csv.DictReader(stream))


def main() -> None:
    assets = load_json(DATA / "v16_asset_scope_registry.json")
    freeze = load_json(DATA / "v16_protocol_freeze.json")
    holdout = load_json(DATA / "v16_service_holdout_manifest.json")
    results = read(DATA / "v16_service_policy_results.csv")
    utility = read(REPORT / "v16_paired_service_utility.csv")
    shadow = read(DATA / "v16_natural_shadow.csv")
    require(assets["official_asset_count"] == 129 and assets["streetlight_eligible_count"] == 5 and assets["out_of_scope_count"] == 124, "BLOCKED_SCOPE_CONTRACT")
    require(freeze["h1_threshold_retuned"] is False and freeze["selection_uses_outcome"] is False and freeze["inferential_statistics_permitted"] is False, "BLOCKED_OUTCOME_TUNING")
    require(holdout["v10_overlap_count"] == holdout["canonical_overlap_count"] == 0 and holdout["v15_reused_pair_count"] == 71 and holdout["b_l_12_extension_count"] >= 5 and holdout["independent_validation"] is False, "BLOCKED_REPLAY_CONTRACT")
    require(holdout["one_operator_per_meter_day"] and not holdout["selection_uses_outcome"], "BLOCKED_HOLDOUT_SELECTION")
    require(results and all(row["status"] == "OK" and row["threshold_same"].lower() == "true" for row in results), "BLOCKED_POLICY_RESULT")
    policies = {(row["pair_id"], row["policy"]) for row in results}
    require(all((pair["pair_id"], policy) in policies for pair in holdout["pairs"] for policy in ("P0_COLLAPSED_NON_NORMAL", "P1_GUARDED_LANES")), "BLOCKED_MISSING_POLICY_PAIR")
    expected = {row["meter_id"]: row["expected_phase_count"] for row in assets["eligible_assets"]}
    require(sum(value == 1 for value in expected.values()) == 2 and sum(value == 3 for value in expected.values()) == 3, "BLOCKED_PHASE_SCOPE")
    require({row["meter_id"] for row in results if row["policy"] == "P1_GUARDED_LANES"} == set(expected), "BLOCKED_SERVICE_COVERAGE")
    require({row["endpoint"] for row in utility} == {"R", "B"} and all(int(row["pairs"]) > 0 for row in utility), "BLOCKED_PRIMARY_STATISTICS")
    require(all(row["analysis_status"] == "POST_HOC_DESCRIPTIVE_ONLY" for row in utility), "BLOCKED_INFERENTIAL_OVERCLAIM")
    require(not {"truth", "accuracy", "fpr", "specificity", "fault_probability", "recovery"}.intersection(shadow[0]), "BLOCKED_NATURAL_SHADOW_CLAIM")
    report = (REPORT / "v16_final_summary.md").read_text(encoding="utf-8")
    audit = (REPORT / "v16_internal_artifact_audit.md").read_text(encoding="utf-8")
    for phrase in ("Business fit", "Development feasibility", "Idea specificity and completeness", "Use purpose and tangible effect", "Generality", "Independent validation: false", "Required prospective confirmatory experiment", "No independent validation"):
        require(phrase in report, "BLOCKED_COMPETITION_ALIGNMENT")
    require("Artifact and build contract: `PASS`" in audit and "Experimental prospective targets: `FAIL`" in audit and "Independent validation: `NO`" in audit, "BLOCKED_AUDIT_VERDICT")
    tracked = subprocess.run(["git", "ls-files", "official_docs", "harness_docs", ".env"], cwd=ROOT, text=True, capture_output=True, check=True).stdout
    require(not tracked.strip(), "BLOCKED_FORBIDDEN_TRACKED_INPUT")
    print("v0.16 artifact contract PASS")


if __name__ == "__main__":
    main()
