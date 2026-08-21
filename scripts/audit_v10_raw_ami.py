#!/usr/bin/env python3
"""Fingerprint the ignored B-feeder AMI workbook without copying source rows."""

from __future__ import annotations

import glob
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import openpyxl


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "lightguard_v0_1/data/validation/v10/v10_raw_ami_manifest.json"
TARGET_METERS = ("B-L-9", "B-L-12", "B-L-13", "B-L-14", "B-L-35")
START_DATE = date(2026, 4, 1)
END_DATE = date(2026, 6, 30)
EXPECTED_SOURCE_SHA256 = "c18b49022d1c7dee2117a8d65a07d71351fb1aea8538751b7032867e4081b7d0"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def number(value: object) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    return float(value)


def parse_timestamp(value: object) -> tuple[datetime, date, bool]:
    text = str(value).strip()
    if text.endswith(" 24:00"):
        source_day = datetime.fromisoformat(text[:-5] + "00:00").date()
        return datetime.fromisoformat(text[:-5] + "00:00") + timedelta(days=1), source_day, True
    timestamp = datetime.fromisoformat(text)
    return timestamp, timestamp.date(), False


def locate_source() -> Path:
    matches = [Path(p) for p in glob.glob(str(ROOT / "official_docs/AMI Data Sample/*B*★.xlsx"))]
    if len(matches) != 1:
        raise RuntimeError(f"BLOCKED_NO_FULL_AMI: expected one B-line workbook, found {len(matches)}")
    return matches[0]


def positive_gap_minutes(timestamps: list[datetime]) -> list[int]:
    unique = sorted(set(timestamps))
    return [int((right - left).total_seconds() / 60) for left, right in zip(unique, unique[1:]) if right > left]


def main() -> None:
    source = locate_source()
    source_hash = sha256(source)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(f"raw AMI SHA mismatch: {source_hash}")

    workbook = openpyxl.load_workbook(source, read_only=True, data_only=True)
    sheet = workbook["B선로 AMI DATA"]
    rows_by_meter: dict[str, list[dict]] = defaultdict(list)
    all_meters: set[str] = set()
    source_nonempty_rows = 0

    for source_row, values in enumerate(sheet.iter_rows(min_row=3, values_only=True), start=3):
        if not values or values[0] is None or values[1] is None:
            continue
        source_nonempty_rows += 1
        meter = str(values[0]).strip()
        all_meters.add(meter)
        if meter not in TARGET_METERS:
            continue
        timestamp, logical_date, normalized_24h = parse_timestamp(values[1])
        if not START_DATE <= logical_date <= END_DATE:
            continue
        rows_by_meter[meter].append({
            "timestamp": timestamp,
            "logical_date": logical_date,
            "normalized_24h": normalized_24h,
            "recv_active_kwh": number(values[3]),
            "i1": number(values[13]),
            "i2": number(values[14]),
            "i3": number(values[15]),
            "source_row": source_row,
        })
    workbook.close()

    missing_meters = sorted(set(TARGET_METERS) - set(rows_by_meter))
    meter_records = []
    for meter in TARGET_METERS:
        rows = sorted(rows_by_meter.get(meter, []), key=lambda row: (row["timestamp"], row["source_row"]))
        if not rows:
            continue
        timestamps = [row["timestamp"] for row in rows]
        logical_dates = [row["logical_date"] for row in rows]
        gaps = positive_gap_minutes(timestamps)
        channel_missing = {
            key: sum(row[key] is None for row in rows)
            for key in ("i1", "i2", "i3", "recv_active_kwh")
        }
        meter_records.append({
            "meter_id": meter,
            "row_count": len(rows),
            "date_min": min(logical_dates).isoformat(),
            "date_max": max(logical_dates).isoformat(),
            "timestamp_min_interval_end": min(timestamps).isoformat(sep=" "),
            "timestamp_max_interval_end": max(timestamps).isoformat(sep=" "),
            "cadence_minutes_median": int(statistics.median(gaps)) if gaps else None,
            "cadence_gap_counts": {str(key): value for key, value in sorted(Counter(gaps).items())},
            "duplicate_timestamp_count": len(timestamps) - len(set(timestamps)),
            "hour24_normalization_count": sum(row["normalized_24h"] for row in rows),
            "channel_missing_count": channel_missing,
            "channel_missing_rate": {
                key: round(value / len(rows), 9) for key, value in channel_missing.items()
            },
            "measured_current_phase_count": sum(
                any(row[key] is not None for row in rows) for key in ("i1", "i2", "i3")
            ),
        })

    failures = []
    if missing_meters:
        failures.append(f"missing meters: {missing_meters}")
    for record in meter_records:
        if record["date_min"] != START_DATE.isoformat() or record["date_max"] != END_DATE.isoformat():
            failures.append(f"incomplete period: {record['meter_id']}")
        if record["cadence_minutes_median"] != 15:
            failures.append(f"unexpected cadence: {record['meter_id']}")
        if record["measured_current_phase_count"] < 1:
            failures.append(f"no measured current: {record['meter_id']}")

    payload = {
        "schema_version": "lightguard.v10.raw_ami_manifest.1",
        "availability_gate": "PASS" if not failures else "BLOCKED_NO_FULL_AMI",
        "source": {
            "filename": source.name,
            "sha256": source_hash,
            "byte_count": source.stat().st_size,
            "sheet_name": "B선로 AMI DATA",
            "source_nonempty_row_count": source_nonempty_rows,
            "source_meter_count": len(all_meters),
            "tracked_in_git": False,
            "source_rows_copied_to_manifest": False,
        },
        "scope": {
            "target_meters": list(TARGET_METERS),
            "period_start": START_DATE.isoformat(),
            "period_end": END_DATE.isoformat(),
            "timestamp_semantics": "source interval end; source 24:00 normalized to next midnight",
            "timezone": "Asia/Seoul",
        },
        "columns": {
            "meter_id": {"zero_based_index": 0, "source_label": "순번(계기번호)"},
            "timestamp": {"zero_based_index": 1, "source_label": "시간"},
            "energy": [{"zero_based_index": 3, "semantic": "receiving_active_kwh"}],
            "current": [
                {"zero_based_index": 13, "semantic": "i1_ampere"},
                {"zero_based_index": 14, "semantic": "i2_ampere"},
                {"zero_based_index": 15, "semantic": "i3_ampere"},
            ],
        },
        "meters": meter_records,
        "failures": failures,
        "immutability": {
            "raw_source_modified": False,
            "raw_source_must_remain_untracked": True,
            "energy_reconstruction_allowed": False,
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "availability_gate": payload["availability_gate"],
        "source_sha256": source_hash,
        "source_rows": source_nonempty_rows,
        "source_meters": len(all_meters),
        "target_rows": sum(row["row_count"] for row in meter_records),
        "target_meters": len(meter_records),
        "failures": failures,
    }, ensure_ascii=False))
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
