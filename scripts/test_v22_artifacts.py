#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "lightguard_v0_1" / "data" / "validation" / "v22" / "v22_regional_evidence.json"
data = json.loads(path.read_text(encoding="utf-8"))
regions = data["regions"]
assert set(regions) == {"YANGJU", "MICHUHOL", "DAEJEON", "GANGNEUNG"}
assert regions["YANGJU"]["metrics"]["events"] == 11892
assert 0 < regions["YANGJU"]["metrics"]["repeat"]["90"]["share"] < 1
assert regions["MICHUHOL"]["metrics"]["complete_months"] == 34
assert 0 < regions["MICHUHOL"]["metrics"]["iot_share_of_recorded_work"] < 1
assert regions["DAEJEON"]["metrics"]["valid_coordinate_coverage"] == 1
assert regions["DAEJEON"]["metrics"]["decision"].endswith("GAPS")
assert regions["GANGNEUNG"]["metrics"]["unique_cabinet_keys"] == 339
assert regions["GANGNEUNG"]["metrics"]["rated_capacity_row_coverage"] > 0.99
assert data["evidence_architecture"]["same_model_nationwide_claim"] is False
assert data["evidence_architecture"]["new_predictive_tuning"] == 0
for item in regions.values():
    assert "raw_rows" not in item
    assert "record_values" not in item
    assert set(item) == {"manifest", "metrics"}
print("v22 artifact contract: PASS")
