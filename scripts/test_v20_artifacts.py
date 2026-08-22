#!/usr/bin/env python3
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1" / "data" / "validation" / "v20"
REPORT = ROOT / "lightguard_v0_1" / "reports" / "v20"
U1_SHA = "d0e3fecb06577d53b86cba5bf294b745559c2412e3f3b8965b69cb50d497d9fb"
U2_SHA = "a060cf2f289274b62ea1578704b8673920a02cfb54f2232171482384266790fb"
HISTORICAL_APP_PATH = "lightguard_app/lib/features/ami_validation/municipal_operations_evidence_card.dart"
HISTORICAL_APP_SHA = "8827bd178c6816b1aad300988840e4e0e664094b9f22e179f32918d9b3345a89"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    required = [
        DATA / "v20_ulsan_u1_manifest.json", DATA / "v20_ulsan_u2_manifest.json",
        DATA / "v20_u1_u2_join_summary.json", DATA / "v20_asset_spatial_summary.json",
        DATA / "v20_feature_availability_contract.json", DATA / "v20_frozen_common_ops_model.json",
        DATA / "v20_zero_shot_summary.json", DATA / "v20_lifecycle_summary.json",
        DATA / "v20_queue_replay_summary.json", DATA / "v20_artifact_manifest.json",
        REPORT / "v20_independent_audit.md", REPORT / "v20_final_summary.md",
    ]
    assert all(p.is_file() for p in required), "missing required v0.20 artifact"
    u1 = json.loads(required[0].read_text())
    assert u1["sha256"] == U1_SHA and u1["physical_row_count"] == 2233
    assert u1["structurally_empty_row_count"] == 1173 and u1["canonical_event_count"] == 1060
    u2 = json.loads(required[1].read_text())
    assert u2["sha256"] == U2_SHA and u2["local_source_status"] == "AVAILABLE_VERIFIED"
    assert u2["physical_row_count"] == 17061 and u2["ambiguous_identifier_count"] == 101
    join = json.loads(required[2].read_text())
    assert join["join_status"] == "PARTIAL_VERIFIED_EXACT_ID"
    assert join["safe_matched_asset_count"] == 920 and join["safe_matched_event_count"] == 994
    assert join["ambiguous_u2_match_asset_count"] == 13 and join["unmatched_asset_count"] == 48
    assert join["category_conflict_event_count"] == 0 and join["row_multiplication_count"] == 0
    spatial = json.loads(required[3].read_text())
    assert spatial["all_u2_coordinate_valid_count"] == 17061 and not spatial["raw_coordinates_exported"]
    contract = json.loads(required[4].read_text())
    assert not contract["ulsan_retuning_allowed"] and "work_start_date" in contract["blocked_features"]
    model = json.loads(required[5].read_text())
    assert model["retuning_count"] == 0 and model["decision_timestamp"] == "BEFORE_ULSAN_OUTCOME_CONSTRUCTION"
    zero = json.loads(required[6].read_text())
    assert zero["external"]["ulsan_retuning_count"] == 0 and zero["external"]["transfer_grade"] in {"TM-A", "TM-B", "TM-C", "TM-X"}
    queue = json.loads(required[8].read_text())
    assert queue["capacity_interpretation"] == "NOT_EVALUABLE_AS_STAFFING_CAPACITY"
    assert queue["same_day_order"] == "NOT_SUPPORTED" and queue["causal_claim"] == "NOT_SUPPORTED"
    manifest = json.loads(required[9].read_text())
    for item in manifest["artifacts"]:
        if item["path"] == HISTORICAL_APP_PATH:
            # Preserve the v0.20 integration hash in the historical manifest,
            # while allowing later regional releases to evolve the shared UI.
            assert item["sha256"] == HISTORICAL_APP_SHA
            assert (ROOT / item["path"]).is_file()
            continue
        assert sha(ROOT / item["path"]) == item["sha256"], item["path"]
    raw_sources = [next(p for p in (ROOT / "official_docs").rglob("*") if p.is_file() and sha(p) == expected) for expected in (U1_SHA, U2_SHA)]
    source = []
    for raw in raw_sources:
        with raw.open(encoding="cp949", newline="") as f:
            source.extend(csv.DictReader(f))
    forbidden = {v.strip() for r in source for key in ("관리번호", "작업내용", "주소") if len((v := r.get(key, "")).strip()) >= 8}
    public_text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for base in (DATA, REPORT, ROOT / "lightguard_app" / "docs") for p in base.rglob("*") if p.is_file())
    assert not any(value in public_text for value in forbidden), "raw identifier/work text leaked"
    assert "PARTIAL_VERIFIED" in public_text and "NOT_EVALUABLE" in public_text and "NOT_SUPPORTED" in public_text
    print("v0.20 artifact contract: PASS")


if __name__ == "__main__":
    main()
