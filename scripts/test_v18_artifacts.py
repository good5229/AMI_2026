#!/usr/bin/env python3
import csv
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1" / "data" / "validation" / "v18"
REPORT = ROOT / "lightguard_v0_1" / "reports" / "v18"


def require(condition, code):
    if not condition:
        raise RuntimeError(code)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    freeze = load_json(DATA / "v17_freeze_manifest.json")
    split = load_json(DATA / "v18_temporal_split.json")
    config = load_json(DATA / "v18_model_config.json")
    manifest = load_json(DATA / "v18_artifact_manifest.json")
    require(freeze["status"] == "FROZEN_UNMODIFIED" and freeze["operational_need_grade"] == "ON-A", "BLOCKED_V17_FREEZE")
    for item in freeze["files"]:
        require(digest(ROOT / item["path"]) == item["sha256"], "BLOCKED_V17_MUTATION")
    require(split["primary_outcome"] == "REPEAT_WITHIN_30D" and split["confirmatory"]["end"] == "2025-07-10", "BLOCKED_PRIMARY_CENSORING")
    require(split["development"]["end"] == "2023-12-01" and split["validation"]["end"] == "2024-12-01", "BLOCKED_EMBARGO")
    require(split["development"]["end"] < split["validation"]["start"] < split["confirmatory"]["start"], "BLOCKED_TEMPORAL_ORDER")
    require(split["confirmatory_frozen_before_scoring"] is True, "BLOCKED_HOLDOUT_FREEZE")
    require(config["candidate_limit"] <= 2 and config["holdout_refit_count"] == 0, "BLOCKED_MODEL_SEARCH")
    require(config["asset_id_memorization"] is False and config["same_day_order_feature"] is False, "BLOCKED_ID_OR_ORDER")
    require(config["capacity"]["C25"] == 0 and config["capacity"]["C25_status"] == "NONREVIEWING_SCENARIO", "BLOCKED_ZERO_CAPACITY_DISCLOSURE")
    require(config["capacity"]["staffing_parameter_count"] == config["capacity"]["service_duration_parameter_count"] == 0, "BLOCKED_STAFFING_INVENTION")
    banned = set(config["banned_features"])
    require(not banned.intersection(config["model_input_features"]), "BLOCKED_BANNED_FEATURE")
    features = []
    with (DATA / "v18_event_feature_table.csv").open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            require(row["same_day_order_used"] == "False", "BLOCKED_SAME_DAY_ORDER")
            receipt = row["receipt_date"]
            require(not row["max_prior_receipt_date"] or row["max_prior_receipt_date"] < receipt, "BLOCKED_RECEIPT_LEAKAGE")
            require(not row["max_prior_completion_date"] or row["max_prior_completion_date"] < receipt, "BLOCKED_COMPLETION_LEAKAGE")
            features.append(row)
    require(len(features) == 101843, "BLOCKED_FEATURE_ROW_COUNT")
    same_day = defaultdict(list)
    comparison_columns = [
        "prior_event_count_30d", "prior_event_count_90d", "prior_event_count_365d",
        "days_since_previous_event", "days_since_previous_event_missing",
        "prior_long_resolution_count_3d", "prior_long_resolution_count_7d",
        "currently_open_prior_case_count", "oldest_open_prior_age_days",
        "start_of_day_open_backlog", "recent_7d_system_intake", "recent_30d_system_intake",
        "max_prior_receipt_date", "max_prior_completion_date", "same_day_order_used",
    ]
    for row in features:
        same_day[(row["asset_hash_audit_only_not_model_feature"], row["receipt_date"])].append(row)
    for rows in same_day.values():
        if len(rows) > 1:
            require(all(tuple(row[name] for name in comparison_columns) == tuple(rows[0][name] for name in comparison_columns) for row in rows), "BLOCKED_SAME_DAY_FEATURE_DRIFT")
    outcomes = list(csv.DictReader((DATA / "v18_outcome_table.csv").open(encoding="utf-8", newline="")))
    require(len(outcomes) == 101843, "BLOCKED_OUTCOME_ROW_COUNT")
    require(all(row["repeat_within_30d_evaluable"] == "False" for row in outcomes if row["receipt_date"] > "2025-07-10"), "BLOCKED_RIGHT_CENSORING")
    scores = list(csv.DictReader((DATA / "v18_confirmatory_scores.csv").open(encoding="utf-8", newline="")))
    require(len(scores) == split["confirmatory"]["episodes"] and all(row["direct_ami_validation"] == "False" for row in scores), "BLOCKED_CONFIRMATORY_SCORE")
    queue = list(csv.DictReader((DATA / "v18_queue_simulation.csv").open(encoding="utf-8", newline="")))
    require(queue and all(row["tie_order_is_actual"] == "False" and "not repair completion" in row["interpretation"] for row in queue), "BLOCKED_QUEUE_WORDING")
    report = (REPORT / "v18_final_summary.md").read_text(encoding="utf-8")
    audit = (REPORT / "v18_independent_audit.md").read_text(encoding="utf-8")
    for phrase in ("REPEAT_WITHIN_30D", "C25=0", "simulated time-to-review", "Direct AMI validation: `NO`", "Claims Prohibited"):
        require(phrase in report, "BLOCKED_FINAL_REPORT")
    require("Same-day order invention: `NO`" in audit and "Daegu-to-Suyeong performance transfer: `NO`" in audit, "BLOCKED_INDEPENDENT_AUDIT")
    card = (ROOT / "lightguard_app" / "lib" / "features" / "ami_validation" / "v18_operational_triage_card.dart").read_text(encoding="utf-8")
    for phrase in ("REMOTE_REVIEW_CANDIDATE", "고장 확률", "실제 수리시간 단축", "대구→수영구"):
        require(phrase in card, "BLOCKED_FLUTTER_BOUNDARY")
    for item in manifest["artifacts"]:
        require(digest(ROOT / item["path"]) == item["sha256"], "BLOCKED_ARTIFACT_DRIFT")
    tracked = subprocess.run(["git", "ls-files", "official_docs", "harness_docs", ".env"], cwd=ROOT, text=True, capture_output=True, check=True).stdout
    require(not tracked.strip(), "BLOCKED_FORBIDDEN_TRACKED_INPUT")
    print("v0.18 artifact contract PASS")


if __name__ == "__main__":
    main()
