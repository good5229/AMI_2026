#!/usr/bin/env python3
"""Freeze the v0.9 H1 implementation and evidence before v0.10 scoring."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "lightguard_v0_1/data/validation/v10/v09_freeze_manifest.json"
CONFIG = ROOT / "lightguard_v0_1/data/validation/v09/v09_candidate_config.json"
RAW_MANIFEST = ROOT / "lightguard_v0_1/data/validation/v10/v10_raw_ami_manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def frozen_paths() -> list[Path]:
    prefixes = (
        "docs/agent_learning_v09/",
        "lightguard_v0_1/data/validation/v09/",
        "lightguard_v0_1/reports/v09/",
    )
    exact = {
        "lightguard_app/assets/data/context/v09_specificity_summary.json",
        "lightguard_app/docs/v09_specificity_validation.md",
        "lightguard_app/lib/features/ami_validation/v09_specificity_card.dart",
        "lightguard_app/test/unit/v09_specificity_validation_test.dart",
    }
    tracked = git("ls-files").splitlines()
    selected = [name for name in tracked if name.startswith(prefixes) or name in exact]
    selected.extend(name for name in tracked if name.startswith("scripts/") and "v09" in Path(name).name)
    return [ROOT / name for name in sorted(set(selected))]


def main() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    if config["selected_candidate"] != "H1":
        raise RuntimeError("v0.9 selected candidate is not H1")
    expected = {
        "stage_a_threshold": 0.525,
        "specificity_threshold": 0.525,
        "availability_floor": None,
        "weather_weight": 0.0,
    }
    if config["selected_config"] != expected:
        raise RuntimeError(f"frozen H1 config changed: {config['selected_config']}")
    if config["confirmatory_seen"] or config["post_confirmatory_retuning_permitted"]:
        raise RuntimeError("v0.9 freeze permits confirmatory retuning")

    files = frozen_paths()
    payload = {
        "schema_version": "lightguard.v10.v09-freeze.1",
        "frozen_at_git": {
            "branch": git("branch", "--show-current"),
            "sha": git("rev-parse", "HEAD"),
        },
        "candidate": {
            "name": "H1",
            "config": expected,
            "config_file_sha256": sha256(CONFIG),
            "detector_file_sha256": sha256(ROOT / "scripts/v09_detector.py"),
            "weather_scoring": "disabled",
            "load_imputation": "none",
            "v10_track_a_retuning_permitted": False,
        },
        "raw_ami_manifest_sha256": sha256(RAW_MANIFEST),
        "frozen_files": [
            {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)} for path in files
        ],
        "frozen_file_count": len(files),
        "claim_boundary": "v09_controlled_generated_evidence_is_regression_only_for_v10",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidate": "H1",
        "frozen_file_count": len(files),
        "config_sha256": payload["candidate"]["config_file_sha256"],
        "detector_sha256": payload["candidate"]["detector_file_sha256"],
    }))


if __name__ == "__main__":
    main()

