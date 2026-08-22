#!/usr/bin/env python3
"""Build claim-safe aggregate evidence from four Data.go.kr file datasets."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "official_docs" / "external_data"
DATA = ROOT / "lightguard_v0_1" / "data" / "validation" / "v23"
REPORT = ROOT / "lightguard_v0_1" / "reports" / "v23"

SOURCES = {
    "SEONGNAM": {
        "region": "성남시",
        "filename": "seongnam_streetlight_cabinets_20260805.csv",
        "url": "https://www.data.go.kr/data/15032441/fileData.do",
        "sha256": "2d5dac17d44f1520729e67942caf1940c05947c46891dff536e021647feb0769",
        "rows": 826,
        "role": "CABINET_WORKLOAD",
        "id": 1,
        "pole_count": 3,
        "lamp_count": 4,
    },
    "CHUNGJU": {
        "region": "충주시",
        "filename": "chungju_streetlight_cabinets_20260713.csv",
        "url": "https://www.data.go.kr/data/15041822/fileData.do",
        "sha256": "083319803dbf373dee5050deaf59943c14e257cc211c3a33fc799dd5627bc731",
        "rows": 871,
        "role": "CABINET_SPATIAL",
        "id": 2,
        "pole_count": 3,
        "latitude": 5,
        "longitude": 6,
    },
    "GUNPO": {
        "region": "군포시",
        "filename": "gunpo_urban_lighting_20251127.csv",
        "url": "https://www.data.go.kr/data/15062604/fileData.do",
        "sha256": "10284135b962c605640a2c074053586aedd60fa6efdb54b3ba39590d9464dd45",
        "rows": 250,
        "role": "CABINET_AGE_SPATIAL",
        "id": 0,
        "installation_date": 1,
        "pole_count": 3,
        "lamp_count": 4,
        "latitude": 5,
        "longitude": 6,
    },
    "TONGYEONG": {
        "region": "통영시",
        "filename": "tongyeong_streetlight_assets_20260423.csv",
        "url": "https://www.data.go.kr/data/15062585/fileData.do",
        "sha256": "62a8f8c0f1bfcd563497cfd6454eee8a5e475bce155d1474901131a14841c180",
        "rows": 4025,
        "role": "ASSET_TECHNICAL_SPATIAL",
        "id": 1,
        "cabinet_id": 3,
        "installation_date": 8,
        "lamp_count": 10,
        "longitude": 18,
        "latitude": 19,
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[list[str]], str]:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            decoded = raw.decode(encoding)
        except UnicodeDecodeError:
            continue
        parsed = list(csv.reader(decoded.splitlines()))
        if parsed:
            return [value.strip() for value in parsed[0]], parsed[1:], encoding
    raise RuntimeError(f"SOURCE_ENCODING:{path.name}")


def number(value: str) -> float | None:
    try:
        return float(value.replace(",", "").strip())
    except (ValueError, AttributeError):
        return None


def date_year(value: str) -> int | None:
    digits = "".join(ch for ch in value if ch.isdigit())
    if len(digits) < 4:
        return None
    year = int(digits[:4])
    return year if 1900 <= year <= 2026 else None


def profile(key: str, config: dict) -> dict:
    path = RAW / config["filename"]
    if not path.exists():
        raise RuntimeError(f"SOURCE_MISSING:{path.name}")
    actual_sha = sha256(path)
    if actual_sha != config["sha256"]:
        raise RuntimeError(f"SOURCE_SHA:{key}:{actual_sha}")
    columns, rows, encoding = read_csv(path)
    if len(rows) != config["rows"]:
        raise RuntimeError(f"SOURCE_ROWS:{key}:{len(rows)}")
    if any(len(row) != len(columns) for row in rows):
        raise RuntimeError(f"SOURCE_WIDTH:{key}")

    ids = [row[config["id"]].strip() for row in rows]
    nonempty_ids = [value for value in ids if value]
    metrics = {
        "role": config["role"],
        "decision": "MEANINGFUL_ASSET_CONTRACT_EVIDENCE",
        "records": len(rows),
        "column_count": len(columns),
        "exact_duplicate_rows": len(rows) - len(set(map(tuple, rows))),
        "id_coverage": len(nonempty_ids) / len(rows),
        "unique_ids": len(set(nonempty_ids)),
        "duplicate_id_records": len(nonempty_ids) - len(set(nonempty_ids)),
    }

    for field in ("pole_count", "lamp_count"):
        if field in config:
            values = [number(row[config[field]]) for row in rows]
            positive = [value for value in values if value is not None and value > 0]
            metrics[f"positive_{field}_coverage"] = len(positive) / len(rows)
            metrics[f"positive_{field}_sum"] = int(sum(positive))

    if "latitude" in config:
        valid = 0
        for row in rows:
            lat = number(row[config["latitude"]])
            lon = number(row[config["longitude"]])
            valid += lat is not None and lon is not None and 33 <= lat <= 39 and 124 <= lon <= 132
        metrics["valid_coordinate_coverage"] = valid / len(rows)

    if "cabinet_id" in config:
        cabinet_ids = [row[config["cabinet_id"]].strip() for row in rows]
        nonempty = [value for value in cabinet_ids if value]
        metrics["cabinet_id_coverage"] = len(nonempty) / len(rows)
        metrics["unique_cabinet_ids"] = len(set(nonempty))

    if "installation_date" in config:
        years = [date_year(row[config["installation_date"]]) for row in rows]
        plausible = [year for year in years if year is not None and year >= 1950]
        metrics["plausible_installation_year_coverage"] = len(plausible) / len(rows)
        metrics["installation_year_min"] = min(plausible) if plausible else None
        metrics["installation_year_max"] = max(plausible) if plausible else None
        metrics["year_1900_placeholder_count"] = sum(year == 1900 for year in years)

    return {
        "manifest": {
            "filename": path.name,
            "sha256": actual_sha,
            "byte_size": path.stat().st_size,
            "encoding": encoding,
            "rows": len(rows),
            "columns": columns,
            "schema_fingerprint": hashlib.sha256("|".join(columns).encode()).hexdigest(),
            "official_source": config["url"],
            "tracked_in_git": False,
        },
        "metrics": metrics,
    }


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    REPORT.mkdir(parents=True, exist_ok=True)
    regions = {key: profile(key, config) for key, config in SOURCES.items()}
    result = {
        "version": "0.23",
        "decision": "MEANINGFUL_WITH_ASSET_ROLE_ONLY",
        "claim_boundary": "Municipal asset applicability only; not AMI field-fault accuracy or operational effect.",
        "regions": regions,
        "evidence_architecture": {
            "municipal_regions_total": 11,
            "new_regions": ["SEONGNAM", "CHUNGJU", "GUNPO", "TONGYEONG"],
            "new_predictive_tuning": 0,
            "same_model_nationwide_claim": False,
            "raw_values_exported": False,
        },
    }
    (DATA / "v23_regional_file_evidence.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# LightGuard v0.23 Data.go.kr Regional File-Data Expansion",
        "",
        "## Decision",
        "",
        "- Overall: **MEANINGFUL_WITH_ASSET_ROLE_ONLY**",
        "- New municipalities: Seongnam, Chungju, Gunpo, Tongyeong.",
        "- Direct file downloads: approval-free Data.go.kr CSV content URLs.",
        "- Predictive retuning: 0.",
        "- Boundary: asset applicability only; no AMI truth or field-fault performance claim.",
        "",
    ]
    for key, config in SOURCES.items():
        metrics = regions[key]["metrics"]
        lines.extend([
            f"## {config['region']} - {metrics['role']}",
            "",
            f"- Records / unique IDs: {metrics['records']:,} / {metrics['unique_ids']:,}",
            f"- ID coverage: {metrics['id_coverage']:.2%}",
        ])
        if "valid_coordinate_coverage" in metrics:
            lines.append(f"- Valid coordinate coverage: {metrics['valid_coordinate_coverage']:.2%}")
        if "positive_pole_count_coverage" in metrics:
            lines.append(f"- Positive pole-count coverage: {metrics['positive_pole_count_coverage']:.2%}")
        if "positive_lamp_count_coverage" in metrics:
            lines.append(f"- Positive lamp-count coverage: {metrics['positive_lamp_count_coverage']:.2%}")
        if "cabinet_id_coverage" in metrics:
            lines.append(f"- Cabinet-link coverage: {metrics['cabinet_id_coverage']:.2%}")
        if "plausible_installation_year_coverage" in metrics:
            lines.append(f"- Plausible installation-year coverage: {metrics['plausible_installation_year_coverage']:.2%}")
        lines.extend([
            "- Value: LightGuard asset/cabinet/spatial intake contract can be configured for this municipality.",
            "- Limitation: no cabinet-linked AMI or adjudicated fault outcome in this file.",
            "",
        ])
    lines.extend([
        "## Claim-safe conclusion",
        "",
        "The four sources widen municipal asset-contract coverage but do not add AMI ground truth. They support modular regional onboarding and workload-denominator construction, not nationwide detector performance or realized maintenance benefit.",
        "",
    ])
    (REPORT / "v23_regional_file_expansion.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": "BUILT", "decision": result["decision"], "regions": 4}, ensure_ascii=False))


if __name__ == "__main__":
    main()
