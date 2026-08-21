#!/usr/bin/env python3
import csv
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1" / "data" / "validation" / "v17"
REPORT = ROOT / "lightguard_v0_1" / "reports" / "v17"


def require(condition, code):
    if not condition:
        raise RuntimeError(code)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    freeze = load_json(DATA / "v16_freeze_manifest.json")
    sources = load_json(DATA / "v17_source_manifest.json")
    summary = load_json(DATA / "v17_operational_summary.json")
    require(freeze["status"] == "FROZEN_UNMODIFIED" and freeze["policy_promotion"] == "STOPPED", "BLOCKED_V16_FREEZE")
    for item in freeze["files"]:
        require(sha256(ROOT / item["path"]) == item["sha256"], "BLOCKED_V16_MUTATION")
    require({row["source_id"] for row in sources} == {"D1", "D2", "D3", "D4", "D5"}, "BLOCKED_SOURCE_SET")
    require(all(len(row["sha256"]) == 64 and row["snapshot_type"] == "latest_local_complete_snapshot_canonical" for row in sources), "BLOCKED_PROVENANCE")
    require(summary["fault_management"]["rows"] == 101843 and summary["fault_management"]["unique_assets"] == 40148, "BLOCKED_D1_PROFILE")
    require(summary["fault_management"]["negative_resolution_rows"] == 4 and summary["fault_management"]["unresolved_rows"] == 0, "BLOCKED_DURATION_QUALITY")
    require(summary["spatial_join"]["status"] == "PARTIAL_JOIN", "BLOCKED_JOIN_VERDICT")
    require(summary["spatial_join"]["ambiguous_unique_ids"] == 137 and summary["spatial_join"]["unmatched_unique_ids"] == 174, "BLOCKED_JOIN_EXCLUSIONS")
    require(summary["spatial_join"]["unambiguous_join_candidate_event_rows"] == 100561, "BLOCKED_JOIN_CANDIDATE_SCOPE")
    require(summary["spatial_join"]["spatial_analysis_status"] == "NO_SPATIAL_JOIN", "BLOCKED_SPATIAL_GATE")
    require(summary["repeat_events"]["assets_with_repeats"] == 23815, "BLOCKED_REPEAT_ANALYSIS")
    require(summary["repeat_events"]["same_asset_same_day_extra_records"] == 848, "BLOCKED_SAME_DAY_COLLAPSE")
    require(summary["safety_inspection"]["measurement_policy"].startswith("DESCRIPTIVE_ONLY"), "BLOCKED_SAFETY_THRESHOLD")
    require(summary["maintenance"]["material_row_count_status"] == "MISMATCH_REQUIRES_SOURCE_CONFIRMATION", "BLOCKED_D4_MISMATCH_DISCLOSURE")
    require(summary["maintenance"]["material_analysis_status"] == "HOLD_PROFILE_ONLY", "BLOCKED_D4_HOLD")
    require(summary["maintenance"]["cost_savings_permitted"] is False, "BLOCKED_COST_CLAIM")
    require(summary["operational_need_grade"] == "ON-A", "BLOCKED_OPERATIONAL_GRADE")
    with (DATA / "v17_fault_events_clean.csv").open(encoding="utf-8", newline="") as stream:
        fault_rows = sum(1 for _ in csv.DictReader(stream))
    with (DATA / "v17_safety_inspection_clean.csv").open(encoding="utf-8", newline="") as stream:
        safety_rows = sum(1 for _ in csv.DictReader(stream))
    require(fault_rows == 101843 and safety_rows == 105449, "BLOCKED_CLEAN_ROW_COUNT")
    report = (REPORT / "v17_final_summary.md").read_text(encoding="utf-8")
    audit = (REPORT / "v17_independent_audit.md").read_text(encoding="utf-8")
    for phrase in ("ON-A", "PARTIAL_JOIN", "NO_SPATIAL_JOIN", "Daegu supports operational need only", "No event join key", "국민체감", "범용성"):
        require(phrase in report, "BLOCKED_FINAL_REPORT")
    require("Artifact and claim contract: `PASS`" in audit and "Cost savings calculated: `NO`" in audit, "BLOCKED_CLAIM_AUDIT")
    dart = (ROOT / "lightguard_app" / "lib" / "features" / "ami_validation" / "v17_municipal_operations_card.dart").read_text(encoding="utf-8")
    for phrase in ("101,843", "40,148", "PARTIAL_JOIN", "100,561", "AMI와 직접 연결되지 않음", "비용절감"):
        require(phrase in dart, "BLOCKED_FLUTTER_DISCLOSURE")
    tracked = subprocess.run(["git", "ls-files", "official_docs", "harness_docs", ".env"], cwd=ROOT, text=True, capture_output=True, check=True).stdout
    require(not tracked.strip(), "BLOCKED_FORBIDDEN_TRACKED_INPUT")
    print("v0.17 artifact contract PASS")


if __name__ == "__main__":
    main()
