#!/usr/bin/env python3
"""Contract checks for committed v0.7 regional-seasonal artifacts."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v07"
REPORTS = ROOT / "lightguard_v0_1/reports/v07"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    context = load(DATA / "regional_seasonal_context_2025.json")
    cases = load(DATA / "regional_seasonal_cases.json")["cases"]
    summary = load(DATA / "regional_seasonal_summary.json")
    assert len(context["cells"]) == 12
    assert {cell["region_id"] for cell in context["cells"]} == {"suyeong", "gangneung", "chungju"}
    assert {cell["season"] for cell in context["cells"]} == {"winter", "spring", "summer", "autumn"}
    assert all(len(cell["kma_observations"]) == 168 for cell in context["cells"])
    assert len(cases) == 96
    counts = Counter((case["cell_id"], case["label"]) for case in cases)
    assert all(counts[(cell["cell_id"], "normal")] == 4 for cell in context["cells"])
    assert all(counts[(cell["cell_id"], "anomaly")] == 4 for cell in context["cells"])
    assert summary["frozen_detector_config"]["weather_weight"] == 0.0
    assert summary["frozen_detector_config"]["threshold"] == 0.55
    assert summary["validation_kind"] == "controlled_cross_context_invariance"
    assert summary["external_ami_validation"]["status"] == "unavailable"
    assert summary["regional_assets"]["chungju"]["rated_load_status"] == "unavailable_no_imputation"
    assert "Not field" in summary["claim_boundary"]
    manifest = load(REPORTS / "reproducibility_manifest.json")
    for relative, expected in manifest["files"].items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        assert actual == expected, relative
    print("v0.7 artifact contract: PASS")


if __name__ == "__main__":
    main()
