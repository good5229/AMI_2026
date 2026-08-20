#!/usr/bin/env python3
"""Verify that the frozen v0.7 regression baseline remains intact."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "lightguard_v0_1/data/validation/v08/v07_freeze_manifest.json"


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["baseline_role"] == "regression_only_not_for_v08_tuning"
    assert manifest["preflight"]["status"] == "PASS"
    assert manifest["baseline_metrics"]["scenario_count"] == 96
    assert manifest["baseline_metrics"]["macro_recall"] == 0.5
    assert manifest["baseline_metrics"]["macro_fpr"] == 0.0
    for relative, expected in manifest["sha256"].items():
        path = ROOT / relative
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == expected, f"freeze mismatch: {relative}"
    subprocess.run(
        ["git", "cat-file", "-e", f"{manifest['frozen_git_sha']}^{{commit}}"],
        cwd=ROOT,
        check=True,
    )
    print("v0.7 freeze integrity: PASS")


if __name__ == "__main__":
    main()
