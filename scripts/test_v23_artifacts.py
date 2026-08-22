#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "lightguard_v0_1" / "data" / "validation" / "v23" / "v23_regional_file_evidence.json"
data = json.loads(path.read_text(encoding="utf-8"))
regions = data["regions"]

assert data["decision"] == "MEANINGFUL_WITH_ASSET_ROLE_ONLY"
assert set(regions) == {"SEONGNAM", "CHUNGJU", "GUNPO", "TONGYEONG"}
assert {key: item["metrics"]["records"] for key, item in regions.items()} == {
    "SEONGNAM": 826,
    "CHUNGJU": 871,
    "GUNPO": 250,
    "TONGYEONG": 4025,
}
assert regions["SEONGNAM"]["metrics"]["positive_pole_count_coverage"] > 0.9
assert regions["CHUNGJU"]["metrics"]["valid_coordinate_coverage"] > 0.9
assert regions["GUNPO"]["metrics"]["valid_coordinate_coverage"] > 0.9
assert regions["TONGYEONG"]["metrics"]["cabinet_id_coverage"] > 0.9
assert data["evidence_architecture"]["municipal_regions_total"] == 11
assert data["evidence_architecture"]["new_predictive_tuning"] == 0
assert data["evidence_architecture"]["same_model_nationwide_claim"] is False
assert data["evidence_architecture"]["raw_values_exported"] is False
for item in regions.values():
    assert set(item) == {"manifest", "metrics"}
    assert item["manifest"]["tracked_in_git"] is False
    assert "raw_rows" not in item and "addresses" not in item and "coordinates" not in item
    raw = ROOT / "official_docs" / "external_data" / item["manifest"]["filename"]
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", str(raw)], cwd=ROOT, check=False
    )
    assert ignored.returncode == 0
print("v23 artifact contract: PASS")
