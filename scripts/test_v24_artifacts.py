#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "lightguard_v0_1" / "data" / "validation" / "v24" / "v24_nationwide_file_census.json"
data = json.loads(path.read_text(encoding="utf-8"))

assert data["version"] == "0.24"
assert data["unique_candidates"] >= data["analyzable_datasets"] > 0
assert data["analyzable_region_count"] > 0
assert len(data["represented_top_level_regions"]) > 0
assert data["raw_values_exported"] is False
assert data["new_predictive_tuning"] == 0
assert "nationwide AMI accuracy" in data["claim_boundary"]
assert set(data["role_counts"]) == {"SIGNAL", "OPERATIONS", "CABINET", "LOAD", "SPATIAL", "ASSET"}
for item in data["datasets"]:
    assert "content_url" not in item and "external_url" not in item
    assert "header" not in item and "raw_rows" not in item and "coordinates" not in item
    if item.get("acquisition_status") == "DOWNLOADED_ANALYZABLE":
        assert item["roles"] and item["rows"] > 0 and item["sha256"]
        raw = ROOT / "official_docs" / "external_data" / "nationwide_v24" / item["raw_filename"]
        assert raw.exists()
        assert subprocess.run(["git", "check-ignore", "-q", str(raw)], cwd=ROOT).returncode == 0
print("v24 nationwide census artifact contract: PASS")
