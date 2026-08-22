#!/usr/bin/env python3
"""Build LightGuard v0.20 Ulsan operational-transfer evidence.

Raw identifiers and free-text work descriptions are used only in memory. They
are never written to tracked artifacts. Observed work starts are replay slots,
not staffing or true municipal capacity.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import statistics
import unicodedata
from collections import Counter, defaultdict, deque
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1" / "data" / "validation" / "v20"
REPORT = ROOT / "lightguard_v0_1" / "reports" / "v20"
APP_DOC = ROOT / "lightguard_app" / "docs" / "v20_ulsan_operational_transfer.md"
CARD = ROOT / "lightguard_app" / "lib" / "features" / "ami_validation" / "municipal_operations_evidence_card.dart"
V19_PATH = ROOT / "scripts" / "build_v19_buyeo.py"
MAIN_FREEZE = "8d3809efb628f0e496fccd0184078b7603771e97"
U1_SHA = "d0e3fecb06577d53b86cba5bf294b745559c2412e3f3b8965b69cb50d497d9fb"
U2_SHA = "a060cf2f289274b62ea1578704b8673920a02cfb54f2232171482384266790fb"
U1_URL = "https://www.data.go.kr/data/15116405/fileData.do"
U2_URL = "https://www.data.go.kr/data/15127415/fileData.do"
FEATURES = ["month", "weekday", "prior_30d_count", "prior_90d_count", "prior_365d_count", "days_since_previous_event", "open_prior_case_count", "historical_long_resolution_count"]
EXPECTED_COLUMNS = ["관리번호", "시설구분", "시설종류", "보수접수일", "작업시작일", "작업완료일", "작업내용", "완료확인일", "진행상태"]
EXPECTED_U2_COLUMNS = ["관리번호", "시설종류", "주소", "등기구종류", "램프종류", "램프용량(W)", "램프수량", "등주종류", "위도", "경도", "데이터기준일자"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, default=json_default) + "\n", encoding="utf-8")


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def json_default(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(type(value).__name__)


def load_v19():
    spec = importlib.util.spec_from_file_location("lightguard_v19", V19_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def locate_sha(expected: str) -> Path:
    for path in (ROOT / "official_docs").rglob("*"):
        if path.is_file() and sha(path) == expected:
            return path
    raise RuntimeError(f"BLOCKED_SOURCE_SHA_NOT_FOUND:{expected}")


def parse_day(value: str) -> date | None:
    value = (value or "").strip()
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def normalize_id(value: str) -> str:
    return unicodedata.normalize("NFC", (value or "").strip())


def opaque_event(index: int, receipt: date | None) -> str:
    value = f"v20-ulsan-event|{index}|{receipt or 'missing'}"
    return hashlib.sha256(value.encode()).hexdigest()[:20]


def read_u1(path: Path) -> tuple[list[dict], dict]:
    with path.open(encoding="cp949", newline="") as f:
        reader = csv.DictReader(f)
        columns = list(reader.fieldnames or [])
        physical = list(reader)
    if columns != EXPECTED_COLUMNS:
        raise RuntimeError(f"BLOCKED_U1_SCHEMA:{columns}")
    empty = [r for r in physical if not any((r.get(c) or "").strip() for c in columns)]
    source = [r for r in physical if any((r.get(c) or "").strip() for c in columns)]
    exact_duplicate_rows = len(source) - len({tuple((r.get(c) or "").strip() for c in columns) for r in source})
    events = []
    parse_failures = 0
    for i, raw in enumerate(source):
        try:
            receipt = parse_day(raw["보수접수일"])
            start = parse_day(raw["작업시작일"])
            complete = parse_day(raw["작업완료일"])
            confirmed = parse_day(raw["완료확인일"])
        except ValueError:
            parse_failures += 1
            continue
        asset = raw["관리번호"].strip() or None
        anomalies = []
        if receipt is None:
            anomalies.append("RECEIPT_MISSING")
        if receipt and start and start < receipt:
            anomalies.append("START_BEFORE_RECEIPT")
        if receipt and complete and complete < receipt:
            anomalies.append("COMPLETION_BEFORE_RECEIPT")
        if start and complete and complete < start:
            anomalies.append("COMPLETION_BEFORE_START")
        if complete and confirmed and confirmed < complete:
            anomalies.append("CONFIRMATION_BEFORE_COMPLETION")
        if complete and not start:
            anomalies.append("COMPLETION_WITHOUT_START")
        facility = (raw["시설구분"].strip() or raw["시설종류"].strip() or "UNKNOWN")
        events.append({
            "event_hash": opaque_event(i, receipt), "asset": asset, "receipt_date": receipt,
            "start_date": start, "completion_date": complete, "confirmation_date": confirmed,
            "facility_category": facility, "work_text_present": bool(raw["작업내용"].strip()),
            "lifecycle_status": "VALID" if not anomalies else "+".join(sorted(anomalies)),
            "valid_receipt_start": bool(receipt and start and start >= receipt),
            "valid_receipt_completion": bool(receipt and complete and complete >= receipt),
        })
    manifest = {
        "dataset": "U1_EVENT", "official_source": U1_URL, "sha256": sha(path),
        "encoding": "cp949", "columns": columns, "schema_fingerprint": hashlib.sha256("|".join(columns).encode()).hexdigest(),
        "physical_row_count": len(physical), "structurally_empty_row_count": len(empty),
        "canonical_event_count": len(events), "exact_duplicate_nonempty_rows": exact_duplicate_rows,
        "date_parse_failure_count": parse_failures,
        "receipt_date_min": min(e["receipt_date"] for e in events if e["receipt_date"]).isoformat(),
        "receipt_date_max": max(e["receipt_date"] for e in events if e["receipt_date"]).isoformat(),
        "usable_unique_asset_count": len({e["asset"] for e in events if e["asset"]}),
        "start_before_receipt_count": sum("START_BEFORE_RECEIPT" in e["lifecycle_status"] for e in events),
        "completion_before_receipt_count": sum("COMPLETION_BEFORE_RECEIPT" in e["lifecycle_status"] for e in events),
        "tracked_in_git": False, "raw_identifier_exported": False, "raw_work_text_exported": False,
    }
    return events, manifest


def read_u2(path: Path) -> tuple[list[dict], dict]:
    with path.open(encoding="cp949", newline="") as f:
        reader = csv.DictReader(f)
        columns = list(reader.fieldnames or [])
        physical = list(reader)
    if columns != EXPECTED_U2_COLUMNS:
        raise RuntimeError(f"BLOCKED_U2_SCHEMA:{columns}")
    rows = []
    invalid_coordinates = 0
    for raw in physical:
        asset = normalize_id(raw["관리번호"])
        try:
            latitude = float((raw["위도"] or "").strip())
            longitude = float((raw["경도"] or "").strip())
            coordinate_valid = 33 <= latitude <= 39 and 124 <= longitude <= 132
        except ValueError:
            latitude = longitude = None
            coordinate_valid = False
        invalid_coordinates += not coordinate_valid
        rows.append({
            "asset": asset,
            "facility_category": (raw["시설종류"] or "").strip() or "UNKNOWN",
            "latitude": latitude,
            "longitude": longitude,
            "coordinate_valid": coordinate_valid,
            "snapshot_date": parse_day(raw["데이터기준일자"]),
            "normalized_row": tuple((raw.get(c) or "").strip() for c in columns),
        })
    groups = defaultdict(list)
    for row in rows:
        groups[row["asset"]].append(row)
    repeated = {key: value for key, value in groups.items() if len(value) > 1}
    exact_duplicate_ids = sum(len({r["normalized_row"] for r in value}) == 1 for value in repeated.values())
    manifest = {
        "dataset": "U2_ASSET", "official_source": U2_URL, "sha256": sha(path),
        "encoding": "cp949", "columns": columns,
        "schema_fingerprint": hashlib.sha256("|".join(columns).encode()).hexdigest(),
        "physical_row_count": len(physical), "canonical_asset_row_count": len(rows),
        "unique_identifier_count": len(groups), "missing_identifier_count": sum(not r["asset"] for r in rows),
        "duplicate_identifier_row_count": sum(len(value) - 1 for value in repeated.values()),
        "ambiguous_identifier_count": len(repeated), "exact_duplicate_identifier_count": exact_duplicate_ids,
        "conflicting_duplicate_identifier_count": len(repeated) - exact_duplicate_ids,
        "valid_coordinate_count": len(rows) - invalid_coordinates,
        "invalid_or_missing_coordinate_count": invalid_coordinates,
        "facility_categories": dict(sorted(Counter(r["facility_category"] for r in rows).items())),
        "snapshot_dates": dict(sorted(Counter(str(r["snapshot_date"]) for r in rows).items())),
        "local_source_status": "AVAILABLE_VERIFIED", "tracked_in_git": False,
        "raw_identifier_exported": False, "raw_address_exported": False,
        "raw_coordinate_exported": False,
    }
    return rows, manifest


def build_u1_u2_join(events: list[dict], u2_rows: list[dict]) -> tuple[dict, dict]:
    groups = defaultdict(list)
    for row in u2_rows:
        groups[row["asset"]].append(row)
    unique = {key: value[0] for key, value in groups.items() if key and len(value) == 1}
    ambiguous = {key for key, value in groups.items() if key and len(value) > 1}
    matched = []
    ambiguous_events = unmatched_events = category_conflicts = 0
    for event in events:
        asset = normalize_id(event["asset"] or "")
        if asset in ambiguous:
            ambiguous_events += 1
        elif asset not in unique:
            unmatched_events += 1
        elif event["facility_category"] != unique[asset]["facility_category"]:
            category_conflicts += 1
        else:
            matched.append((event, unique[asset]))
    matched_assets = {normalize_id(event["asset"] or "") for event, _ in matched}
    all_assets = {normalize_id(event["asset"] or "") for event in events if event["asset"]}
    ambiguous_assets = all_assets & ambiguous
    unmatched_assets = {asset for asset in all_assets if asset not in groups}
    snapshot = date(2026, 3, 10)
    join = {
        "join_status": "PARTIAL_VERIFIED_EXACT_ID",
        "join_method": "EXACT_NORMALIZED_ID_AND_CATEGORY",
        "u1_event_count": len(events), "u1_unique_asset_count": len(all_assets),
        "safe_matched_event_count": len(matched), "safe_matched_asset_count": len(matched_assets),
        "safe_asset_match_rate": len(matched_assets) / len(all_assets),
        "ambiguous_u2_match_event_count": ambiguous_events,
        "ambiguous_u2_match_asset_count": len(ambiguous_assets),
        "unmatched_event_count": unmatched_events, "unmatched_asset_count": len(unmatched_assets),
        "category_conflict_event_count": category_conflicts, "row_multiplication_count": 0,
        "u2_snapshot_date": snapshot, "historical_coverage": "UNKNOWN",
        "matched_events_after_snapshot_count": sum(event["receipt_date"] > snapshot for event, _ in matched if event["receipt_date"]),
        "raw_identifier_exported": False, "fuzzy_join_used": False,
    }
    spatial = {
        "scope": "AGGREGATE_ONLY", "safe_matched_asset_count": len(matched_assets),
        "safe_matched_event_count": len(matched),
        "matched_coordinate_valid_event_count": sum(asset["coordinate_valid"] for _, asset in matched),
        "matched_facility_event_counts": dict(sorted(Counter(asset["facility_category"] for _, asset in matched).items())),
        "all_u2_coordinate_valid_count": sum(row["coordinate_valid"] for row in u2_rows),
        "raw_coordinates_exported": False, "map_point_exported": False,
        "claim_boundary": "Asset coverage evidence only; no historical co-temporality or AMI fault-truth claim.",
    }
    return join, spatial


def ulsan_for_v19(events: list[dict]) -> list[dict]:
    return [{
        "event_hash": e["event_hash"], "receipt_date": e["receipt_date"],
        "completion_date": e["completion_date"], "asset": e["asset"],
        "asset_hash": hashlib.sha256(("v20-asset|" + e["asset"]).encode()).hexdigest()[:20] if e["asset"] else "",
        "resolution_days": (e["completion_date"] - e["receipt_date"]).days if e["valid_receipt_completion"] else None,
    } for e in events if e["receipt_date"]]


def freeze_model(v19) -> tuple[dict, dict, list[float], object]:
    daegu = v19.canonical_daegu(v19.read_csv(v19.locate(v19.DAEGU_SHA)))
    enriched = v19.enrich(daegu, max(r["receipt_date"] for r in daegu))
    dev = [r for r in enriched if date(2020, 1, 2) <= r["receipt_date"] <= date(2023, 12, 1) and r["asset"] and r["repeat_30d_evaluable"]]
    val = [r for r in enriched if date(2024, 1, 1) <= r["receipt_date"] <= date(2024, 12, 1) and r["asset"] and r["repeat_30d_evaluable"]]
    x, stats = v19.design(dev)
    beta = v19.logistic_fit(x, [r["repeat_30d"] for r in dev])
    xv, _ = v19.design(val, stats)
    logistic = (1 / (1 + np.exp(-np.clip(xv @ beta, -30, 30)))).tolist()
    simple = v19.score_simple(val)
    candidates = {
        "SIMPLE_RULE": {"ap": v19.ap([r["repeat_30d"] for r in val], simple), **v19.top_metrics([r["repeat_30d"] for r in val], simple)},
        "LOGISTIC": {"ap": v19.ap([r["repeat_30d"] for r in val], logistic), **v19.top_metrics([r["repeat_30d"] for r in val], logistic)},
    }
    selected = max(candidates, key=lambda k: (candidates[k]["enrichment"], candidates[k]["ap"]))
    model = {
        "freeze_base": MAIN_FREEZE, "training_domain": "Daegu only", "external_domain": "Ulsan untouched",
        "decision_timestamp": "BEFORE_ULSAN_OUTCOME_CONSTRUCTION", "features": FEATURES,
        "validation_candidates": candidates, "selected_model": selected, "retuning_count": 0,
        "beta": [float(v) for v in beta], "design_stats": json.loads(json.dumps(stats, default=json_default)),
    }
    model["model_sha256"] = hashlib.sha256(json.dumps(model, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return model, candidates, [float(v) for v in beta], stats


def bootstrap_cluster(v19, rows: list[dict], scores: list[float], reps: int = 2000) -> dict:
    groups = defaultdict(list)
    for i, row in enumerate(rows):
        groups[row["asset_hash"]].append(i)
    keys = sorted(groups)
    rng = np.random.default_rng(20260821)
    enrichments = []
    for _ in range(reps):
        sample = rng.choice(keys, len(keys), replace=True)
        idx = [i for key in sample for i in groups[key]]
        metric = v19.top_metrics([rows[i]["repeat_30d"] for i in idx], [scores[i] for i in idx])["enrichment"]
        if metric is not None and math.isfinite(metric):
            enrichments.append(float(metric))
    enrichments.sort()
    def q(p):
        return enrichments[min(len(enrichments) - 1, int((len(enrichments) - 1) * p))] if enrichments else None
    return {"method": "asset_cluster_bootstrap", "repetitions": reps, "top10_enrichment_ci95": [q(.025), q(.975)]}


def percentile(values: list[float], p: float):
    if not values:
        return None
    values = sorted(values)
    x = (len(values) - 1) * p
    lo, hi = math.floor(x), math.ceil(x)
    return values[lo] if lo == hi else values[lo] * (hi - x) + values[hi] * (x - lo)


def distribution(values: list[int]) -> dict:
    return {
        "n": len(values), "median": percentile(values, .5), "p75": percentile(values, .75),
        "p90": percentile(values, .9), "p95": percentile(values, .95),
        "same_day_share": sum(v == 0 for v in values) / len(values) if values else None,
        "over_1d_share": sum(v > 1 for v in values) / len(values) if values else None,
        "over_3d_share": sum(v > 3 for v in values) / len(values) if values else None,
        "over_7d_share": sum(v > 7 for v in values) / len(values) if values else None,
    }


def simulate(rows: list[dict], capacity: dict[date, int], policy: str, horizon: date) -> list[dict]:
    arrivals = defaultdict(list)
    for row in rows:
        arrivals[row["receipt_date"]].append(row)
    backlog: list[dict] = []
    result = []
    first = min(arrivals)
    day = first
    while day <= horizon:
        backlog.extend(arrivals.get(day, []))
        if policy == "FIFO":
            backlog.sort(key=lambda r: (r["receipt_date"], r["event_hash"]))
        elif policy == "FROZEN_COMMON_OPS":
            backlog.sort(key=lambda r: (-r["frozen_score"], r["receipt_date"], r["event_hash"]))
        else:
            backlog.sort(key=lambda r: (-r["simple_score"], r["receipt_date"], r["event_hash"]))
        slots = capacity.get(day, 0)
        served, backlog = backlog[:slots], backlog[slots:]
        for row in served:
            result.append({"event_hash": row["event_hash"], "policy": policy, "receipt_date": row["receipt_date"], "simulated_start_date": day, "wait_days": (day - row["receipt_date"]).days, "repeat_30d": row["repeat_30d"], "repeat_30d_evaluable": row["repeat_30d_evaluable"]})
        day += timedelta(days=1)
    for row in backlog:
        result.append({"event_hash": row["event_hash"], "policy": policy, "receipt_date": row["receipt_date"], "simulated_start_date": None, "wait_days": (horizon - row["receipt_date"]).days + 1, "repeat_30d": row["repeat_30d"], "repeat_30d_evaluable": row["repeat_30d_evaluable"]})
    return sorted(result, key=lambda r: r["event_hash"])


def queue_summary(rows: list[dict]) -> dict:
    all_wait = [r["wait_days"] for r in rows]
    repeat_wait = [r["wait_days"] for r in rows if r["repeat_30d_evaluable"] and r["repeat_30d"]]
    return {"all_cases": distribution(all_wait), "repeat_30d_cases": distribution(repeat_wait), "unstarted_at_horizon": sum(r["simulated_start_date"] is None for r in rows)}


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    REPORT.mkdir(parents=True, exist_ok=True)
    u1_path = locate_sha(U1_SHA)
    u2_path = locate_sha(U2_SHA)
    events, manifest = read_u1(u1_path)
    if manifest["physical_row_count"] != 2233 or manifest["canonical_event_count"] != 1060:
        raise RuntimeError("BLOCKED_U1_ROW_CONTRACT")
    dump(DATA / "v20_ulsan_u1_manifest.json", manifest)
    u2_rows, u2_manifest = read_u2(u2_path)
    if u2_manifest["physical_row_count"] != 17061:
        raise RuntimeError("BLOCKED_U2_ROW_CONTRACT")
    dump(DATA / "v20_ulsan_u2_manifest.json", u2_manifest)
    join_summary, spatial_summary = build_u1_u2_join(events, u2_rows)
    dump(DATA / "v20_u1_u2_join_summary.json", join_summary)
    dump(DATA / "v20_asset_spatial_summary.json", spatial_summary)
    contract = {"decision_timestamp": "BEFORE_ULSAN_OUTCOME_CONSTRUCTION", "eligible": True, "decision": "ELIGIBLE_COMMON_OPS", "features": FEATURES, "blocked_features": ["work_start_date", "work_completion_date", "confirmation_date", "facility_category", "work_text", "raw_asset_id", "address", "coordinates"], "ulsan_retuning_allowed": False, "primary_outcome": "repeat_30d", "right_censor_days": 30}
    dump(DATA / "v20_feature_availability_contract.json", contract)
    v19 = load_v19()
    model, candidates, beta, stats = freeze_model(v19)
    dump(DATA / "v20_frozen_common_ops_model.json", model)

    ue = v19.enrich(ulsan_for_v19(events), max(e["receipt_date"] for e in events if e["receipt_date"]))
    xall, _ = v19.design(ue, stats)
    logistic_all = (1 / (1 + np.exp(-np.clip(xall @ np.asarray(beta), -30, 30)))).tolist()
    simple_all = v19.score_simple(ue)
    for row, logistic_score, simple_score in zip(ue, logistic_all, simple_all):
        row["frozen_score"] = float(simple_score if model["selected_model"] == "SIMPLE_RULE" else logistic_score)
        row["simple_score"] = float(simple_score)
    ext = [r for r in ue if r["asset"] and r["repeat_30d_evaluable"]]
    scores = [r["frozen_score"] for r in ext]
    labels = [r["repeat_30d"] for r in ext]
    top = v19.top_metrics(labels, scores)
    ci = bootstrap_cluster(v19, ext, scores)
    enrichment = top["enrichment"]
    lo = ci["top10_enrichment_ci95"][0]
    tm_grade = "TM-A" if enrichment and enrichment >= 2 and lo and lo > 1 else "TM-B" if enrichment and enrichment > 1 else "TM-C" if enrichment is not None else "TM-X"
    zero = {"executed": True, "model": model["selected_model"], "ulsan_retuning_count": 0, "n": len(ext), "positives": sum(labels), "prevalence": sum(labels) / len(labels) if labels else None, "average_precision": v19.ap(labels, scores), "top10": top, **ci, "transfer_grade": tm_grade, "claim_boundary": "Operational-priority transfer only; not AMI accuracy or confirmed field-fault truth."}
    dump(DATA / "v20_zero_shot_summary.json", {"validation_candidates": candidates, "external": zero, "seal": {"outcome_unseen_at_freeze": True, "retuning_count": 0, "model_sha256": model["model_sha256"]}})
    write_csv(REPORT / "v20_zero_shot_results.csv", [{k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for k, v in zero.items()}], list(zero))
    score_rows = [{"event_hash": r["event_hash"], "score": round(r["frozen_score"], 12), "repeat_30d": r["repeat_30d"], "repeat_30d_evaluable": r["repeat_30d_evaluable"]} for r in ext]
    write_csv(DATA / "optional_v20_zero_shot_scores.csv", score_rows, list(score_rows[0]))

    wait_start = [(e["start_date"] - e["receipt_date"]).days for e in events if e["valid_receipt_start"]]
    execution = [(e["completion_date"] - e["start_date"]).days for e in events if e["valid_receipt_start"] and e["completion_date"] and e["completion_date"] >= e["start_date"]]
    total = [(e["completion_date"] - e["receipt_date"]).days for e in events if e["valid_receipt_completion"]]
    lifecycle = {"WAIT_TO_START": distribution(wait_start), "EXECUTION_DURATION": distribution(execution), "TOTAL_RESOLUTION": distribution(total), "temporal_anomaly_quarantine_count": sum(e["lifecycle_status"] != "VALID" for e in events), "same_day_order": "NOT_SUPPORTED"}
    dump(DATA / "v20_lifecycle_summary.json", lifecycle)
    lifecycle_rows = [{"event_hash": e["event_hash"], "receipt_date": e["receipt_date"], "start_date": e["start_date"], "completion_date": e["completion_date"], "confirmation_date": e["confirmation_date"], "facility_category": e["facility_category"], "work_text_present": e["work_text_present"], "lifecycle_status": e["lifecycle_status"]} for e in events]
    write_csv(DATA / "v20_ulsan_lifecycle_clean.csv", lifecycle_rows, list(lifecycle_rows[0]))

    capacity = Counter(e["start_date"] for e in events if e["valid_receipt_start"])
    capacity_rows = [{"date": d, "observed_work_starts": capacity[d], "interpretation": "OBSERVED_START_SLOTS_NOT_STAFFING_CAPACITY"} for d in sorted(capacity)]
    write_csv(DATA / "v20_work_start_capacity.csv", capacity_rows, list(capacity_rows[0]))
    by_hash = {e["event_hash"]: e for e in events}
    qevents = [r for r in ue if by_hash[r["event_hash"]]["valid_receipt_start"]]
    horizon = max(e["receipt_date"] for e in events if e["receipt_date"])
    replay_rows = []
    summaries = {}
    for policy in ["FIFO", "FROZEN_COMMON_OPS", "FROZEN_SIMPLE_RULE"]:
        simulated = simulate(qevents, capacity, policy, horizon)
        replay_rows.extend(simulated)
        summaries[policy] = queue_summary(simulated)
    base_p90 = summaries["FIFO"]["all_cases"]["p90"]
    model_p90 = summaries["FROZEN_COMMON_OPS"]["all_cases"]["p90"]
    repeat_base = summaries["FIFO"]["repeat_30d_cases"]["p90"]
    repeat_model = summaries["FROZEN_COMMON_OPS"]["repeat_30d_cases"]["p90"]
    promoted = model_p90 <= base_p90 + 1 and repeat_model is not None and repeat_base is not None and repeat_model < repeat_base
    ws_grade = "WS-A" if promoted else "WS-B" if model_p90 <= base_p90 + 1 else "WS-C"
    queue_result = {"policies": summaries, "promotion_gate": {"predeclared_all_case_p90_tolerance_days": 1, "repeat_case_p90_must_improve": True, "passed": promoted}, "work_start_grade": ws_grade, "capacity_interpretation": "NOT_EVALUABLE_AS_STAFFING_CAPACITY", "same_day_order": "NOT_SUPPORTED", "causal_claim": "NOT_SUPPORTED"}
    dump(DATA / "v20_queue_replay_summary.json", queue_result)
    write_csv(DATA / "v20_queue_replay_events.csv", replay_rows, list(replay_rows[0]))
    write(REPORT / "v20_queue_replay.md", "# v0.20 Queue Replay\n\n" + json.dumps(queue_result, ensure_ascii=False, indent=2, default=json_default) + "\n\nObserved daily work starts are replay slots, not staffing or true capacity. This counterfactual replay does not establish actual field-delay reduction or causality.\n")

    audit = f"""# LightGuard v0.20 Independent Audit

- Freeze: `{MAIN_FREEZE}`; v0.18/v0.19 artifacts are inputs and are not rewritten.
- U1: CP949, SHA `{U1_SHA}`, 2,233 physical rows, 1,173 structural blanks, 1,060 canonical events.
- Temporal quarantine: {lifecycle['temporal_anomaly_quarantine_count']} rows are excluded from lifecycle/queue claims where required.
- U2: **AVAILABLE_VERIFIED**, 17,061 rows; safe exact-ID/category join is **PARTIAL_VERIFIED_EXACT_ID**.
- Safe join: {join_summary['safe_matched_asset_count']} assets / {join_summary['safe_matched_event_count']} events; {join_summary['ambiguous_u2_match_asset_count']} ambiguous and {join_summary['unmatched_asset_count']} unmatched assets remain excluded.
- Retuning: **0**; Ulsan outcome is constructed after the COMMON-OPS model seal.
- Transfer grade: **{tm_grade}**; work-start replay grade: **{ws_grade}**.
- Staffing capacity: **NOT_EVALUABLE**. Same-day observed ordering: **NOT_SUPPORTED**.
- U1 is municipal operational evidence, not AMI ground truth or adjudicated physical-fault truth.
"""
    write(REPORT / "v20_independent_audit.md", audit)
    final = f"""# LightGuard v0.20 Ulsan Operational Transfer

- Third municipality: Ulsan Nam-gu U1, {len(events):,} canonical operational records.
- Frozen COMMON-OPS zero-shot: **{tm_grade}**, AP {zero['average_precision']:.4f}, top-10% enrichment {enrichment:.4f}x.
- Lifecycle separates receipt-to-start, start-to-completion, and total resolution.
- Queue replay: **{ws_grade}**, using observed daily work starts only.
- U2 asset/location data: **AVAILABLE_VERIFIED**; {join_summary['safe_matched_asset_count']:,} assets ({join_summary['safe_asset_match_rate']:.1%}) passed exact-ID/category/uniqueness gates.
- U2 ambiguous IDs and unmatched assets are excluded; snapshot co-temporality remains **UNKNOWN**.
- Staffing capacity: **NOT_EVALUABLE**; same-day order and causal delay reduction: **NOT_SUPPORTED**.
- Boundary: external municipal records are operational evidence, not LightGuard AMI accuracy truth.
"""
    write(REPORT / "v20_final_summary.md", final)
    write(APP_DOC, final)
    card = f'''import 'package:flutter/material.dart';

class MunicipalOperationsEvidenceCard extends StatelessWidget {{
  const MunicipalOperationsEvidenceCard({{super.key}});

  @override
  Widget build(BuildContext context) {{
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Municipal Operations Evidence', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 10),
          const Text('Daegu: large-scale maintenance burden · Buyeo: fault-type and repeat history · Ulsan: receipt → work start → completion'),
          const SizedBox(height: 8),
          const Wrap(spacing: 8, runSpacing: 8, children: [Chip(label: Text('{tm_grade} transfer')), Chip(label: Text('{ws_grade} replay'))]),
          const SizedBox(height: 8),
          const Text('U2 asset/location: PARTIAL_VERIFIED · 920/981 assets exact-matched · 13 ambiguous · 48 unmatched'),
          const SizedBox(height: 6),
          const Text('Staffing capacity: NOT_EVALUABLE · Same-day order: NOT_SUPPORTED · Historical coverage: UNKNOWN'),
          const SizedBox(height: 6),
          const Text('External municipal records are operational evidence, not AMI truth. Queue replay does not prove actual field-delay reduction.'),
        ]),
      ),
    );
  }}
}}
'''
    write(CARD, card)
    tracked = []
    for base in [DATA, REPORT]:
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.name != "v20_artifact_manifest.json":
                tracked.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path)})
    for path in [APP_DOC, CARD]:
        tracked.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path)})
    dump(DATA / "v20_artifact_manifest.json", {"version": "0.20", "status": "BUILT", "freeze_base": MAIN_FREEZE, "u1_sha256": U1_SHA, "u2_sha256": U2_SHA, "u2_local_status": "AVAILABLE_VERIFIED", "u1_u2_join_status": "PARTIAL_VERIFIED_EXACT_ID", "retuning_count": 0, "artifacts": tracked, "privacy_scan_required": True})
    print(json.dumps({"status": "BUILT", "events": len(events), "transfer_grade": tm_grade, "work_start_grade": ws_grade}, ensure_ascii=False))


if __name__ == "__main__":
    main()
