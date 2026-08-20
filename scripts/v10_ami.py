#!/usr/bin/env python3
"""Shared read-only access to the ignored anonymized v0.10 AMI source."""

from __future__ import annotations

import glob
import hashlib
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import openpyxl


ROOT = Path(__file__).resolve().parents[1]
TARGET_METERS = ("B-L-9", "B-L-12", "B-L-13", "B-L-14", "B-L-35")
RAW_SHA256 = "c18b49022d1c7dee2117a8d65a07d71351fb1aea8538751b7032867e4081b7d0"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_sha(payload: object) -> str:
    import json
    return sha256_bytes(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())


def locate_source() -> Path:
    matches = [Path(p) for p in glob.glob(str(ROOT / "official_docs/AMI Data Sample/*B*★.xlsx"))]
    if len(matches) != 1:
        raise RuntimeError(f"BLOCKED_NO_FULL_AMI: expected one B-line workbook, found {len(matches)}")
    if sha256_file(matches[0]) != RAW_SHA256:
        raise RuntimeError("raw AMI source hash changed")
    return matches[0]


def parse_timestamp(value: object) -> tuple[datetime, date, bool]:
    text = str(value).strip()
    if text.endswith(" 24:00"):
        logical = datetime.fromisoformat(text[:-5] + "00:00").date()
        return datetime.fromisoformat(text[:-5] + "00:00") + timedelta(days=1), logical, True
    parsed = datetime.fromisoformat(text)
    return parsed, parsed.date(), False


def number(value: object) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    return float(value)


def load_rows(start: date = date(2026, 4, 1), end: date = date(2026, 6, 30)) -> dict[str, list[dict]]:
    source = locate_source()
    workbook = openpyxl.load_workbook(source, read_only=True, data_only=True)
    sheet = workbook["B선로 AMI DATA"]
    result: dict[str, list[dict]] = {meter: [] for meter in TARGET_METERS}
    for source_row, values in enumerate(sheet.iter_rows(min_row=3, values_only=True), start=3):
        meter = str(values[0]).strip() if values and values[0] is not None else ""
        if meter not in result or values[1] is None:
            continue
        timestamp, logical_date, normalized_24h = parse_timestamp(values[1])
        if not start <= logical_date <= end:
            continue
        currents = {"i1": number(values[13]), "i2": number(values[14]), "i3": number(values[15])}
        row_identity = {
            "source_row": source_row,
            "meter_id": meter,
            "source_timestamp": str(values[1]),
            "currents": currents,
            "recv_active_kwh": number(values[3]),
        }
        result[meter].append({
            "meter_id": meter,
            "timestamp": timestamp,
            "logical_date": logical_date,
            "normalized_24h": normalized_24h,
            "source_row": source_row,
            "row_sha256": canonical_json_sha(row_identity),
            "currents": currents,
            "recv_active_kwh": number(values[3]),
        })
    workbook.close()
    for rows in result.values():
        rows.sort(key=lambda row: (row["timestamp"], row["source_row"]))
    return result


def measured_phases(rows: list[dict]) -> tuple[str, ...]:
    return tuple(phase for phase in ("i1", "i2", "i3") if any(row["currents"][phase] is not None for row in rows))


def group_days(rows: list[dict]) -> dict[date, list[dict]]:
    grouped: dict[date, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["logical_date"]].append(row)
    return {day: sorted(values, key=lambda row: row["timestamp"]) for day, values in grouped.items()}

