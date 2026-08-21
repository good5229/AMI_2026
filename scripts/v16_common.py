#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v16"
REPORT = ROOT / "lightguard_v0_1/reports/v16"
V10 = ROOT / "lightguard_v0_1/data/validation/v10"
V15 = ROOT / "lightguard_v0_1/data/validation/v15"
OFFICIAL = ROOT / "official_docs/AMI Data Sample"
SEED = "LG-v16-COMPETITION-UTILITY-20260821"
BOOTSTRAP_SEED = 202616
CLAIM_BOUNDARY = "Controlled counterfactual dispatch utility only; not field accuracy, real-background FPR, fault probability, maintenance truth, or actual savings."


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_sha(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, fields, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
