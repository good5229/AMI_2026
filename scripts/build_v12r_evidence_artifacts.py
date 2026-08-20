#!/usr/bin/env python3
"""Build literature registry and sealed v0.12R evidence joins."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v12r"
REPORTS = ROOT / "lightguard_v0_1/reports/v12r"
MATRIX = DATA / "v12r_literature_evidence_matrix.csv"
APP = ROOT / "lightguard_app/assets/data/context/v12r_literature_summary.json"


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flag(row: dict, name: str) -> int:
    return 0 if row.get(name) in ("", "NA", None) else int(row[name])


def literature_grade(pattern_id: str) -> str:
    return {"P1": "EVIDENCE_A", "P2": "EVIDENCE_B", "P3": "EVIDENCE_B", "P4": "EVIDENCE_C"}[pattern_id]


def pattern_for_score(row: dict) -> tuple[str, str]:
    if flag(row, "d3_proxy_signal"):
        return "P3", "phase-current asymmetry observation"
    if flag(row, "d2_proxy_signal"):
        return "P2", "persistent meter-relative load departure"
    return "P4", "meter-relative historical baseline"


def final_grade(lit: str, h1: bool, proxy_count: int) -> str:
    if lit in ("EVIDENCE_A", "EVIDENCE_B") and h1 and proxy_count >= 2:
        return "EVIDENCE_A"
    if lit in ("EVIDENCE_A", "EVIDENCE_B") and proxy_count >= 2:
        return "EVIDENCE_B"
    return "EVIDENCE_C"


def main() -> None:
    matrix = read_csv(MATRIX)
    if len({row["source_id"] for row in matrix}) != 21:
        raise RuntimeError("literature source count must remain 21")
    by_source: dict[str, list[dict]] = defaultdict(list)
    for row in matrix:
        by_source[row["source_id"]].append(row)
    registry = []
    for source_id, rows in sorted(by_source.items()):
        row = rows[0]
        quality = "B" if source_id in {"C02", "C06"} else "A"
        registry.append({
            "source_id": source_id,
            "citation": f"{row['title']} ({row['year']})",
            "DOI": row["DOI"],
            "URL": row["URL"],
            "year": row["year"],
            "quality_grade": quality,
            "support_grade": row["support_grade"],
            "pattern_ids": sorted({item["pattern_id"] for item in rows}),
        })
    write_json(DATA / "v12r_reference_registry.json", registry)

    log_fields = ["record_type", "id", "query_or_source", "status", "quality", "directness", "verification_or_reason", "url"]
    terra_log = [
        {field: row.get(field, "") for field in log_fields}
        for row in read_csv(REPORTS / "v12r_literature_search_log_terra.csv")
    ]
    registry_log = [{
        "record_type": "registry",
        "id": row["source_id"],
        "query_or_source": row["citation"],
        "status": "included",
        "quality": row["quality_grade"],
        "directness": row["support_grade"],
        "verification_or_reason": "independently reconciled in v12r literature evidence matrix",
        "url": row["URL"],
    } for row in registry]
    write_csv(REPORTS / "v12r_literature_search_log.csv", terra_log + registry_log, log_fields)

    claim_rows = []
    for pattern_id, name, mechanism, grade, allowed, prohibited in (
        ("P1", "Daytime full activation", "expected-state/current mismatch", "EVIDENCE_A", "strong daytime anomaly sign with independently verified context", "actual fault or controller/lamp cause"),
        ("P2", "Persistent partial activation", "sustained meter-relative load departure", "EVIDENCE_B", "persistence anomaly evidence", "confirmed partial outage"),
        ("P3", "Phase-selective activation", "phase-current asymmetry observation", "EVIDENCE_B", "phase-selective anomaly sign", "negative-sequence fault or failed phase"),
        ("P4", "Baseline deviation", "past-only meter-relative historical departure", "EVIDENCE_C", "time-slot baseline anomaly sign", "fault probability or outcome accuracy"),
    ):
        claim_rows.append((pattern_id, name, mechanism, grade, allowed, prohibited))
    claim_md = "# v0.12R Claim Evidence Matrix\n\n| pattern | mechanism | grade | allowed | prohibited |\n|---|---|---|---|---|\n" + "".join(
        f"| {pid} {name} | {mechanism} | {grade} | {allowed} | {prohibited} |\n"
        for pid, name, mechanism, grade, allowed, prohibited in claim_rows
    ) + "\nEvidence grades express support strength, not fault probability. Literature never replaces Gold or Silver labels.\n"
    (REPORTS / "v12r_claim_evidence_matrix.md").write_text(claim_md, encoding="utf-8")

    h1_rows = read_csv(ROOT / "lightguard_v0_1/data/validation/v10/v10_shadow_origin_audit.csv")
    h1 = {(row["meter_id"], row["availability_time"]): row["action"] for row in h1_rows}
    scores = read_csv(ROOT / "lightguard_v0_1/data/validation/v11/v11_proxy_signs.csv")
    events = read_csv(ROOT / "lightguard_app/assets/data/ami_events.csv")
    for event in events:
        event["_start"] = datetime.fromisoformat(event["first_sample"])
        event["_end"] = datetime.fromisoformat(event["last_sample"])
    cases = []
    for row in scores:
        proxy_count = int(row["proxy_family_count"])
        if proxy_count < 2:
            continue
        pattern_id, pattern_name = pattern_for_score(row)
        action = h1.get((row["meter_id"], row["timestamp"]), "normal")
        h1_positive = action in ("observe", "inspect")
        timestamp = datetime.fromisoformat(row["timestamp"])
        canonical = next((event["event_id"] for event in events if event["meter_id"] == row["meter_id"] and event["_start"] <= timestamp <= event["_end"]), "")
        lit = literature_grade(pattern_id)
        cases.append({
            "case_id": row["sample_id"],
            "meter_id": row["meter_id"],
            "timestamp": row["timestamp"],
            "pattern_id": pattern_id,
            "pattern_name": pattern_name,
            "literature_support_grade": max((item["support_grade"] for item in matrix if item["pattern_id"] == pattern_id), default="L0"),
            "literature_evidence_grade": lit,
            "h1_action": action,
            "h1_positive": h1_positive,
            "p1_robust_residual": flag(row, "d1_proxy_signal"),
            "p2_persistence": flag(row, "d2_proxy_signal"),
            "p3_phase": row["d3_proxy_signal"],
            "proxy_family_count": proxy_count,
            "final_evidence_grade": final_grade(lit, h1_positive, proxy_count),
            "canonical_event_id": canonical,
            "field_confirmation": "unavailable",
            "allowed_claim": "literature-supported multi-evidence anomaly-sign candidate",
            "prohibited_claim": "confirmed fault, fault probability, field accuracy, recall, precision, FPR, or specificity",
        })
    write_csv(DATA / "v12r_case_evidence_matrix.csv", cases, list(cases[0]))

    event_pattern = {
        "daytime_full_activation": ("P1", "expected-state/current mismatch"),
        "daytime_partial_activation": ("P2", "persistent meter-relative load departure"),
        "daytime_phase_selective_activation": ("P3", "phase-current asymmetry observation"),
    }
    canonical_proxy = {row["event"]: row for row in read_csv(REPORTS.parent / "v11/v11_canonical_six_proxy_review.csv")}
    canonical_rows = []
    for event in events:
        pattern_id, pattern_name = event_pattern[event["event_type"]]
        proxy = canonical_proxy[event["event_id"]]
        p_count = int(proxy["proxy_family_count"])
        h1_positive = proxy["h1"] in ("observe", "inspect")
        lit = literature_grade(pattern_id)
        canonical_rows.append({
            "event": event["event_id"],
            "observed_pattern": pattern_name,
            "literature_grade": lit,
            "literature_support": "L3 direct" if pattern_id == "P1" else "L2 mechanism",
            "h1": proxy["h1"],
            "p1": proxy["p1"],
            "p2": proxy["p2"],
            "p3": proxy["p3"],
            "proxy_family_count": p_count,
            "final_evidence_grade": final_grade(lit, h1_positive, p_count),
            "final_interpretation": "Strong literature-supported anomaly sign; field confirmation required",
            "field_confirmation": "unavailable",
        })
    table = "# v0.12R Canonical Six Literature Evidence\n\n| event | pattern | literature | H1 | proxy families | final |\n|---|---|---|---|---:|---|\n" + "".join(
        f"| {row['event']} | {row['observed_pattern']} | {row['literature_grade']} | {row['h1']} | {row['proxy_family_count']} | {row['final_evidence_grade']} |\n"
        for row in canonical_rows
    ) + "\nAll six remain previously identified anomaly-sign candidates. Field confirmation is unavailable.\n"
    (REPORTS / "v12r_canonical_six_evidence.md").write_text(table, encoding="utf-8")

    quality = Counter(row["quality_grade"] for row in registry)
    pattern_counts = Counter(row["pattern_id"] for row in cases)
    summary = {
        "schema_version": "lightguard.v12r.literature-summary.1",
        "status": "PHASE_A_LITERATURE_COMPLETE",
        "review_status": "HUMAN_REVIEW_PENDING",
        "route": "C",
        "sources": len(registry),
        "quality_a": quality["A"],
        "quality_b": quality["B"],
        "core_direct_or_mechanism": sum(row["support_grade"] in ("L2", "L3") for row in registry),
        "patterns": {
            "P1": {"label": "Expected-state/current mismatch", "grade": "EVIDENCE_A"},
            "P2": {"label": "Persistent meter-relative departure", "grade": "EVIDENCE_B"},
            "P3": {"label": "Phase-current asymmetry observation", "grade": "EVIDENCE_B"},
            "P4": {"label": "Historical baseline departure", "grade": "EVIDENCE_C"},
        },
        "proxy_high_mapped": len(cases),
        "proxy_pattern_counts": dict(pattern_counts),
        "canonical_cases": len(canonical_rows),
        "gold_usable": 0,
        "silver_usable": 0,
        "maximum_current_claim_level": 3,
        "fault_probability_available": False,
        "claim_guard": "Evidence grades are not fault probabilities; literature does not replace field labels.",
        "matrix_sha256": sha(MATRIX),
    }
    write_json(APP, summary)
    print(json.dumps({"sources": len(registry), "A": quality["A"], "B": quality["B"], "proxy_high": len(cases), "canonical": len(canonical_rows)}))


if __name__ == "__main__":
    main()
