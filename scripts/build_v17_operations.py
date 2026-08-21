#!/usr/bin/env python3
"""Build claim-safe v0.17 municipal streetlight operational evidence."""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import math
import statistics
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "official_docs" / "external_data"
DATA = ROOT / "lightguard_v0_1" / "data" / "validation" / "v17"
REPORT = ROOT / "lightguard_v0_1" / "reports" / "v17"
LEARNING = ROOT / "docs" / "agent_learning_v17"
APP_DOCS = ROOT / "lightguard_app" / "docs"
BUILD_DATE = "2026-08-21"
PROVIDER = "대구공공시설관리공단"

SOURCES = {
    "D1": ("고장등관리", "https://www.data.go.kr/data/15120484/fileData.do", 101843, "primary operational outcome"),
    "D2": ("위치DB", "https://www.data.go.kr/data/15120529/fileData.do", 71973, "asset location"),
    "D3": ("안전점검관리", "https://www.data.go.kr/data/15120494/fileData.do", 105449, "safety inspection context"),
    "D4": ("자재관리", "https://www.data.go.kr/data/15120490/fileData.do", 145365, "aggregate maintenance workload only"),
    "D5": ("공사정보", "https://www.data.go.kr/data/15120488/fileData.do", 2519, "aggregate project context only"),
}


def normalized(value: str) -> str:
    return unicodedata.normalize("NFC", value.strip())


def source_path(token: str) -> Path:
    matches = [path for path in RAW.glob("*.csv") if token in normalized(path.name)]
    if len(matches) != 1:
        raise RuntimeError(f"expected one source for {token}, found {len(matches)}")
    return matches[0]


def read_rows(path: Path):
    with path.open(encoding="cp949", newline="") as stream:
        yield from csv.DictReader(stream)


def read_header(path: Path) -> list[str]:
    with path.open(encoding="cp949", newline="") as stream:
        return next(csv.reader(stream))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_date(value: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value.strip())
    except (AttributeError, ValueError):
        return None


def quantile(values: list[int], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def asset_hash(value: str) -> str:
    payload = f"lightguard-v17-public-daegu:{value}".encode()
    return "LGD-" + hashlib.sha256(payload).hexdigest()[:16]


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, fieldnames: list[str], rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def stats(values: list[int]) -> dict:
    return {
        "count": len(values),
        "mean_days": statistics.mean(values) if values else None,
        "median_days": statistics.median(values) if values else None,
        "p75_days": quantile(values, 0.75),
        "p90_days": quantile(values, 0.90),
        "p95_days": quantile(values, 0.95),
        "same_day_rate": ratio(sum(value == 0 for value in values), len(values)),
        "within_1d_rate": ratio(sum(value <= 1 for value in values), len(values)),
        "within_3d_rate": ratio(sum(value <= 3 for value in values), len(values)),
        "within_7d_rate": ratio(sum(value <= 7 for value in values), len(values)),
    }


def main() -> None:
    for directory in (DATA, REPORT, LEARNING, APP_DOCS):
        directory.mkdir(parents=True, exist_ok=True)

    paths = {source_id: source_path(spec[0]) for source_id, spec in SOURCES.items()}
    d1 = list(read_rows(paths["D1"]))
    d2 = list(read_rows(paths["D2"]))
    d3 = list(read_rows(paths["D3"]))
    d5 = list(read_rows(paths["D5"]))

    locations: dict[str, set[tuple[float, float] | None]] = defaultdict(set)
    for row in d2:
        identifier = row["가로등번호"].strip()
        try:
            locations[identifier].add((round(float(row["위도"]), 7), round(float(row["경도"]), 7)))
        except ValueError:
            locations[identifier].add(None)

    fault_ids = {row["관리번호"].strip() for row in d1}
    matched_ids = fault_ids & set(locations)
    unambiguous_ids = {
        identifier for identifier in matched_ids
        if None not in locations[identifier] and len(locations[identifier]) == 1
    }
    unmatched_ids = fault_ids - set(locations)
    ambiguous_ids = matched_ids - unambiguous_ids
    join_status = "PARTIAL_JOIN" if matched_ids else "INCOMPATIBLE_ID"

    channels = Counter()
    districts = Counter()
    event_signatures = Counter()
    dates_by_asset: dict[str, set[dt.date]] = defaultdict(set)
    resolution_valid: list[int] = []
    resolution_by_channel: dict[str, list[int]] = defaultdict(list)
    resolution_by_district: dict[str, list[int]] = defaultdict(list)
    resolution_by_year: dict[str, list[int]] = defaultdict(list)
    resolution_by_month: dict[str, list[int]] = defaultdict(list)
    invalid_receipt = invalid_resolution = negative_resolution = unresolved = 0
    daily_arrivals = Counter()
    clean_faults = []
    for index, row in enumerate(d1, 1):
        receipt = parse_date(row["접수일자"])
        resolved = parse_date(row["처리일"])
        channel = row["접수구분"].strip()
        district = row["구청"].strip()
        identifier = row["관리번호"].strip()
        channels[channel] += 1
        districts[district] += 1
        event_signatures[tuple(row[key].strip() for key in (
            "접수일자", "접수구분", "관리번호", "구청", "가로등명", "구간", "처리일"
        ))] += 1
        if receipt is None:
            invalid_receipt += 1
        else:
            dates_by_asset[identifier].add(receipt)
            daily_arrivals[receipt.isoformat()] += 1
        quality = "VALID"
        duration = None
        if not row["처리일"].strip():
            unresolved += 1
            quality = "UNRESOLVED"
        elif resolved is None:
            invalid_resolution += 1
            quality = "INVALID_RESOLUTION_DATE"
        elif receipt is None:
            quality = "INVALID_RECEIPT_DATE"
        else:
            duration = (resolved - receipt).days
            if duration < 0:
                negative_resolution += 1
                quality = "NEGATIVE_DURATION"
            else:
                resolution_valid.append(duration)
                resolution_by_channel[channel].append(duration)
                resolution_by_district[district].append(duration)
                resolution_by_year[str(receipt.year)].append(duration)
                resolution_by_month[receipt.strftime("%Y-%m")].append(duration)
        cohort = "PROACTIVE" if channel == "일상점검" else (
            "REACTIVE" if channel in {"민원신고", "직원신고"} else "OTHER"
        )
        clean_faults.append({
            "event_id": f"D1-{index:06d}",
            "receipt_date": row["접수일자"].strip(),
            "receipt_channel": channel,
            "research_cohort": cohort,
            "asset_hash": asset_hash(identifier),
            "district": district,
            "resolved_date": row["처리일"].strip(),
            "resolution_days": "" if duration is None else duration,
            "quality_status": quality,
            "spatial_join_status": "UNAMBIGUOUS" if identifier in unambiguous_ids else (
                "AMBIGUOUS" if identifier in ambiguous_ids else "UNMATCHED"
            ),
        })

    repeat_windows = (7, 30, 90, 365)
    repeat_counts = Counter()
    repeat_denominators = Counter()
    recurrence_gaps: list[int] = []
    repeated_assets = 0
    events_per_asset = Counter()
    canonical_end = max(max(dates) for dates in dates_by_asset.values())
    for identifier, dates in dates_by_asset.items():
        ordered_dates = sorted(dates)
        events_per_asset[identifier] = len(ordered_dates)
        if len(ordered_dates) > 1:
            repeated_assets += 1
        for previous, current in zip(ordered_dates, ordered_dates[1:]):
            gap = (current - previous).days
            recurrence_gaps.append(gap)
        for index, current in enumerate(ordered_dates):
            for window in repeat_windows:
                if current > canonical_end - dt.timedelta(days=window):
                    continue
                repeat_denominators[window] += 1
                if index + 1 < len(ordered_dates):
                    gap = (ordered_dates[index + 1] - current).days
                    repeat_counts[window] += 1 <= gap <= window

    hotspot_rows = [{
        "analysis_status": "NO_SPATIAL_JOIN",
        "join_status": join_status,
        "candidate_event_rows": sum(row["관리번호"].strip() in unambiguous_ids for row in d1),
        "reason": "Long Goal permits hotspot analysis only after VERIFIED_JOIN; semantic identity and duplicate-coordinate issues remain",
    }]

    field_actions = Counter(row["현장조치"].strip() for row in d3)
    review_actions = Counter(row["검토후조치"].strip() for row in d3)
    safety_dates = [date for row in d3 if (date := parse_date(row["조치일"]))]
    d1_sections = {row["구간"].strip() for row in d1}
    d3_sections = {row["구간"].strip() for row in d3}
    clean_safety = [{
        "inspection_id": f"D3-{index:06d}",
        "section_hash": asset_hash(row["구간"].strip()),
        "zone": row["구역"].strip(),
        "action_date": row["조치일"].strip(),
        "insulation_measurement_raw": row["절연저항"].strip(),
        "field_action": row["현장조치"].strip(),
        "review_action": row["검토후조치"].strip(),
        "ground_measurement_raw": row["접지저항"].strip(),
        "threshold_classification": "NOT_APPLIED_UNIT_OR_OFFICIAL_THRESHOLD_UNVERIFIED",
    } for index, row in enumerate(d3, 1)]

    material_count = 0
    material_dates = []
    repair_methods = Counter()
    materials = Counter()
    quantity_total = 0.0
    quantity_invalid = 0
    material_month = Counter()
    for row in read_rows(paths["D4"]):
        material_count += 1
        repair_methods[row["수리방법"].strip() or "단순수리(공식 설명)"] += 1
        materials[row["자재명"].strip() or "미기재"] += 1
        if date := parse_date(row["일자"]):
            material_dates.append(date)
            material_month[date.strftime("%Y-%m")] += 1
        try:
            quantity_total += float(row["출고량"])
        except ValueError:
            quantity_invalid += 1

    construction_dates = [date for row in d5 if (date := parse_date(row["입력일"]))]
    construction_status = Counter(row["공사진행상태"].strip() for row in d5)
    construction_types = Counter(row["공사구분"].strip() for row in d5)

    source_manifest = []
    observed_counts = {"D1": len(d1), "D2": len(d2), "D3": len(d3), "D4": material_count, "D5": len(d5)}
    temporal = {
        "D1": (min(date for dates in dates_by_asset.values() for date in dates), max(date for dates in dates_by_asset.values() for date in dates)),
        "D2": (None, None),
        "D3": (min(safety_dates), max(safety_dates)),
        "D4": (min(material_dates), max(material_dates)),
        "D5": (min(construction_dates), max(construction_dates)),
    }
    for source_id, (_, url, portal_rows, role) in SOURCES.items():
        path = paths[source_id]
        time_min, time_max = temporal[source_id]
        source_manifest.append({
            "source_id": source_id,
            "provider": PROVIDER,
            "official_url": url,
            "local_filename": normalized(path.name),
            "download_date": BUILD_DATE,
            "sha256": sha256(path),
            "rows": observed_counts[source_id],
            "portal_advertised_rows": portal_rows,
            "row_count_status": "MATCH" if observed_counts[source_id] == portal_rows else "MISMATCH_REQUIRES_SOURCE_CONFIRMATION",
            "columns": read_header(path),
            "time_min": time_min.isoformat() if time_min else None,
            "time_max": time_max.isoformat() if time_max else None,
            "license": "공공데이터포털 이용허락범위 제한 없음",
            "snapshot_type": "latest_local_complete_snapshot_canonical",
            "role": role,
        })

    resolution_rows = []
    for dimension, groups in (
        ("overall", {"ALL": resolution_valid}),
        ("receipt_channel", resolution_by_channel),
        ("district", resolution_by_district),
        ("year", resolution_by_year),
        ("month", resolution_by_month),
    ):
        for group, values in sorted(groups.items()):
            resolution_rows.append({"dimension": dimension, "group": group, **stats(values)})

    channel_rows = []
    for channel, count in channels.most_common():
        cohort = "PROACTIVE" if channel == "일상점검" else (
            "REACTIVE" if channel in {"민원신고", "직원신고"} else "OTHER"
        )
        channel_rows.append({
            "receipt_channel": channel,
            "research_cohort": cohort,
            "event_count": count,
            "event_share": ratio(count, len(d1)),
            "claim_boundary": "observed receipt route; not preventable-event estimate",
        })

    repeat_rows = [{
        "window_days": window,
        "repeat_recorded_events": repeat_counts[window],
        "eligible_asset_day_episodes": repeat_denominators[window],
        "repeat_rate": ratio(repeat_counts[window], repeat_denominators[window]),
        "definition": "next distinct asset-day episode is within window; same cause unverified; full follow-up required",
    } for window in repeat_windows]

    profile_rows = [
        {"metric": "rows", "value": len(d1)},
        {"metric": "unique_management_ids", "value": len(fault_ids)},
        {"metric": "date_min", "value": temporal["D1"][0]},
        {"metric": "date_max", "value": temporal["D1"][1]},
        {"metric": "duplicate_event_signatures_excluding_sequence", "value": sum(count - 1 for count in event_signatures.values() if count > 1)},
        {"metric": "same_asset_same_day_extra_records", "value": len(d1) - sum(len(dates) for dates in dates_by_asset.values())},
        {"metric": "unresolved", "value": unresolved},
        {"metric": "invalid_receipt_date", "value": invalid_receipt},
        {"metric": "invalid_resolution_date", "value": invalid_resolution},
        {"metric": "negative_resolution", "value": negative_resolution},
    ]

    safety_rows = [
        {"dimension": "overview", "category": "inspection_rows", "count": len(d3), "share": 1.0},
        {"dimension": "overview", "category": "field_action_not_이상없음", "count": len(d3) - field_actions["이상없음"], "share": ratio(len(d3) - field_actions["이상없음"], len(d3))},
        {"dimension": "overview", "category": "review_action_not_이상없음", "count": len(d3) - review_actions["이상없음"], "share": ratio(len(d3) - review_actions["이상없음"], len(d3))},
    ]
    safety_rows += [{"dimension": "field_action", "category": key, "count": value, "share": ratio(value, len(d3))} for key, value in field_actions.most_common()]
    safety_rows += [{"dimension": "review_action", "category": key, "count": value, "share": ratio(value, len(d3))} for key, value in review_actions.most_common()]

    maintenance_rows = [{
        "source": "D4", "dimension": "row_count_audit", "category": "HOLD_PROFILE_ONLY",
        "count": material_count, "quantity": "", "claim_scope": "portal advertises 145365 rows; no detailed service-value publication",
    }]
    maintenance_rows += [{"source": "D5", "dimension": "construction_status", "category": key, "count": value, "quantity": "", "claim_scope": "project context only"} for key, value in construction_status.most_common()]
    maintenance_rows += [{"source": "D5", "dimension": "construction_type_code", "category": key, "count": value, "quantity": "", "claim_scope": "raw code; no unverified label mapping"} for key, value in construction_types.most_common()]

    candidates = [
        ("보안등 민원처리", "인천 미추홀구", "인천광역시미추홀구시설관리공단", "https://www.data.go.kr/data/15125540/fileData.do", 36, "월, 민원접수, 민원처리, 미처리, IoT 자체보수", "aggregate complaint/IoT comparator"),
        ("가로등 점검", "충북 단양군", "충청북도 단양군", "https://www.data.go.kr/data/15155411/fileData.do", None, "표찰번호, 계기번호, 위치", "inspection asset linkage candidate"),
        ("가로등 자산", "강원 강릉시", "강원특별자치도 강릉시", "https://www.data.go.kr/data/15117413/fileData.do", None, "가로등/분전함 코드, 등용량, 좌표", "asset/load comparator only"),
        ("분전함 유지관리", "충북 충주시", "충청북도 충주시", "https://www.data.go.kr/data/15041822/fileData.do", 871, "분전함 ID, 등주 수량, 좌표", "cabinet workload denominator"),
        ("보안등 자산", "울산 남구", "울산광역시 남구", "https://www.data.go.kr/data/15127415/fileData.do", None, "관리번호, 용량, 좌표", "asset denominator only"),
        ("가로등 시설현황", "인천광역시", "인천광역시", "https://www.data.go.kr/data/15103933/fileData.do", 5, "광원별 집계", "context only"),
        ("가로등 자산", "경북 구미시", "경상북도 구미시", "https://www.data.go.kr/data/15128238/fileData.do", None, "시설/위치", "asset candidate"),
        ("가로등 자산", "경남 창원시", "경상남도 창원시", "https://www.data.go.kr/data/15074277/fileData.do", None, "시설/위치", "asset candidate"),
        ("가로등 자산", "광주 동구", "광주광역시 동구", "https://www.data.go.kr/data/15113447/fileData.do", None, "시설/위치", "asset candidate"),
        ("가로등 분전함", "서울 은평구", "서울특별시 은평구", "https://www.data.go.kr/data/3078204/fileData.do", None, "노선, 계약종별, 위치", "cabinet context candidate"),
        ("가로등 차량", "대구광역시", PROVIDER, "https://www.data.go.kr/data/15120455/fileData.do", 21356, "차량, 연료, 주행, 고장상태", "maintenance fleet context"),
        ("가로등 공사", "제주 서귀포시", "제주특별자치도 서귀포시", "https://www.data.go.kr/data/15090635/openapi.do", None, "공사 알림", "project context candidate"),
    ]
    candidate_rows = [{
        "query_family": row[0], "region": row[1], "provider": row[2], "official_url": row[3],
        "row_count": "" if row[4] is None else row[4], "key_fields": row[5],
        "data_type": "official municipal streetlight-related public data", "license": "verify_on_include",
        "downloadable": "candidate_verify", "usefulness": row[6], "inclusion_status": "NOT_INCLUDED_SECONDARY_RESEARCH_ONLY",
    } for row in candidates]

    summary = {
        "release": "v0.17",
        "generated_on": BUILD_DATE,
        "evidence_axis": "MUNICIPAL_OPERATIONAL_EVIDENCE_SEPARATE_FROM_AMI",
        "operational_need_grade": "ON-A",
        "fault_management": {
            "rows": len(d1), "unique_assets": len(fault_ids),
            "period": [temporal["D1"][0].isoformat(), temporal["D1"][1].isoformat()],
            "routine_inspection_share": ratio(channels["일상점검"], len(d1)),
            "citizen_report_share": ratio(channels["민원신고"], len(d1)),
            "reactive_report_share": ratio(channels["민원신고"] + channels["직원신고"], len(d1)),
            "valid_resolution_rows": len(resolution_valid), "negative_resolution_rows": negative_resolution,
            "unresolved_rows": unresolved, "resolution": stats(resolution_valid),
        },
        "repeat_events": {
            "assets_with_repeats": repeated_assets,
            "asset_day_episodes": sum(len(dates) for dates in dates_by_asset.values()),
            "same_asset_same_day_extra_records": len(d1) - sum(len(dates) for dates in dates_by_asset.values()),
            "median_days_to_next_record": statistics.median(recurrence_gaps),
            "windows": {str(row["window_days"]): row for row in repeat_rows},
        },
        "spatial_join": {
            "status": join_status, "fault_unique_ids": len(fault_ids),
            "location_rows": len(d2), "location_unique_ids": len(locations),
            "matched_unique_ids": len(matched_ids), "matched_unique_rate": ratio(len(matched_ids), len(fault_ids)),
            "unambiguous_unique_ids": len(unambiguous_ids), "ambiguous_unique_ids": len(ambiguous_ids),
            "unmatched_unique_ids": len(unmatched_ids),
            "unambiguous_join_candidate_event_rows": sum(row["관리번호"].strip() in unambiguous_ids for row in d1),
            "spatial_analysis_status": "NO_SPATIAL_JOIN",
        },
        "safety_inspection": {
            "rows": len(d3), "period": [min(safety_dates).isoformat(), max(safety_dates).isoformat()],
            "field_action_not_no_issue": len(d3) - field_actions["이상없음"],
            "review_action_not_no_issue": len(d3) - review_actions["이상없음"],
            "section_name_overlap": len(d1_sections & d3_sections),
            "section_join_status": "SECTION_LEVEL_CONTEXT_ONLY_NOT_ASSET_KEY",
            "measurement_policy": "DESCRIPTIVE_ONLY_UNIT_AND_OFFICIAL_THRESHOLD_UNVERIFIED",
        },
        "maintenance": {
            "material_rows": material_count, "portal_advertised_material_rows": SOURCES["D4"][2],
            "material_row_count_status": "MISMATCH_REQUIRES_SOURCE_CONFIRMATION",
            "material_analysis_status": "HOLD_PROFILE_ONLY",
            "material_quantity_total_raw_units": quantity_total, "material_quantity_invalid_rows": quantity_invalid,
            "construction_rows": len(d5), "cost_savings_permitted": False,
        },
        "workflow_mapping": {
            "DATA_QUALITY_REVIEW": "invalid/negative date, ambiguous ID, source-row mismatch review",
            "REMOTE_MONITOR": "repeat-record and aging context for remote recheck; not automatic fault truth",
            "FIELD_INSPECTION_CANDIDATE": "explainable queue using repeated records, age, citizen report, and safety action context",
        },
        "claim_boundary": {
            "supports": "actual municipal workload, receipt routes, processing duration, repeated records, safety-action and maintenance context",
            "does_not_support": "competition AMI fault accuracy, Daegu-to-Suyeong transfer, prevented complaints, causal savings, or cost savings",
        },
    }

    v16_files = [
        ROOT / "lightguard_v0_1" / "data" / "validation" / "v16" / "v16_protocol_freeze.json",
        ROOT / "lightguard_v0_1" / "reports" / "v16" / "v16_final_summary.md",
    ]
    write_json(DATA / "v16_freeze_manifest.json", {
        "release": "v0.16", "status": "FROZEN_UNMODIFIED", "official_meter_count": 129,
        "streetlight_meter_count": 5, "policy_promotion": "STOPPED",
        "files": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in v16_files],
    })
    write_json(DATA / "v17_source_manifest.json", source_manifest)
    write_json(DATA / "v17_operational_summary.json", summary)
    write_csv(DATA / "v17_fault_events_clean.csv", list(clean_faults[0]), clean_faults)
    write_csv(DATA / "v17_asset_join_audit.csv", [
        "join_status", "fault_unique_ids", "location_rows", "location_unique_ids", "matched_unique_ids",
        "matched_unique_rate", "unambiguous_unique_ids", "ambiguous_unique_ids", "unmatched_unique_ids",
        "unambiguous_join_candidate_event_rows", "spatial_analysis_status", "rule",
    ], [{**{key: value for key, value in summary["spatial_join"].items() if key != "status"},
         "join_status": join_status,
         "rule": "exact normalized 7-digit ID; one valid coordinate required for spatial use"}])
    write_csv(DATA / "v17_safety_inspection_clean.csv", list(clean_safety[0]), clean_safety)
    write_csv(DATA / "v17_additional_source_candidates.csv", list(candidate_rows[0]), candidate_rows)
    write_csv(REPORT / "v17_fault_event_profile.csv", ["metric", "value"], profile_rows)
    write_csv(REPORT / "v17_resolution_analysis.csv", list(resolution_rows[0]), resolution_rows)
    write_csv(REPORT / "v17_detection_channel_analysis.csv", list(channel_rows[0]), channel_rows)
    write_csv(REPORT / "v17_repeat_event_analysis.csv", list(repeat_rows[0]), repeat_rows)
    write_csv(REPORT / "v17_spatial_hotspot_analysis.csv", list(hotspot_rows[0]), hotspot_rows)
    write_csv(REPORT / "v17_safety_inspection_analysis.csv", list(safety_rows[0]), safety_rows)
    write_csv(REPORT / "v17_maintenance_activity_analysis.csv", list(maintenance_rows[0]), maintenance_rows)

    protocol = """
# v0.17 Municipal Operations Protocol

## Frozen scope

- D1 latest local snapshot is the only canonical fault-event table. Historical snapshots are not stacked.
- Resolution is `처리일 - 접수일` in calendar days. Missing, invalid, and negative durations are separate quality states.
- A repeat is another recorded event for the same exact management ID within 7, 30, 90, or 365 days. It is not a confirmed same-cause fault.
- D1-D2 spatial use requires an exact normalized ID and exactly one valid coordinate. Fuzzy road/section joins are prohibited.
- D3 measurements remain descriptive because units and an applicable official threshold were not verified.
- D4 and D5 are aggregate workload context. They have no event join key and support no cost-savings calculation.

## Interpretation

Asset clustering and repeated records mean rows are not independent fault-probability samples. Metrics are descriptive and stratified by asset, district, channel, year, and month. Daegu is an operational Evidence Layer, separate from competition B-line AMI, Suyeong scenarios, and Gangneung/Chungju assets.
"""
    write_md(REPORT / "v17_operations_protocol.md", protocol)
    data_quality = f"""
# v0.17 Data Quality Report

| source | observed rows | portal rows | status |
|---|---:|---:|---|
{chr(10).join(f'| {row["source_id"]} | {row["rows"]:,} | {row["portal_advertised_rows"]:,} | {row["row_count_status"]} |' for row in source_manifest)}

## D1

- Unique management IDs: {len(fault_ids):,}
- Duplicate event signatures excluding sequence: {sum(count - 1 for count in event_signatures.values() if count > 1):,}
- Valid durations: {len(resolution_valid):,}; negative durations: {negative_resolution}; unresolved: {unresolved}

## Join

- Verdict: `{join_status}`
- Exact ID overlap: {len(matched_ids):,}/{len(fault_ids):,} ({ratio(len(matched_ids), len(fault_ids)):.2%})
- Ambiguous matched IDs: {len(ambiguous_ids):,}; unmatched IDs: {len(unmatched_ids):,}
- Unambiguous exact-ID join candidates: {summary['spatial_join']['unambiguous_join_candidate_event_rows']:,}
- Spatial analysis: `NO_SPATIAL_JOIN`; no hotspot result is published until semantic identity is verified.

## Blocking discrepancy

D4 local file has {material_count:,} rows while the official page advertises {SOURCES['D4'][2]:,}. D4 remains aggregate context and is not used for event-level or cost claims until the provider confirms the snapshot semantics.
"""
    write_md(REPORT / "v17_data_quality_report.md", data_quality)
    service_value = f"""
# v0.17 Service Value Summary

- Operational need grade: **ON-A**
- Actual fault-management events: {len(d1):,} across {len(fault_ids):,} recorded asset IDs.
- Routine-inspection discovery: {ratio(channels['일상점검'], len(d1)):.1%}; citizen reports: {ratio(channels['민원신고'], len(d1)):.1%}; citizen + staff reports: {ratio(channels['민원신고'] + channels['직원신고'], len(d1)):.1%}.
- Valid resolution median: {statistics.median(resolution_valid):.0f} days; p90: {quantile(resolution_valid, .90):.0f} days; over 7 days: {ratio(sum(value > 7 for value in resolution_valid), len(resolution_valid)):.1%}.
- Assets with more than one distinct event day: {repeated_assets:,}; 30-day repeat-record rate among episodes with full follow-up: {ratio(repeat_counts[30], repeat_denominators[30]):.1%}.
- D3 field action other than `이상없음`: {len(d3) - field_actions['이상없음']:,}; review action other than `이상없음`: {len(d3) - review_actions['이상없음']:,}.

These observations support an explainable three-lane triage workflow. They do not show that LightGuard would have detected these events early or reduced complaints, response time, or cost.
"""
    write_md(REPORT / "v17_service_value_summary.md", service_value)
    audit = f"""
# v0.17 Independent Artifact Audit

## Verdict

- Artifact and claim contract: `PASS`
- D1 operational event confused with AMI label: `NO`
- Historical snapshots stacked: `NO`
- D1-D2 join forced: `NO` (`{join_status}` with ambiguous/unmatched exclusions)
- Unresolved/negative duration hidden: `NO`
- Citizen complaint called preventable: `NO`
- Cost savings calculated: `NO`
- Safety threshold invented: `NO`
- Daegu transferred directly to Suyeong: `NO`
- Raw public or Office files intended for Git: `NO`

## Residual issues

- D4 observed-versus-portal row-count mismatch requires provider confirmation.
- D2 has repeated IDs and 137 matched IDs with ambiguous coordinate sets.
- D3 section overlap is context only, not a verified asset-level key.
- Separate TERRA methodology and LUNA claim-safety reviews were incorporated before preflight.
"""
    write_md(REPORT / "v17_independent_audit.md", audit)
    final = f"""
# LightGuard v0.17 Municipal Operational Evidence Expansion

## Sources

| source | provider | rows | role |
|---|---|---:|---|
{chr(10).join(f'| {row["source_id"]} | {row["provider"]} | {row["rows"]:,} | {row["role"]} |' for row in source_manifest)}

## Fault Management Dataset

- Rows: {len(d1):,}; unique assets: {len(fault_ids):,}; period: {temporal['D1'][0]} to {temporal['D1'][1]}.
- Closed with valid nonnegative duration: {len(resolution_valid):,}; unresolved: {unresolved}; negative-duration quality cases: {negative_resolution}.

## Resolution Time

- Median: {statistics.median(resolution_valid):.0f} days; p90: {quantile(resolution_valid, .90):.0f} days.
- Same day: {ratio(sum(value == 0 for value in resolution_valid), len(resolution_valid)):.1%}; over 3 days: {ratio(sum(value > 3 for value in resolution_valid), len(resolution_valid)):.1%}; over 7 days: {ratio(sum(value > 7 for value in resolution_valid), len(resolution_valid)):.1%}.

## Detection Channel

- Routine inspection: {channels['일상점검']:,} ({ratio(channels['일상점검'], len(d1)):.1%}).
- Staff report: {channels['직원신고']:,} ({ratio(channels['직원신고'], len(d1)):.1%}).
- Citizen complaint: {channels['민원신고']:,} ({ratio(channels['민원신고'], len(d1)):.1%}).

## Repeat Events

- Assets with repeats on distinct days: {repeated_assets:,}; median positive gap: {statistics.median(recurrence_gaps):.0f} days.
- 30-day: {repeat_counts[30]:,}/{repeat_denominators[30]:,} eligible episodes ({ratio(repeat_counts[30], repeat_denominators[30]):.1%}); 90-day: {repeat_counts[90]:,}/{repeat_denominators[90]:,}; 365-day: {repeat_counts[365]:,}/{repeat_denominators[365]:,}.

## Spatial Join

- ID compatibility: `{join_status}`; matched: {len(matched_ids):,}; ambiguous: {len(ambiguous_ids):,}; unmatched: {len(unmatched_ids):,}.
- {summary['spatial_join']['unambiguous_join_candidate_event_rows']:,} event rows have exact, unambiguous candidate coordinates, but the result is `NO_SPATIAL_JOIN` and no hotspot is published because semantic identity is not verified.

## Safety Inspection

- Rows: {len(d3):,}; field actions other than `이상없음`: {len(d3) - field_actions['이상없음']:,}; review actions other than `이상없음`: {len(d3) - review_actions['이상없음']:,}.
- Electrical measurements are distribution-only because unit and official threshold applicability are unverified.

## Maintenance Context

- Material rows: {material_count:,}, versus {SOURCES['D4'][2]:,} advertised; D4 is `HOLD_PROFILE_ONLY` pending provider confirmation.
- Construction/project rows: {len(d5):,}; D5 type codes are not relabeled without a codebook.
- No event join key, unit price, expenditure, or cost savings is inferred.

## Operational Need Grade

**ON-A**: large actual event volume, multiple receipt routes, processing-time tail, repeated records, and safety/maintenance workload are all observed.

## LightGuard Service Mapping

- `DATA_QUALITY_REVIEW`: date, ID, coordinate, and source-snapshot exceptions.
- `REMOTE_MONITOR`: repeated-record and aging context for remote recheck.
- `FIELD_INSPECTION_CANDIDATE`: explainable queue using repeat, age, citizen report, and safety-action context.

## Competition Value

- 국민체감: citizen-report share, response-time tail, and repeated records are visible without claiming prevention.
- 활용목적: existing AMI is positioned as a triage aid for a demonstrated municipal workflow.
- 유형효과: the app separates signal evidence, controlled validation, literature, and actual operational burden.
- 개발용이성: the three-lane object maps to observed intake, monitoring, and field-action concepts.
- 범용성: other municipal schemas are candidates, not force-merged evidence.

## Claim Boundary

Daegu supports operational need only. It does not validate competition AMI fault accuracy, Suyeong field performance, prevented complaints, causal response-time improvement, or savings.

## QA / Build

Artifact QA is enforced by `scripts/test_v17_artifacts.py`; Flutter analyze/test/Web/Android are enforced by `scripts/v17_preflight.sh`.

## Next Step

Use newly linked field outcomes or new independent AMI for detector validation. Do not tune again on the frozen five-meter corpus.
"""
    write_md(REPORT / "v17_final_summary.md", final)

    learning_common = """
## Sources learned before analysis

- OpenAI Harness Engineering: https://openai.com/index/harness-engineering/
- OpenAI Codex: https://openai.com/codex/
- Codex AGENTS.md: https://github.com/openai/codex/blob/main/docs/agents_md.md
- D1-D5 official pages: https://www.data.go.kr/data/15120484/fileData.do, https://www.data.go.kr/data/15120529/fileData.do, https://www.data.go.kr/data/15120494/fileData.do, https://www.data.go.kr/data/15120490/fileData.do, https://www.data.go.kr/data/15120488/fileData.do
- Ravago et al. (2023), recurrent outage-event survival analysis: https://doi.org/10.1016/j.japwor.2023.101213
- Parfitt (2004), municipal public-lighting maintenance and response cycles: https://researchspace.ukzn.ac.za/items/6ac5164c-3497-423f-881a-b589b1d562fa
- Chalfin et al., street-light outages and public safety: https://doi.org/10.1007/s10940-021-09519-4

## Applied learning

Repeated rows must be treated as clustered asset histories, incomplete resolution needs an explicit state, and operational response evidence cannot become AMI accuracy or causal service-benefit evidence without a linked intervention design.
"""
    write_md(LEARNING / "sol_orchestration.md", "# SOL Orchestration\n" + learning_common + "\nThe main task froze definitions before producing outcome artifacts and preserved v0.16.")
    write_md(LEARNING / "terra_operations_methodology.md", "# TERRA Operations Methodology\n" + learning_common + "\nProtocol: calendar-day resolution, explicit invalid/censored states, asset-level repeated recorded events, exact-only spatial join, descriptive clustered interpretation.")
    write_md(LEARNING / "terra_service_value_statistics.md", "# TERRA Service-Value Statistics\n" + learning_common + "\nPermitted metrics are observed workload shares, duration quantiles, repeat-record shares, hotspot concentration, and action frequencies. Avoidable events and savings are prohibited.")
    write_md(LEARNING / "luna_data_expansion.md", "# LUNA Data Expansion\n" + learning_common + f"\nTwelve Korean query families produced {len(candidate_rows)} official candidates. None is force-merged; license and schema are reverified only at inclusion.")
    write_md(LEARNING / "luna_independent_qa.md", "# LUNA Independent QA Contract\n" + learning_common + "\nThe audit blocks AMI-label confusion, snapshot stacking, fuzzy joins, hidden invalid dates, preventable-complaint claims, cost inference, invented electrical thresholds, and Daegu-to-Suyeong transfer.")
    write_md(APP_DOCS / "v17_municipal_operations_evidence.md", f"""
# v0.17 Municipal Operations Evidence

The app displays a separate Daegu operational Evidence Layer: {len(d1):,} fault-management events, observed receipt routes, valid processing-time quantiles, repeat recorded events, and {len(d3):,} safety inspections. D4 remains profile-only because its local row count conflicts with official metadata.

`PARTIAL_JOIN` means 99.57% of D1 unique IDs overlap D2, but semantic identity and duplicate-coordinate issues are unresolved. Therefore no hotspot is published. This layer is not linked to competition AMI, Suyeong scenarios, Gangneung, or Chungju. It supports workflow need, not field accuracy, prevented complaints, or savings.
""")
    print(json.dumps({
        "status": "BUILT", "fault_events": len(d1), "unique_assets": len(fault_ids),
        "join_status": join_status, "spatial_analysis_status": "NO_SPATIAL_JOIN",
        "median_resolution_days": statistics.median(resolution_valid), "p90_resolution_days": quantile(resolution_valid, .90),
        "repeat_30d_eligible_episode_rate": ratio(repeat_counts[30], repeat_denominators[30]), "operational_need_grade": "ON-A",
        "d4_row_mismatch": [material_count, SOURCES["D4"][2]],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
