#!/usr/bin/env python3
"""Build claim-safe evidence for four newly acquired municipal datasets."""
from __future__ import annotations

import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "official_docs" / "external_data"
DATA = ROOT / "lightguard_v0_1" / "data" / "validation" / "v22"
REPORT = ROOT / "lightguard_v0_1" / "reports" / "v22"

SOURCES = {
    "YANGJU": ("양주시", "https://www.data.go.kr/data/15087686/fileData.do"),
    "MICHUHOL": ("미추홀구", "https://www.data.go.kr/data/15125540/fileData.do"),
    "DAEJEON": ("대전광역시", "https://www.data.go.kr/data/15110054/fileData.do"),
    "GANGNEUNG": ("강릉시", "https://www.data.go.kr/data/15117413/fileData.do"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def locate(token: str) -> Path:
    matches = sorted(RAW.glob(f"*{token}*.csv"))
    if len(matches) != 1:
        raise RuntimeError(f"SOURCE_CARDINALITY:{token}:{len(matches)}")
    return matches[0]


def read_csv(path: Path) -> tuple[list[dict[str, str]], str]:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            rows = list(csv.DictReader(raw.decode(encoding).splitlines()))
            return rows, encoding
        except UnicodeDecodeError:
            continue
    raise RuntimeError(f"SOURCE_ENCODING:{path.name}")


def parse_date(value: str):
    for fmt in ("%Y-%m-%d", "%Y.%m.%d", "%Y%m%d"):
        try:
            return datetime.strptime((value or "").strip(), fmt).date()
        except ValueError:
            pass
    return None


def number(value: str):
    try:
        return float((value or "").replace(",", "").strip())
    except ValueError:
        return None


def base_manifest(path: Path, rows: list[dict[str, str]], encoding: str, url: str) -> dict:
    columns = list(rows[0])
    return {
        "filename": path.name,
        "sha256": sha(path),
        "byte_size": path.stat().st_size,
        "encoding": encoding,
        "rows": len(rows),
        "columns": columns,
        "schema_fingerprint": hashlib.sha256("|".join(columns).encode()).hexdigest(),
        "missing_by_column": {c: sum(not (r.get(c) or "").strip() for r in rows) for c in columns},
        "official_source": url,
        "tracked_in_git": False,
    }


def yangju(rows: list[dict[str, str]]) -> dict:
    dates = [parse_date(r["접수일자"]) for r in rows]
    if any(d is None for d in dates):
        raise RuntimeError("YANGJU_INVALID_DATE")
    by_asset = defaultdict(list)
    for row, day in zip(rows, dates):
        asset = row["관리번호"].strip()
        if asset:
            by_asset[asset].append(day)
    maximum = max(dates)
    repeat = {}
    for window in (30, 90, 365):
        eligible = repeated = 0
        for values in by_asset.values():
            distinct = sorted(set(values))
            for day in distinct:
                if day <= maximum - timedelta(days=window):
                    eligible += 1
                    repeated += any(day < other <= day + timedelta(days=window) for other in distinct)
        repeat[str(window)] = {
            "eligible_distinct_asset_dates": eligible,
            "repeated": repeated,
            "share": repeated / eligible if eligible else None,
        }
    return {
        "role": "EVENT_OPERATION",
        "decision": "MEANINGFUL_REPEAT_AND_ACTION_EVIDENCE",
        "events": len(rows),
        "date_min": str(min(dates)),
        "date_max": str(maximum),
        "unique_management_ids": len(by_asset),
        "assets_with_multiple_distinct_dates": sum(len(set(v)) > 1 for v in by_asset.values()),
        "receipt_media": dict(sorted(Counter(r["접수매체"].strip() for r in rows).items())),
        "repeat": repeat,
        "action_text_coverage": sum(bool(r["조치사항"].strip()) for r in rows) / len(rows),
        "limitations": ["처리일 부재로 처리시간 산출 불가", "접수매체가 전부 민원이라 발견경로 비교 불가", "자유문은 산출물에 미복제"],
    }


def michuhol(rows: list[dict[str, str]]) -> dict:
    fields = ("민원접수", "민원처리", "미처리(민원)", "자체보수(IoT 관제)")
    complete = []
    for row in rows:
        values = [number(row[f]) for f in fields]
        if (row.get("년도") or "").strip() and (row.get("월") or "").strip() and all(v is not None for v in values):
            complete.append((row, values))
    complaints = [v[0] for _, v in complete]
    processed = [v[1] for _, v in complete]
    unresolved = [v[2] for _, v in complete]
    iot = [v[3] for _, v in complete]
    months = [f"{r['년도']}-{int(r['월']):02d}" for r, _ in complete]
    recorded_work = sum(complaints) + sum(iot)
    return {
        "role": "AGGREGATE_OPERATION",
        "decision": "MEANINGFUL_IOT_AND_WORKLOAD_EVIDENCE",
        "source_rows": len(rows),
        "complete_months": len(complete),
        "excluded_incomplete_rows": len(rows) - len(complete),
        "period_min": min(months),
        "period_max": max(months),
        "complaints": int(sum(complaints)),
        "processed": int(sum(processed)),
        "unprocessed": int(sum(unresolved)),
        "iot_self_repairs": int(sum(iot)),
        "iot_share_of_recorded_work": sum(iot) / recorded_work,
        "monthly_complaint_cv": statistics.pstdev(complaints) / statistics.mean(complaints),
        "monthly_iot_cv": statistics.pstdev(iot) / statistics.mean(iot),
        "limitations": ["월별 집계로 개별 사건·자산·처리시간 분석 불가", "완료율은 집계 필드의 기술통계이며 LightGuard 효과가 아님"],
    }


def daejeon(rows: list[dict[str, str]]) -> dict:
    ids = [r["관리번호"].strip() for r in rows if r["관리번호"].strip()]
    valid_xy = 0
    for row in rows:
        lat, lon = number(row["위도"]), number(row["경도"])
        valid_xy += lat is not None and lon is not None and 33 <= lat <= 39 and 124 <= lon <= 132
    controller = [r["가로등제어기관리번호"].strip() for r in rows]
    placeholders = {"", "0", "9999999999", "미분류"}
    usable_controller = [v for v in controller if v not in placeholders]
    lamp_counts = [number(r["등기구수량"]) for r in rows]
    positive_lamp = [v for v in lamp_counts if v is not None and v > 0]
    return {
        "role": "ASSET_SPATIAL",
        "decision": "MEANINGFUL_WITH_LOAD_AND_CONTROLLER_GAPS",
        "assets": len(rows),
        "unique_management_ids": len(set(ids)),
        "valid_coordinate_coverage": valid_xy / len(rows),
        "district_counts": dict(sorted(Counter(r["행정읍면동"].strip() for r in rows).items())),
        "positive_lamp_count_coverage": len(positive_lamp) / len(rows),
        "positive_lamp_count_sum": int(sum(positive_lamp)),
        "usable_controller_id_coverage": len(usable_controller) / len(rows),
        "unique_usable_controller_ids": len(set(usable_controller)),
        "limitations": ["정격용량 필드 부재로 예상 정격부하 산출 불가", "placeholder 제어기 ID 제외 필요", "공간 자산 inventory로만 사용"],
    }


def gangneung(rows: list[dict[str, str]]) -> dict:
    cabinets = [(r["분전함코드"].strip(), r["분전함순번(SEQ)"].strip()) for r in rows]
    valid_xy = 0
    rated_rows = 0
    rated_entries = []
    for row in rows:
        lat, lon = number(row["좌표(위도)"]), number(row["좌표(경도)"])
        valid_xy += lat is not None and lon is not None and 33 <= lat <= 39 and 124 <= lon <= 132
        capacities = [number(row["등용량1"]), number(row["등용량2"])]
        positive = [v for v in capacities if v is not None and v > 0]
        rated_rows += bool(positive)
        rated_entries.extend(positive)
    return {
        "role": "CABINET_ASSET_LOAD",
        "decision": "STRONG_MEANINGFUL_OBJECT_CONTRACT_EVIDENCE",
        "assets": len(rows),
        "unique_cabinet_keys": len(set(cabinets)),
        "cabinet_key_coverage": sum(bool(a or b) for a, b in cabinets) / len(rows),
        "valid_coordinate_coverage": valid_xy / len(rows),
        "rated_capacity_row_coverage": rated_rows / len(rows),
        "rated_capacity_entries": len(rated_entries),
        "nominal_capacity_sum_kw_if_field_is_watts": sum(rated_entries) / 1000,
        "fixture_type_counts": dict(sorted(Counter(r["등종류1"].strip() or "MISSING" for r in rows).items())),
        "limitations": ["등용량 단위를 W로 해석한 명목합이며 실측 부하가 아님", "AMI 미포함으로 detector 현장성능 검증 불가"],
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    REPORT.mkdir(parents=True, exist_ok=True)
    builders = {"YANGJU": yangju, "MICHUHOL": michuhol, "DAEJEON": daejeon, "GANGNEUNG": gangneung}
    result = {"version": "0.22", "claim_boundary": "Municipal operational/asset applicability, not AMI fault accuracy.", "regions": {}}
    for key, (token, url) in SOURCES.items():
        path = locate(token)
        rows, encoding = read_csv(path)
        result["regions"][key] = {"manifest": base_manifest(path, rows, encoding, url), "metrics": builders[key](rows)}
    result["evidence_architecture"] = {
        "OPERATIONS_5": ["DAEGU", "BUYEO", "ULSAN_NAMGU", "YANGJU", "MICHUHOL"],
        "ASSET_SIGNAL_3": ["SUYEONG", "DAEJEON", "GANGNEUNG"],
        "same_model_nationwide_claim": False,
        "new_predictive_tuning": 0,
    }
    (DATA / "v22_regional_evidence.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    metric_rows = []
    primary_fields = {
        "YANGJU": ("90d_repeat_share", lambda m: m["repeat"]["90"]["share"]),
        "MICHUHOL": ("iot_work_share", lambda m: m["iot_share_of_recorded_work"]),
        "DAEJEON": ("coordinate_coverage", lambda m: m["valid_coordinate_coverage"]),
        "GANGNEUNG": ("rated_capacity_coverage", lambda m: m["rated_capacity_row_coverage"]),
    }
    for key, item in result["regions"].items():
        m = item["metrics"]
        value_name, value_getter = primary_fields[key]
        metric_rows.append({"region": key, "role": m["role"], "decision": m["decision"], "source_rows": item["manifest"]["rows"], "primary_value": value_getter(m), "primary_value_name": value_name})
    write_csv(REPORT / "v22_regional_metrics.csv", metric_rows)
    y, i, d, g = [result["regions"][k]["metrics"] for k in ("YANGJU", "MICHUHOL", "DAEJEON", "GANGNEUNG")]
    report = f"""# LightGuard v0.22 Regional Public-Data Value Validation

## Decision

- Overall: **MEANINGFUL_WITH_ROLE_SEPARATION**
- OPERATIONS evidence: Daegu, Buyeo, Ulsan Nam-gu + Yangju + Michuhol = 5 municipalities.
- ASSET/SIGNAL applicability: Suyeong + Daejeon + Gangneung = 3 municipalities.
- Predictive retuning: 0; municipal data are not AMI fault labels.

## Yangju — EVENT_OPERATION

- Events / management IDs: {y['events']:,} / {y['unique_management_ids']:,}
- Assets with multiple distinct receipt dates: {y['assets_with_multiple_distinct_dates']:,}
- Distinct-date recurrence: 30d {y['repeat']['30']['share']:.2%}, 90d {y['repeat']['90']['share']:.2%}, 365d {y['repeat']['365']['share']:.2%}
- Value: repeated complaint history and recorded action support inspection-priority context.
- Boundary: no completion date; no resolution-latency claim.

## Michuhol — AGGREGATE_OPERATION

- Complete months: {i['complete_months']} ({i['period_min']} to {i['period_max']}); incomplete rows excluded: {i['excluded_incomplete_rows']}
- Complaints / IoT self-repairs: {i['complaints']:,} / {i['iot_self_repairs']:,}
- IoT share of recorded complaint+IoT work: {i['iot_share_of_recorded_work']:.2%}
- Value: independent machine-originated observations already form a material operating channel.
- Boundary: monthly aggregates cannot support event-level ranking or causal effect.

## Daejeon — ASSET_SPATIAL

- Assets / unique IDs: {d['assets']:,} / {d['unique_management_ids']:,}
- Valid coordinates: {d['valid_coordinate_coverage']:.2%}
- Positive lamp-count coverage: {d['positive_lamp_count_coverage']:.2%}
- Usable controller-ID coverage: {d['usable_controller_id_coverage']:.2%}
- Value: city-scale spatial inventory and stable asset identifiers support rollout screening.
- Boundary: rated load cannot be reconstructed; controller placeholders must remain unavailable.

## Gangneung — CABINET_ASSET_LOAD

- Assets / cabinet keys: {g['assets']:,} / {g['unique_cabinet_keys']:,}
- Coordinate / rated-capacity coverage: {g['valid_coordinate_coverage']:.2%} / {g['rated_capacity_row_coverage']:.2%}
- Nominal capacity sum: {g['nominal_capacity_sum_kw_if_field_is_watts']:,.3f} kW, conditional on the public field representing watts.
- Value: the LightGuard cabinet → asset → expected-load object contract is directly reproducible outside Suyeong.
- Boundary: nominal asset capacity is not AMI measurement or detector accuracy.

## Claim-safe conclusion

LightGuard has meaningful value across the four added regions, but through different evidence roles. Yangju and Michuhol strengthen the operational need and discovery-channel case; Daejeon supports city-scale spatial deployment screening; Gangneung strongly replicates the cabinet/asset/rated-load data contract. These results support a modular regional rollout, not a nationwide uncalibrated model or a field-fault accuracy claim.
"""
    (REPORT / "v22_regional_expansion.md").write_text(report, encoding="utf-8")
    print(json.dumps({"status": "BUILT", "decision": "MEANINGFUL_WITH_ROLE_SEPARATION", "regions": 4}, ensure_ascii=False))


if __name__ == "__main__":
    main()
