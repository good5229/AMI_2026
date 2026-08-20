#!/usr/bin/env python3
"""Hard-gate the v0.11 Route-C artifact and claim contract."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v11"
REPORTS = ROOT / "lightguard_v0_1/reports/v11"


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    required = [
        DATA / "v10_freeze_manifest.json", DATA / "v11_raw_source_inventory.csv",
        DATA / "v11_label_source_inventory.csv", DATA / "v11_label_mapping_audit.csv",
        DATA / "v11_proxy_signs.csv", DATA / "v11_random_controls.csv",
        DATA / "v11_blind_review_manifest.json",
        REPORTS / "v11_full_label_audit.md", REPORTS / "v11_proxy_definition_protocol.md",
        REPORTS / "v11_independent_detector_results.csv",
        REPORTS / "v11_canonical_six_proxy_review.csv",
        REPORTS / "v11_random_control_enrichment.md",
        REPORTS / "v11_blind_review_packet.html",
        REPORTS / "v11_blind_review_labels_template.csv",
        REPORTS / "v11_final_summary.md", REPORTS / "reproducibility_manifest.json",
    ]
    require(all(path.exists() and path.stat().st_size > 0 for path in required), "required artifact missing")
    inventory = rows(DATA / "v11_raw_source_inventory.csv")
    require(len(inventory) == 149, "raw inventory coverage changed")
    require(len({row["path"] for row in inventory}) == len(inventory), "duplicate inventory path")
    labels = rows(DATA / "v11_label_source_inventory.csv")
    require(not any(row["usable"].lower() == "true" and row["level"] in ("G_CANDIDATE", "S1_CANDIDATE") for row in labels), "Route C contradicted by usable label")
    mapping = rows(DATA / "v11_label_mapping_audit.csv")
    require(not any(row["usable_for_gold"].lower() == "true" or row["usable_for_silver"].lower() == "true" for row in mapping), "usable mapping contradicts Route C")
    seal = json.loads((DATA / "v11_proxy_score_seal.json").read_text())
    require(seal["sealed_before_canonical_join"], "score was not sealed before canonical join")
    require(sha(ROOT / seal["score_path"]) == seal["score_sha256"], "score seal mismatch")
    freeze = json.loads((DATA / "v11_proxy_detector_freeze.json").read_text())
    require(freeze["calibration_window"] == {"start": "2026-04-01", "end": "2026-04-30"}, "April calibration changed")
    require(freeze["scoring_window"] == {"start": "2026-05-01", "end": "2026-06-30"}, "confirmatory window changed")
    require(len(rows(DATA / "v11_proxy_canonical_six.csv")) == 6, "canonical six contract failed")
    controls = rows(DATA / "v11_random_controls.csv")
    require(len(controls) == 6 and all(row["match_status"] == "MATCHED" for row in controls), "matched controls incomplete")
    require(all("detector scores not used" in row["selection_policy"] for row in controls), "control selection leakage")
    blind = json.loads((DATA / "v11_blind_review_manifest.json").read_text())
    require(blind["reviewer_labels_collected"] is False, "uncollected review labels misrepresented")
    packet = (REPORTS / "v11_blind_review_packet.html").read_text()
    for hidden in ("H1_PROXY_HIGH", "H1_ONLY", "PROXY_HIGH_ONLY", "MATCHED_RANDOM", "canonical six"):
        require(hidden not in packet, f"blind packet leaks {hidden}")
    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    require(not any(path == ".env" or path.startswith("official_docs/") or path.startswith("harness_docs/") for path in tracked), "protected source tracked")
    app = json.loads((ROOT / "lightguard_app/assets/data/context/v11_proxy_detector_summary.json").read_text())
    require(app["route"] == "C" and app["gold_usable"] == 0 and app["silver_usable"] == 0, "app claim boundary invalid")
    require(app["high_confidence_proxy_candidates"] == 765, "proxy result changed")
    reproducibility = json.loads((REPORTS / "reproducibility_manifest.json").read_text())
    require(all(sha(ROOT / item["path"]) == item["sha256"] for item in reproducibility["files"]), "reproducibility manifest mismatch")
    print(json.dumps({"status": "PASS", "files": len(inventory), "score_rows": app["score_rows"], "review_cases": app["review_packet_cases"]}))


if __name__ == "__main__":
    main()
