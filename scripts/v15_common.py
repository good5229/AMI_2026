#!/usr/bin/env python3
"""Fail-closed, outcome-blind utilities for the v0.15 paired ablation plan."""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

from v10_ami import ROOT, RAW_SHA256, TARGET_METERS, canonical_json_sha, group_days, load_rows, measured_phases, sha256_file

DATA = ROOT / "lightguard_v0_1/data/validation/v15"
V10 = ROOT / "lightguard_v0_1/data/validation/v10"
ASSETS = ROOT / "lightguard_app/assets/data/ami_events.csv"
V10_POOL = V10 / "v10_background_pool_manifest.json"
PREDECESSOR_FREEZE = DATA / "v14_freeze_manifest.json"
LEGACY_PREDECESSOR_FREEZE = DATA / "v15_predecessor_freeze.json"
REMAINING_POOL_AUDIT = DATA / "v15_remaining_pool_audit.csv"
LEGACY_REMAINING_POOL_AUDIT = DATA / "v15_meter_day_audit.csv"
HOLDOUT_MANIFEST = DATA / "v15_background_holdout_manifest.json"
LEGACY_HOLDOUT_MANIFEST = DATA / "v15_counterfactual_holdout.json"
INJECTION_MANIFEST = DATA / "v15_injection_manifest.json"
SEED = "LG-v15-HOLDOUT-20260821"
POOL_DATES = (date(2026, 5, 1), date(2026, 6, 30))
CLAIM_BOUNDARY = "Paired target-domain mechanism ablation only; not streetlight field accuracy, fault probability, or maintenance truth."
VARIANT_FIELDS = ("A0", "A1", "A2", "A3", "A4", "A5", "Z1")
RESULT_FIELDS = ["pair_id", "meter_id", "local_date", "operator", "operator_class", "variant", "status", "control_action", "injected_action", "control_score", "injected_score", "recovered", "benign_escalated", "threshold_same", "action_scale_comparable", "source_start", "target_start", "claim_boundary"]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing required artifact: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON object required: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def file_hashes(paths: Iterable[Path]) -> list[dict[str, str]]:
    output = []
    for path in paths:
        require(path.is_file(), f"missing predecessor artifact: {path}")
        output.append({"path": str(path.relative_to(ROOT)), "sha256": sha256_file(path)})
    return output


def canonical_windows() -> dict[str, list[tuple[datetime, datetime]]]:
    windows = {meter: [] for meter in TARGET_METERS}
    with ASSETS.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            meter = row.get("meter_id", "")
            if meter not in windows:
                continue
            start = datetime.fromisoformat(row["first_sample"]) - timedelta(hours=4)
            end = datetime.fromisoformat(row["last_sample"]) + timedelta(hours=4)
            windows[meter].append((start, end))
    return windows


def overlaps(left_start: datetime, left_end: datetime, right_start: datetime, right_end: datetime) -> bool:
    return left_start <= right_end and right_start <= left_end


def day_hash(meter_id: str, local_date: date, rows: list[dict]) -> str:
    return canonical_json_sha({"meter_id": meter_id, "local_date": local_date.isoformat(), "rows": [row["row_sha256"] for row in rows]})


def active_phase_gate(rows: list[dict]) -> bool:
    return len(measured_phases(rows)) == 3 and all(all(row["currents"][phase] is not None for phase in ("i1", "i2", "i3")) for row in rows)


def deterministic_key(*parts: object) -> str:
    return hashlib.sha256("|".join((SEED, *(str(part) for part in parts))).encode()).hexdigest()


def severity(action: str) -> int:
    return {"normal": 0, "abstain": -1, "observe": 1, "data_check_required": 1, "inspect": 2}.get(action, -99)
