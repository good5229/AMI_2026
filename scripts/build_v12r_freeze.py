#!/usr/bin/env python3
"""Freeze v0.11 evidence before v0.12R literature work."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "lightguard_v0_1/data/validation/v12r/v11_freeze_manifest.json"
V11_RELEASE = "b25b168250ede29b5c5bbcadab918c455d61ba74"
FILES = (
    "lightguard_v0_1/data/validation/v11/v10_freeze_manifest.json",
    "lightguard_v0_1/data/validation/v11/v11_proxy_score_seal.json",
    "lightguard_v0_1/data/validation/v11/v11_proxy_signs.csv",
    "lightguard_v0_1/data/validation/v11/v11_blind_review_manifest.json",
    "lightguard_v0_1/reports/v11/v11_final_summary.md",
    "scripts/v09_detector.py",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if subprocess.run(["git", "cat-file", "-e", f"{V11_RELEASE}^{{commit}}"], cwd=ROOT).returncode:
        raise RuntimeError("v0.11 release commit unavailable")
    payload = {
        "schema_version": "lightguard.v12r.v11-freeze.1",
        "v11_release_commit": V11_RELEASE,
        "route": "C",
        "gold_usable": 0,
        "silver_operational_usable": 0,
        "human_labels_collected": False,
        "detector_retuning_permitted": False,
        "literature_as_fault_label_permitted": False,
        "literature_search_protocol": {
            "path": "lightguard_v0_1/reports/v12r/v12r_literature_search_protocol.md",
            "sha256": sha(ROOT / "lightguard_v0_1/reports/v12r/v12r_literature_search_protocol.md"),
            "frozen_before_screening": True,
        },
        "files": [{"path": name, "sha256": sha(ROOT / name)} for name in FILES],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "FROZEN", "files": len(FILES), "release": V11_RELEASE}))


if __name__ == "__main__":
    main()
