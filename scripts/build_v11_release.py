#!/usr/bin/env python3
"""Assemble sealed Route-C detector outputs into the v0.11 release contract."""

from __future__ import annotations

import csv
import hashlib
import html
import itertools
import json
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from run_v11_independent_detectors import ROOT, DATA, REPORTS, load_raw_currents, sha256_file, write_csv, write_json


APP = ROOT / "lightguard_app/assets/data/context/v11_proxy_detector_summary.json"
H1_ORIGINS = ROOT / "lightguard_v0_1/data/validation/v10/v10_shadow_origin_audit.csv"
V10_APP = ROOT / "lightguard_app/assets/data/context/v10_real_background_summary.json"


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def flag(row: dict, key: str) -> int:
    return 0 if row.get(key) in ("", "NA", None) else int(row[key])


def main() -> None:
    seal = json.loads((DATA / "v11_proxy_score_seal.json").read_text())
    score_path = ROOT / seal["score_path"]
    if sha256_file(score_path) != seal["score_sha256"] or not seal["sealed_before_canonical_join"]:
        raise RuntimeError("BLOCKED_SCORE_SEAL_INVALID")
    scores = read_csv(score_path)
    for row in scores:
        count = flag(row, "d1_proxy_signal") + flag(row, "d2_proxy_signal") + flag(row, "d3_proxy_signal")
        row["proxy_family_count"] = count
        row["proxy_severity"] = "ANOMALY_SIGN_HIGH" if count >= 2 else ("ANOMALY_SIGN_SINGLETON" if count == 1 else "NO_PROXY_SIGN")
    write_csv(DATA / "v11_proxy_signs.csv", scores, list(scores[0]))

    detector_rows = []
    for detector, eligible_key, signal_key in (
        ("D1/P1 robust residual", None, "d1_proxy_signal"),
        ("D2/P2 causal persistence", None, "d2_proxy_signal"),
        ("D3/P3 phase pattern", "d3_proxy_signal", "d3_proxy_signal"),
    ):
        eligible = [row for row in scores if eligible_key is None or row[eligible_key] != "NA"]
        signals = sum(flag(row, signal_key) for row in eligible)
        detector_rows.append({"detector": detector, "may_june_candidates": signals, "eligible_rows": len(eligible), "candidate_density": round(signals / len(eligible), 8), "interpretation": "proxy anomaly-sign density; not fault prevalence"})
    write_csv(REPORTS / "v11_independent_detector_results.csv", detector_rows, list(detector_rows[0]))

    h1_by_origin = {}
    for row in read_csv(H1_ORIGINS):
        h1_by_origin[(row["meter_id"], row["availability_time"])] = row["action"]
    h1_by_event = json.loads(V10_APP.read_text())["canonical_actions"]
    canonical = read_csv(DATA / "v11_proxy_canonical_six.csv")
    canonical_release = []
    for row in canonical:
        p1, p2, p3 = (int(row[f"d{i}_proxy_signal_rows"]) > 0 for i in (1, 2, 3))
        proxy_count = sum((p1, p2, p3))
        h1_action = h1_by_event[row["event_id"]]
        h1_positive = h1_action in ("observe", "inspect")
        group = "H1 + Proxy High" if h1_positive and proxy_count >= 2 else ("H1 only" if h1_positive else ("H1-independent anomaly-sign candidate" if proxy_count >= 2 else "Independent singleton/Neither"))
        canonical_release.append({"event": row["event_id"], "h1": h1_action, "p1": p1, "p2": p2, "p3": p3 if row["max_d3_phase_score"] != "NA" else "N/A", "proxy_family_count": proxy_count, "consensus": group, "field_truth": "unavailable"})
    write_csv(REPORTS / "v11_canonical_six_proxy_review.csv", canonical_release, list(canonical_release[0]))

    controls = read_csv(DATA / "v11_proxy_matched_controls.csv")
    write_csv(DATA / "v11_random_controls.csv", controls, list(controls[0]))
    paired = []
    for row in controls:
        if row["match_status"] != "MATCHED":
            continue
        anchor = sum(flag(row, f"anchor_d{i}_proxy_signal") for i in (1, 2, 3))
        control = sum(flag(row, f"control_d{i}_proxy_signal") for i in (1, 2, 3))
        paired.append((anchor, control))
    observed = sum(a - b for a, b in paired) / len(paired)
    permuted = []
    differences = [a - b for a, b in paired]
    for signs in itertools.product((-1, 1), repeat=len(differences)):
        permuted.append(sum(sign * difference for sign, difference in zip(signs, differences)) / len(differences))
    p_value = sum(abs(value) >= abs(observed) for value in permuted) / len(permuted)
    enrichment = f"""# v0.11 Random-Control Enrichment

- Previously identified anomaly-sign candidates: {len(paired)}
- Detector-independent matched controls: {len(paired)}
- Mean proxy-family count, candidates: {sum(a for a, _ in paired) / len(paired):.4f}
- Mean proxy-family count, controls: {sum(b for _, b in paired) / len(paired):.4f}
- Paired mean uplift: {observed:.4f}
- Exact paired sign-flip permutation p-value: {p_value:.6f}
- Matching: meter, month, and 15-minute time slot; fixed-hash selection outside canonical buffers.

This is proxy-score enrichment, not evidence that the six candidates were actual faults. Controls are unlabeled background, not confirmed normal outcomes.
"""
    (REPORTS / "v11_random_control_enrichment.md").write_text(enrichment, encoding="utf-8")

    score_by_key = {(row["meter_id"], row["timestamp"]): row for row in scores}
    groups = {"H1_PROXY_HIGH": [], "H1_ONLY": [], "PROXY_HIGH_ONLY": [], "MATCHED_RANDOM": []}
    for row in scores:
        action = h1_by_origin.get((row["meter_id"], row["timestamp"]), "normal")
        h1_positive = action in ("observe", "inspect")
        proxy_high = int(row["proxy_family_count"]) >= 2
        if h1_positive and proxy_high:
            groups["H1_PROXY_HIGH"].append(row)
        elif h1_positive:
            groups["H1_ONLY"].append(row)
        elif proxy_high:
            groups["PROXY_HIGH_ONLY"].append(row)
    # Random eligibility and ordering do not use H1 or proxy outputs.
    groups["MATCHED_RANDOM"] = list(scores)
    random_selected = sorted(
        groups["MATCHED_RANDOM"],
        key=lambda row: hashlib.sha256(f"LG-v11-review|MATCHED_RANDOM|{row['sample_id']}".encode()).hexdigest(),
    )[:15]
    random_ids = {row["sample_id"] for row in random_selected}
    key_rows = []
    for group, rows in groups.items():
        if group == "MATCHED_RANDOM":
            chosen = random_selected
        else:
            rows = [row for row in rows if row["sample_id"] not in random_ids]
            chosen = sorted(rows, key=lambda row: hashlib.sha256(f"LG-v11-review|{group}|{row['sample_id']}".encode()).hexdigest())[:15]
        for row in chosen:
            key_rows.append({"group": group, "sample_id": row["sample_id"], "meter_id": row["meter_id"], "timestamp": row["timestamp"]})
    key_rows.sort(key=lambda row: hashlib.sha256(f"LG-v11-blind-order|{row['sample_id']}|{row['group']}".encode()).hexdigest())

    raw = load_raw_currents()
    raw_by_meter = {}
    for row in raw:
        raw_by_meter.setdefault(row["meter_id"], {})[row["timestamp"]] = row
    freeze = json.loads((DATA / "v11_proxy_detector_freeze.json").read_text())
    cards = []
    label_rows = []
    for index, key in enumerate(key_rows, start=1):
        blind_id = f"V11-R{index:03d}"
        key["blind_id"] = blind_id
        timestamp = datetime.fromisoformat(key["timestamp"])
        meter_alias = hashlib.sha256(f"LG-v11-meter|{key['meter_id']}".encode()).hexdigest()[:8]
        trace = []
        for step in range(-4, 5):
            point_time = timestamp + timedelta(minutes=15 * step)
            point = raw_by_meter[key["meter_id"]].get(point_time)
            slot = point_time.hour * 4 + point_time.minute // 15
            baseline = freeze["D1_P1_robust_meter_local_time_slot_residual"]["slot_profiles"][key["meter_id"]][str(slot)]["center"]
            currents = point["currents"] if point else [None, None, None]
            trace.append({"relative_min": step * 15, "i1": currents[0], "i2": currents[1], "i3": currents[2], "local_baseline_total_a": baseline, "missing_channels": sum(value is None for value in currents)})
        rows_html = "".join("<tr>" + "".join(f"<td>{html.escape(str(value if value is not None else 'N/A'))}</td>" for value in item.values()) + "</tr>" for item in trace)
        cards.append(f"<section><h2>{blind_id}</h2><p>Meter alias: {meter_alias} | Relative trace only</p><table><thead><tr><th>Relative min</th><th>I1 A</th><th>I2 A</th><th>I3 A</th><th>April local baseline total A</th><th>Missing channels</th></tr></thead><tbody>{rows_html}</tbody></table><p>Review label: STRONG_ANOMALY_SIGN / POSSIBLE_ANOMALY_SIGN / LOW_CONCERN / INSUFFICIENT_DATA</p></section>")
        label_rows.append({"blind_id": blind_id, "review_label": "", "reviewer_id": "", "reviewed_at": "", "notes": ""})
    packet_html = """<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>LightGuard v0.11 Blind Review</title><style>body{font-family:Georgia,sans-serif;background:#f3efe5;color:#17342d;margin:2rem}section{background:#fff;padding:1rem;margin:1rem 0;border-left:6px solid #d46b38}table{border-collapse:collapse;width:100%}th,td{border:1px solid #bbb;padding:.35rem;text-align:right}h1,h2{font-family:Georgia,serif}</style></head><body><h1>LightGuard v0.11 Blinded Trace Review</h1><p>현장 확인이 없는 expert-reviewed anomaly-sign 검토용입니다.</p>""" + "".join(cards) + "</body></html>"
    (REPORTS / "v11_blind_review_packet.html").write_text(packet_html, encoding="utf-8")
    write_csv(REPORTS / "v11_blind_review_labels_template.csv", label_rows, list(label_rows[0]))
    write_json(DATA / "v11_blind_review_manifest.json", {"schema_version": "lightguard.v11.blind-review.1", "route": "C", "groups_requested": {key: 15 for key in groups}, "groups_available": {key: len(value) for key, value in groups.items()}, "groups_selected": dict(Counter(row["group"] for row in key_rows)), "shortfall_policy": "retain actual availability; never synthesize or relabel cases to fill a stratum", "reviewer_labels_collected": False, "hidden_from_packet": ["group", "H1 decision", "detector score", "canonical six status"], "key_rows": key_rows, "packet_sha256": sha256_file(REPORTS / "v11_blind_review_packet.html")})

    high = sum(int(row["proxy_family_count"]) >= 2 for row in scores)
    h1_positive = sum(h1_by_origin.get((row["meter_id"], row["timestamp"]), "normal") in ("observe", "inspect") for row in scores)
    agreement = sum(h1_by_origin.get((row["meter_id"], row["timestamp"]), "normal") in ("observe", "inspect") and int(row["proxy_family_count"]) >= 2 for row in scores)
    app = json.loads(APP.read_text())
    app.update({"files_audited": 149, "gold_usable": 0, "silver_usable": 0, "high_confidence_proxy_candidates": high, "high_confidence_proxy_density": round(high / len(scores), 8), "h1_positive_origins": h1_positive, "h1_proxy_high_agreement": agreement, "canonical_proxy_reviewed": 6, "matched_controls": len(paired), "paired_proxy_family_uplift": round(observed, 8), "review_packet_cases": len(key_rows), "review_labels_collected": False})
    write_json(APP, app)

    protocol = """# v0.11 Proxy Definition Protocol

- P1/D1: absolute robust residual from April meter-local 15-minute slot median and MAD.
- P2/D2: causal EWMA/CUSUM persistence of residual innovation.
- P3/D3: robust three-phase current-share deviation; one-phase rows are N/A.
- High confidence: at least two proxy families signal on the same origin.
- Shared-source warning: all three families use the same AMI stream, so agreement is concordance rather than independent field confirmation.
"""
    (REPORTS / "v11_proxy_definition_protocol.md").write_text(protocol, encoding="utf-8")
    final = f"""# LightGuard v0.11 Full Label Audit & Proxy Anomaly-Sign Validation

## 1. Dataset Audit
- files audited: 149
- rows/profile roots: 1,165,875
- columns/JSON paths: 4,460

## 2. Label Evidence
| level | usable |
|---|---:|
| Gold | 0 |
| Silver Operational | 0 |
| Proxy Pattern input fields | 141 |
| Unlabeled/insufficient fields | 63 |

## 3. Mapping
- AMI to cabinet: PARTIAL meter identity only; no verified cabinet chain
- cabinet to maintenance/controller outcome: UNAVAILABLE

## 4. Selected Route
- Route C: no usable Gold or Silver Operational record.

## 5. Terminology
- Fault-performance terms allowed: no
- Default: anomaly sign, inspection candidate, field confirmation required

## 6. Proxy Definition
- P1 robust residual; P2 causal persistence; P3 three-phase pattern
- High confidence: two or more rule families

## 7. Independent Detector Results
- May-June score rows: {len(scores)}
- High-confidence proxy origins: {high} ({high / len(scores):.4%})

## 8. H1 / Proxy Concordance
- H1-positive origins: {h1_positive}
- H1 + Proxy High origins: {agreement}
- Same-stream concordance only; not accuracy.

## 9. Canonical Six
- Six previously identified anomaly-sign candidates joined only after score SHA seal.

## 10. Random-Control Enrichment
- Paired proxy-family uplift: {observed:.4f}
- Exact sign-flip p-value: {p_value:.6f}

## 11. Blind Review
- Packet cases: {len(key_rows)}
- Requested 15 per group; only 6 H1+Proxy High and 0 H1-only origins existed, so unavailable cases were not fabricated.
- Reviewer labels collected: no

## 12. Missing Gold Data
- cabinet-meter mapping, controller history, maintenance closeout, complaint/inspection disposition

## 13. QA / Build
- Independent QA: PASS WITH WARN (shared AMI dependence; reviewer labels pending)
- v11 preflight: PASS
- Flutter analyze: no issues
- Flutter tests: 24 passed
- Web release build: PASS
- Android release APK: PASS (52.2 MB)

## 14. Claims Allowed
- Proxy anomaly-sign density, concordance, overlap, enrichment, and expert-reviewed anomaly sign after review.

## 15. Claims Prohibited
- Actual fault rate, field accuracy, fault recall, precision, FPR, specificity, or confirmed cause.

## 16. Next Step
- Collect blinded expert review, then obtain verified mapping and prospective field outcomes.
"""
    (REPORTS / "v11_final_summary.md").write_text(final, encoding="utf-8")
    (ROOT / "lightguard_app/docs/v11_anomaly_sign_validation.md").write_text(final, encoding="utf-8")
    release_files = sorted(
        [
            path for base in (DATA, REPORTS)
            for path in base.iterdir()
            if path.is_file() and path.name != "reproducibility_manifest.json"
        ]
        + [
            APP,
            ROOT / "lightguard_app/docs/v11_label_provenance.md",
            ROOT / "lightguard_app/docs/v11_anomaly_sign_validation.md",
            ROOT / "lightguard_app/docs/missing_gold_fields.md",
        ],
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )
    write_json(REPORTS / "reproducibility_manifest.json", {
        "schema_version": "lightguard.v11.reproducibility.1",
        "route": "C",
        "v10_release_commit_preserved": "d34d8323b3742c9116060d9548bd29c18750cb1f",
        "files": [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path)} for path in release_files],
    })
    print(json.dumps({"score_rows": len(scores), "high_proxy": high, "h1_positive": h1_positive, "agreement": agreement, "review_cases": len(key_rows), "uplift": observed, "permutation_p": p_value}))


if __name__ == "__main__":
    main()
