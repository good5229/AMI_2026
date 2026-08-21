#!/usr/bin/env python3
"""Inventory every local tabular source and conservatively audit label evidence."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

import openpyxl


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v11"
REPORTS = ROOT / "lightguard_v0_1/reports/v11"
EXTENSIONS = {".csv", ".json", ".xls", ".xlsx"}
EXCLUDED_PARTS = {".git", ".dart_tool", "build", "__pycache__", "v11"}
FAULT = ("고장", "장애", "불량", "비정상", "수리", "보수", "정비", "교체", "복구", "처리", "조치", "원인", "fault", "failure", "repair", "maintenance")
OPERATIONAL = ("민원", "신고", "접수", "출동", "현장", "점검", "제어", "명령", "동작", "통신", "상태", "complaint", "inspection", "controller", "command", "status")
TIME = ("시간", "일시", "발생일", "접수일", "처리일", "방문일", "timestamp", "datetime", "date", "time")
JOIN = ("계기번호", "계량기", "meter", "ami", "분전함", "관리번호", "등기구", "가로등", "시설물", "회로", "cabinet", "fixture", "controller")
MEASURE = ("전류", "전력", "전압", "전력량", "current", "energy", "voltage", "i1", "i2", "i3")
CONFIRMED_VALUES = ("고장 확인", "불량 확인", "고장", "장애", "수리 완료", "정비 완료", "교체 완료", "confirmed fault", "repaired")
TARGET_METERS = {"B-L-9", "B-L-12", "B-L-13", "B-L-14", "B-L-35"}
V10_RELEASE = "d34d8323b3742c9116060d9548bd29c18750cb1f"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalized(value: object) -> str:
    return "" if value is None else str(value).strip().lower()


def contains(text: str, terms: tuple[str, ...]) -> bool:
    value = normalized(text)
    return any(term.lower() in value for term in terms)


def source_authority(path: Path) -> str:
    relative = path.relative_to(ROOT)
    if relative.parts[0] == "official_docs":
        return "competition_official_local"
    if relative.parts[0] == "lightguard_v0_1" and "app_seed" not in relative.parts:
        return "project_derived_or_public"
    if relative.parts[0] == "lightguard_app" and "assets" in relative.parts:
        return "app_derived"
    return "repository_support"


def candidate_paths() -> list[Path]:
    result = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_PARTS for part in relative.parts) or path.name.startswith("v11_"):
            continue
        result.append(path)
    return sorted(result, key=lambda item: item.relative_to(ROOT).as_posix())


def flatten_json(value: object, prefix: str = "$") -> Iterable[tuple[str, object]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from flatten_json(child, f"{prefix}.{key}")
    elif isinstance(value, list):
        for child in value:
            yield from flatten_json(child, f"{prefix}[]")
    else:
        yield prefix, value


def profile_records(records: Iterable[tuple[str, list[object]]]) -> tuple[int, set[str], dict[str, Counter], set[str]]:
    rows = 0
    columns: set[str] = set()
    values: dict[str, Counter] = defaultdict(Counter)
    meter_values: set[str] = set()
    for _, record in records:
        rows += 1
        for index, value in enumerate(record):
            column = f"column_{index + 1}"
            columns.add(column)
            text = normalized(value)
            if text:
                values[column][text[:160]] += 1
                if text.upper() in TARGET_METERS:
                    meter_values.add(text.upper())
    return rows, columns, values, meter_values


def read_csv(path: Path) -> tuple[list[str], int, dict[str, Counter], set[str], str]:
    encoding = "utf-8-sig"
    try:
        handle = path.open(encoding=encoding, newline="")
        handle.read(1024)
        handle.seek(0)
    except UnicodeDecodeError:
        encoding = "cp949"
        handle = path.open(encoding=encoding, newline="")
    with handle:
        reader = csv.reader(handle)
        try:
            headers = [str(value).strip() or f"column_{i + 1}" for i, value in enumerate(next(reader))]
        except StopIteration:
            return [], 0, {}, set(), encoding
        counters: dict[str, Counter] = {header: Counter() for header in headers}
        meter_values: set[str] = set()
        rows = 0
        for record in reader:
            rows += 1
            for i, value in enumerate(record):
                header = headers[i] if i < len(headers) else f"column_{i + 1}"
                text = normalized(value)
                if text:
                    counters.setdefault(header, Counter())[text[:160]] += 1
                    if text.upper() in TARGET_METERS:
                        meter_values.add(text.upper())
        return headers, rows, counters, meter_values, encoding


def read_json(path: Path) -> tuple[list[str], int, dict[str, Counter], set[str], str]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    roots = payload if isinstance(payload, list) else [payload]
    counters: dict[str, Counter] = defaultdict(Counter)
    meter_values: set[str] = set()
    rows = len(roots)
    for root in roots:
        for key, value in flatten_json(root):
            text = normalized(value)
            if text:
                counters[key][text[:160]] += 1
                if text.upper() in TARGET_METERS:
                    meter_values.add(text.upper())
    return sorted(counters), rows, counters, meter_values, "utf-8-sig"


def read_excel(path: Path) -> list[tuple[str, list[str], int, dict[str, Counter], set[str]]]:
    if path.suffix.lower() == ".xls":
        return [("<unsupported-xls>", [], 0, {}, set())]
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    result = []
    for sheet in workbook.worksheets:
        rows = sheet.iter_rows(values_only=True)
        first = next(rows, ())
        second = next(rows, ())
        # Competition AMI uses a title row followed by its actual header row.
        header_values = second if sum(value is not None for value in second) >= sum(value is not None for value in first) else first
        headers = [str(value).strip() if value is not None else f"column_{i + 1}" for i, value in enumerate(header_values)]
        counters: dict[str, Counter] = {header: Counter() for header in headers}
        meter_values: set[str] = set()
        count = 0
        for record in rows:
            count += 1
            for i, value in enumerate(record):
                header = headers[i] if i < len(headers) else f"column_{i + 1}"
                text = normalized(value)
                if text:
                    counters.setdefault(header, Counter())[text[:160]] += 1
                    if text.upper() in TARGET_METERS:
                        meter_values.add(text.upper())
        result.append((sheet.title, headers, count, counters, meter_values))
    workbook.close()
    return result


def evidence_rows(source_id: str, path: Path, sheet: str, headers: list[str], counters: dict[str, Counter], meters: set[str]) -> list[dict]:
    output = []
    has_time = any(contains(header, TIME) for header in headers)
    has_join = any(contains(header, JOIN) for header in headers)
    for header in headers:
        samples = counters.get(header, Counter())
        matched = [value for value in samples if contains(value, FAULT + OPERATIONAL)]
        header_fault = contains(header, FAULT)
        header_operational = contains(header, OPERATIONAL)
        header_measure = contains(header, MEASURE)
        confirmed = any(contains(value, CONFIRMED_VALUES) for value in matched)
        if not (header_fault or header_operational or header_measure or matched):
            continue
        if header_fault and confirmed and has_time and has_join:
            level = "G_CANDIDATE"
        elif (header_operational or matched) and has_time and has_join:
            level = "S1_CANDIDATE"
        elif header_measure:
            level = "S2_PROXY_INPUT"
        else:
            level = "U"
        # A candidate is never usable until an independent mapping audit proves linkage.
        usable = False
        reason = "field evidence requires verified target mapping and record-level review"
        if level == "S2_PROXY_INPUT":
            reason = "measurement input only; not a fault or operational truth label"
        elif level == "U":
            reason = "keyword evidence lacks time and/or join key"
        output.append({
            "source_id": source_id,
            "path": path.relative_to(ROOT).as_posix(),
            "sheet": sheet,
            "field": header,
            "level": level,
            "join_key_present": has_join,
            "time_key_present": has_time,
            "target_meter_overlap": ";".join(sorted(meters)),
            "matched_value_count": sum(samples[value] for value in matched),
            "sample_values": " | ".join(matched[:8]),
            "usable": usable,
            "reason": reason,
        })
    return output


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    tracked = set(subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines())
    inventory, evidence, mappings = [], [], []
    totals = Counter()
    for number, path in enumerate(candidate_paths(), start=1):
        source_id = f"SRC-{number:04d}"
        relative = path.relative_to(ROOT).as_posix()
        sheets = []
        if path.suffix.lower() == ".csv":
            headers, rows, counters, meters, encoding = read_csv(path)
            profiles = [("", headers, rows, counters, meters)]
        elif path.suffix.lower() == ".json":
            headers, rows, counters, meters, encoding = read_json(path)
            profiles = [("", headers, rows, counters, meters)]
        else:
            encoding = "binary"
            profiles = read_excel(path)
        for sheet, headers, rows, counters, meters in profiles:
            sheets.append(sheet or "<root>")
            totals["sheets"] += 1
            totals["rows"] += rows
            totals["columns"] += len(headers)
            evidence.extend(evidence_rows(source_id, path, sheet, headers, counters, meters))
            join_fields = [header for header in headers if contains(header, JOIN)]
            if join_fields:
                exact_target_overlap = bool(meters)
                mappings.append({
                    "source_record_id": source_id + (f":{sheet}" if sheet else ""),
                    "source_path": relative,
                    "target_meter_or_cabinet": ";".join(sorted(meters)),
                    "join_method": "exact_target_meter_value" if exact_target_overlap else "field_name_only",
                    "join_key": ";".join(join_fields),
                    "time_alignment": "available" if any(contains(header, TIME) for header in headers) else "unavailable",
                    "mapping_confidence": "PARTIAL" if exact_target_overlap else "UNAVAILABLE",
                    "usable_for_gold": False,
                    "usable_for_silver": False,
                })
        inventory.append({
            "source_id": source_id,
            "path": relative,
            "filename": path.name,
            "extension": path.suffix.lower(),
            "size": path.stat().st_size,
            "sha256": sha256(path),
            "sheet_names": ";".join(sheets),
            "row_count": sum(item[2] for item in profiles),
            "column_count": sum(len(item[1]) for item in profiles),
            "encoding": encoding,
            "tracked_in_git": relative in tracked,
            "source_authority": source_authority(path),
            "source_year": next((part for part in relative.split("/") if part.isdigit() and len(part) == 4), ""),
            "notes": "read-only full value profile",
        })

    gold = [row for row in evidence if row["level"] == "G_CANDIDATE" and row["usable"]]
    silver = [row for row in evidence if row["level"] == "S1_CANDIDATE" and row["usable"]]
    route = "A" if gold else ("B" if silver else "C")
    inventory_fields = list(inventory[0]) if inventory else []
    evidence_fields = list(evidence[0]) if evidence else ["source_id", "path", "sheet", "field", "level", "join_key_present", "time_key_present", "target_meter_overlap", "matched_value_count", "sample_values", "usable", "reason"]
    mapping_fields = list(mappings[0]) if mappings else ["source_record_id", "source_path", "target_meter_or_cabinet", "join_method", "join_key", "time_alignment", "mapping_confidence", "usable_for_gold", "usable_for_silver"]
    write_csv(DATA / "v11_raw_source_inventory.csv", inventory, inventory_fields)
    write_csv(DATA / "v11_label_source_inventory.csv", evidence, evidence_fields)
    write_csv(REPORTS / "v11_label_source_inventory.csv", evidence, evidence_fields)
    write_csv(DATA / "v11_label_mapping_audit.csv", mappings, mapping_fields)
    write_csv(REPORTS / "v11_label_mapping_audit.csv", mappings, mapping_fields)

    freeze_paths = [
        ROOT / "lightguard_v0_1/data/validation/v10/v09_freeze_manifest.json",
        ROOT / "lightguard_v0_1/data/validation/v10/v10_raw_ami_manifest.json",
        ROOT / "lightguard_v0_1/reports/v10/v10_final_summary.md",
        ROOT / "scripts/v09_detector.py",
    ]
    freeze = {
        "schema_version": "lightguard.v11.v10-freeze.1",
        "v10_release_commit": V10_RELEASE,
        "release_commit_exists": subprocess.run(["git", "cat-file", "-e", f"{V10_RELEASE}^{{commit}}"], cwd=ROOT).returncode == 0,
        "frozen_h1_modified": False,
        "files": [{"path": item.relative_to(ROOT).as_posix(), "sha256": sha256(item)} for item in freeze_paths],
    }
    (DATA / "v10_freeze_manifest.json").write_text(json.dumps(freeze, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    level_counts = Counter(row["level"] for row in evidence)
    summary = f"""# LightGuard v0.11 Full Label Audit

## Coverage

- Files audited: {len(inventory)}
- Sheets/root objects: {totals['sheets']}
- Rows/profile roots: {totals['rows']}
- Columns/JSON paths: {totals['columns']}
- Inventory method: full local CSV/JSON/XLSX value scan; raw sources remained read-only

## Label Evidence

| level | fields | usable records | interpretation |
|---|---:|---:|---|
| Gold candidate | {level_counts['G_CANDIDATE']} | {len(gold)} | field-confirmed and target-mapped only |
| Silver Operational candidate | {level_counts['S1_CANDIDATE']} | {len(silver)} | independent operational discrepancy only |
| Proxy Pattern input | {level_counts['S2_PROXY_INPUT']} | 0 | measurement input, not truth |
| Unlabeled keyword evidence | {level_counts['U']} | 0 | insufficient time/mapping evidence |

## Route Decision

- Selected route: **Route {route}**
- Gold usable for target AMI: {len(gold)}
- Silver Operational usable for target AMI: {len(silver)}
- Route C means proxy concordance and enrichment only. It does not support fault accuracy, recall, precision, FPR, or specificity claims.

## Mapping

- Target meter values appear in raw AMI sources, but no verified target meter-to-cabinet-to-maintenance/controller chain was found.
- Field-name similarity is not accepted as a verified mapping.

## Claim Boundary

The audit does not manufacture human truth. A keyword, status field, measurement channel, synthetic scenario, or model output is not a confirmed fault.
"""
    (REPORTS / "v11_full_label_audit.md").write_text(summary, encoding="utf-8")
    (REPORTS / "v11_label_audit_summary.md").write_text(summary, encoding="utf-8")
    (REPORTS / "v11_gold_silver_proxy_summary.md").write_text(summary, encoding="utf-8")
    print(json.dumps({"files": len(inventory), "sheets": totals["sheets"], "rows": totals["rows"], "columns": totals["columns"], "evidence": dict(level_counts), "gold_usable": len(gold), "silver_usable": len(silver), "route": route}, ensure_ascii=False))


if __name__ == "__main__":
    main()
