#!/usr/bin/env python3
"""Freeze a literature-aware but fully blinded v0.12R human-review packet."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

from run_v11_independent_detectors import load_raw_currents

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v12r"
REPORTS = ROOT / "lightguard_v0_1/reports/v12r"
SELECTION_NS = "lightguard.v12r.review.selection.20260821"
ORDER_NS = "lightguard.v12r.review.order.20260821"


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hkey(group: str, sample_id: str) -> str:
    return hashlib.sha256(f"{SELECTION_NS}|{group}|{sample_id}".encode()).hexdigest()


def main() -> None:
    cases = read_csv(DATA / "v12r_case_evidence_matrix.csv")
    scores = read_csv(ROOT / "lightguard_v0_1/data/validation/v11/v11_proxy_signs.csv")
    h1_rows = read_csv(ROOT / "lightguard_v0_1/data/validation/v10/v10_shadow_origin_audit.csv")
    h1 = {(row["meter_id"], row["availability_time"]): row["action"] for row in h1_rows}
    scores_by_id = {row["sample_id"]: row for row in scores}

    s1 = [row for row in cases if row["h1_positive"].lower() == "true" and row["literature_evidence_grade"] in ("EVIDENCE_A", "EVIDENCE_B")]
    s2 = [row for row in cases if row["h1_positive"].lower() == "false" and row["literature_evidence_grade"] in ("EVIDENCE_A", "EVIDENCE_B")]
    singleton = []
    for row in scores:
        if int(row["proxy_family_count"]) != 1:
            continue
        if row["d3_proxy_signal"] == "1":
            pattern, grade = "P3", "EVIDENCE_B"
        elif row["d2_proxy_signal"] == "1":
            pattern, grade = "P2", "EVIDENCE_B"
        else:
            pattern, grade = "P4", "EVIDENCE_C"
        singleton.append({**row, "pattern_id": pattern, "literature_evidence_grade": grade})

    chosen = {
        "S1_ALGORITHM_LITERATURE": sorted(s1, key=lambda row: hkey("S1", row["case_id"])),
        "S2_PROXY_LITERATURE": sorted(s2, key=lambda row: hkey("S2", row["case_id"]))[:18],
        "S3_SINGLETON_LITERATURE": sorted(singleton, key=lambda row: hkey("S3", row["sample_id"]))[:18],
    }
    used = {row.get("case_id", row.get("sample_id")) for values in chosen.values() for row in values}
    anchors = [scores_by_id[row.get("case_id", row.get("sample_id"))] for values in chosen.values() for row in values][:20]
    random_rows = []
    for index, anchor in enumerate(anchors):
        candidates = [
            row for row in scores
            if row["meter_id"] == anchor["meter_id"]
            and row["month"] == anchor["month"]
            and row["time_slot"] == anchor["time_slot"]
            and row["logical_date"] != anchor["logical_date"]
            and row["sample_id"] not in used
        ]
        selected = min(candidates, key=lambda row: hashlib.sha256(f"{SELECTION_NS}|S4|{index}|{row['sample_id']}".encode()).hexdigest(), default=None)
        if selected is not None:
            random_rows.append(selected)
            used.add(selected["sample_id"])
    chosen["S4_MATCHED_RANDOM"] = random_rows

    key_rows = []
    for group, values in chosen.items():
        for row in values:
            sample_id = row.get("case_id", row.get("sample_id"))
            score = scores_by_id[sample_id]
            key_rows.append({
                "group": group,
                "sample_id": sample_id,
                "meter_id": score["meter_id"],
                "timestamp": score["timestamp"],
                "literature_grade": row.get("literature_evidence_grade", "HIDDEN_RANDOM"),
                "h1_action": h1.get((score["meter_id"], score["timestamp"]), "normal"),
                "proxy_family_count": score["proxy_family_count"],
                "canonical_event_id": row.get("canonical_event_id", ""),
            })
    key_rows.sort(key=lambda row: hashlib.sha256(f"{ORDER_NS}|{row['sample_id']}|{row['group']}".encode()).hexdigest())
    if len({row["sample_id"] for row in key_rows}) != len(key_rows):
        raise RuntimeError("review packet contains duplicate case")

    raw = load_raw_currents()
    raw_by_meter: dict[str, dict[datetime, dict]] = defaultdict(dict)
    for row in raw:
        raw_by_meter[row["meter_id"]][row["timestamp"]] = row
    freeze = json.loads((ROOT / "lightguard_v0_1/data/validation/v11/v11_proxy_detector_freeze.json").read_text())
    d1_profiles = freeze["D1_P1_robust_meter_local_time_slot_residual"]["slot_profiles"]
    cards, template = [], []
    for index, key in enumerate(key_rows, start=1):
        blind_id = f"V12R-{index:03d}"
        key["blind_id"] = blind_id
        timestamp = datetime.fromisoformat(key["timestamp"])
        alias = hashlib.sha256(f"{ORDER_NS}|meter|{key['meter_id']}".encode()).hexdigest()[:10]
        trace = []
        for step in range(-4, 5):
            point_time = timestamp + timedelta(minutes=15 * step)
            point = raw_by_meter[key["meter_id"]].get(point_time)
            currents = point["currents"] if point else [None, None, None]
            slot = point_time.hour * 4 + point_time.minute // 15
            profile = d1_profiles[key["meter_id"]][str(slot)]
            trace.append({
                "relative_min": step * 15,
                "i1_a": currents[0],
                "i2_a": currents[1],
                "i3_a": currents[2],
                "baseline_low_total_a": round(float(profile["center"]) - float(profile["scale"]), 6),
                "baseline_high_total_a": round(float(profile["center"]) + float(profile["scale"]), 6),
                "missing_channels": sum(value is None for value in currents),
                "event_window": "CENTER" if step == 0 else "",
            })
        body = "".join("<tr>" + "".join(f"<td>{html.escape(str(value if value is not None else 'N/A'))}</td>" for value in row.values()) + "</tr>" for row in trace)
        cards.append(f"<section><h2>{blind_id}</h2><p>Meter alias: {alias} | uniform ±60-minute window</p><table><thead><tr><th>Relative min</th><th>I1 A</th><th>I2 A</th><th>I3 A</th><th>Past baseline low</th><th>Past baseline high</th><th>Missing</th><th>Window</th></tr></thead><tbody>{body}</tbody></table></section>")
        template.append({"reviewer_id": "", "blind_id": blind_id, "label": "", "confidence": "", "reason": "", "notes": ""})
    packet = """<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>AMI Trace Review</title><style>body{font-family:Georgia,sans-serif;background:#f4f0e5;color:#15372f;margin:2rem}section{background:white;padding:1rem;margin:1rem 0;border-left:6px solid #cb642f}table{border-collapse:collapse;width:100%}th,td{border:1px solid #bbb;padding:.3rem;text-align:right}</style></head><body><h1>Blinded AMI Trace Review</h1><p>파형만 보고 이상 징후 강도를 평가합니다. 현장 고장 확인 작업이 아닙니다.</p>""" + "".join(cards) + "</body></html>"
    packet_path = REPORTS / "v12r_blind_review_packet.html"
    packet_path.write_text(packet, encoding="utf-8")
    write_csv(REPORTS / "v12r_blind_review_template.csv", template, list(template[0]))
    write_csv(DATA / "v12r_review_results.csv", [], ["reviewer_id", "blind_id", "label", "confidence", "reason", "notes"])
    write_csv(DATA / "v12r_consensus_labels.csv", [], ["blind_id", "consensus_label", "reviewer_count", "agreement"])

    availability = {
        "S1_ALGORITHM_LITERATURE": len(s1),
        "S2_PROXY_LITERATURE": len(s2),
        "S3_SINGLETON_LITERATURE": len(singleton),
        "S4_MATCHED_RANDOM": len(anchors),
    }
    selected = Counter(row["group"] for row in key_rows)
    manifest = {
        "schema_version": "lightguard.v12r.review-manifest.1",
        "status": "PHASE_B_REVIEW_READY",
        "human_review_status": "HUMAN_REVIEW_PENDING",
        "selection_namespace": SELECTION_NS,
        "order_namespace": ORDER_NS,
        "requested": {"S1_ALGORITHM_LITERATURE": "all", "S2_PROXY_LITERATURE": 18, "S3_SINGLETON_LITERATURE": 18, "S4_MATCHED_RANDOM": 20},
        "available": availability,
        "selected": dict(selected),
        "shortfall_policy": "never fabricate or relabel unavailable cases",
        "hidden_from_reviewer": ["group", "H1", "proxy", "Literature Grade", "canonical six", "score", "rank"],
        "shown_to_reviewer": ["meter alias", "relative time", "I1/I2/I3", "past-only local baseline band", "missingness", "uniform event window"],
        "reviewer_labels_collected": False,
        "key_rows": key_rows,
        "packet_path": packet_path.relative_to(ROOT).as_posix(),
        "packet_sha256": sha(packet_path),
    }
    (DATA / "v12r_review_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    forbidden = ("S1_ALGORITHM", "S2_PROXY", "S3_SINGLETON", "S4_MATCHED", "EVIDENCE_A", "EVIDENCE_B", "H1", "canonical", "proxy_family_count")
    leaked = [term for term in forbidden if term in packet]
    audit = f"""# v0.12R Blindness Audit

- Packet cases: {len(key_rows)}
- Unique cases: {len({row['sample_id'] for row in key_rows})}
- Group availability: {json.dumps(availability, ensure_ascii=False)}
- Group selected: {json.dumps(dict(selected), ensure_ascii=False)}
- Hidden-field leakage found: {leaked}
- Reviewer labels collected: no
- Status: {'PASS' if not leaked else 'FAIL'}

Matched random selection uses meter, month, and time slot plus a fixed hash. Detector flags and literature grades do not enter random-case selection.
"""
    (REPORTS / "v12r_blindness_audit.md").write_text(audit, encoding="utf-8")
    if leaked:
        raise RuntimeError(f"blind packet leakage: {leaked}")
    print(json.dumps({"status": "REVIEW_READY", "cases": len(key_rows), "selected": dict(selected)}))


if __name__ == "__main__":
    main()
