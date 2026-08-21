#!/usr/bin/env python3
"""Freeze a balanced detector-independent real-AMI background pool."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import date, datetime, timedelta
from pathlib import Path

from v10_ami import ROOT, TARGET_METERS, canonical_json_sha, group_days, load_rows, measured_phases, sha256_file


OUTPUT = ROOT / "lightguard_v0_1/data/validation/v10/v10_background_pool_manifest.json"
RAW_MANIFEST = ROOT / "lightguard_v0_1/data/validation/v10/v10_raw_ami_manifest.json"
CANONICAL = ROOT / "lightguard_app/assets/data/ami_events.csv"
POOL_START = date(2026, 5, 1)
POOL_END = date(2026, 6, 30)
PER_METER = 40
NAMESPACE = "LG-v10-POOL-20260820"
OPS_3P = ("deep_day_full", "daytime_partial", "post_switch_persistence", "phase_selective", "weak_long_duration", "benign_transition")
OPS_1P = ("deep_day_full", "daytime_partial", "post_switch_persistence", "weak_long_duration", "benign_transition")


def unit_hash(meter: str, day: date) -> str:
    return hashlib.sha256(f"{NAMESPACE}|{meter}|{day.isoformat()}".encode()).hexdigest()


def canonical_excluded_dates() -> dict[str, set[date]]:
    excluded = {meter: set() for meter in TARGET_METERS}
    with CANONICAL.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            meter = row["meter_id"]
            start = datetime.fromisoformat(row["first_sample"]) - timedelta(hours=4)
            end = datetime.fromisoformat(row["last_sample"]) + timedelta(minutes=15, hours=4)
            current = start.date()
            while current <= end.date():
                if meter in excluded:
                    excluded[meter].add(current)
                current += timedelta(days=1)
    return excluded


def main() -> None:
    rows_by_meter = load_rows()
    excluded = canonical_excluded_dates()
    units = []
    audit = {}
    for meter in TARGET_METERS:
        rows = rows_by_meter[meter]
        phases = measured_phases(rows)
        days = group_days(rows)
        eligible = []
        reasons = {"outside_pool_period": 0, "canonical_buffer": 0, "fewer_than_90_rows": 0, "grid_or_duplicate": 0, "fewer_than_90_usable_current_slots": 0}
        for day, day_rows in sorted(days.items()):
            if not POOL_START <= day <= POOL_END:
                reasons["outside_pool_period"] += 1; continue
            if day in excluded[meter]:
                reasons["canonical_buffer"] += 1; continue
            if len(day_rows) < 90:
                reasons["fewer_than_90_rows"] += 1; continue
            timestamps = [row["timestamp"] for row in day_rows]
            expected = [datetime.combine(day, datetime.min.time()) + timedelta(minutes=15 * index) for index in range(1, 97)]
            expected_set = set(expected)
            if len(set(timestamps)) != len(timestamps) or any(timestamp not in expected_set for timestamp in timestamps):
                reasons["grid_or_duplicate"] += 1; continue
            usable_slots = sum(all(row["currents"][phase] is not None and row["currents"][phase] >= 0 for phase in phases) for row in day_rows)
            if usable_slots < 90:
                reasons["fewer_than_90_usable_current_slots"] += 1; continue
            eligible.append({"meter_id": meter, "local_date": day.isoformat(), "unit_hash": unit_hash(meter, day), "phases": list(phases), "source_row_count": len(day_rows), "usable_current_slots": usable_slots, "source_rows_sha256": canonical_json_sha([row["row_sha256"] for row in day_rows])})
        eligible.sort(key=lambda row: (row["unit_hash"], row["local_date"]))
        if len(eligible) < PER_METER:
            raise RuntimeError(f"background pool shortfall for {meter}: {len(eligible)} < {PER_METER}")
        selected = eligible[:PER_METER]
        operators = OPS_3P if len(phases) == 3 else OPS_1P
        for rank, unit in enumerate(selected):
            unit.update({"rank_within_meter": rank, "operator": operators[rank % len(operators)], "selection_uses_h1": False, "canonical_buffer_hours": 4})
            units.append(unit)
        audit[meter] = {"measured_phases": list(phases), "eligible_before_cap": len(eligible), "selected": len(selected), "exclusion_counts": reasons}

    payload = {
        "schema_version": "lightguard.v10.background-pool.2",
        "status": "FROZEN_BEFORE_H1_OUTCOME",
        "namespace": NAMESPACE,
        "selection_rule": "first_40_by_sha256_within_meter_after_source_only_eligibility",
        "raw_manifest_sha256": sha256_file(RAW_MANIFEST),
        "canonical_artifact_sha256": sha256_file(CANONICAL),
        "unit_count": len(units),
        "meter_count": len(TARGET_METERS),
        "units_per_meter": PER_METER,
        "detector_output_used": False,
        "unmodified_background_truth_label": "unavailable",
        "audit": audit,
        "units": sorted(units, key=lambda row: (row["meter_id"], row["rank_within_meter"])),
    }
    payload["pool_sha256"] = canonical_json_sha(payload["units"])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"unit_count": len(units), "units_per_meter": PER_METER, "pool_sha256": payload["pool_sha256"], "detector_output_used": False}))


if __name__ == "__main__":
    main()
