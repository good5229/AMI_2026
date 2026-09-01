#!/usr/bin/env python3
import json
import importlib.util
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

builder_path = ROOT / "scripts" / "build_v24_nationwide_census.py"
spec = importlib.util.spec_from_file_location("build_v24_nationwide_census", builder_path)
assert spec and spec.loader
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
assert builder.region_from_title("부산광역시 남구_가로등현황")["region"] == "부산광역시 남구"
assert builder.region_from_title("울산광역시 중구_가로등현황")["region"] == "울산광역시 중구"
assert builder.region_from_title("전남광주통합특별시 동구_가로등현황")["region"] == "전남광주통합특별시 동구"
assert builder.region_from_title("부산광역시_도로조명시스템 현황")["region"] == "부산광역시"
assert builder.region_from_title("대구공공시설관리공단_가로등관리")["region"] == "대구광역시"

for item in data["datasets"]:
    assert "content_url" not in item and "external_url" not in item
    assert "header" not in item and "raw_rows" not in item and "coordinates" not in item
    if item.get("acquisition_status") == "DOWNLOADED_ANALYZABLE":
        assert item["roles"] and item["rows"] > 0 and item["sha256"]
        raw = ROOT / "official_docs" / "external_data" / "nationwide_v24" / item["raw_filename"]
        assert raw.exists()
        assert subprocess.run(["git", "check-ignore", "-q", str(raw)], cwd=ROOT).returncode == 0
print("v24 nationwide census artifact contract: PASS")
