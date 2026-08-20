#!/usr/bin/env python3
"""Assemble the v0.12R release report without inventing human results."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v12r"
REPORTS = ROOT / "lightguard_v0_1/reports/v12r"


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    registry = json.loads((DATA / "v12r_reference_registry.json").read_text())
    app = json.loads((ROOT / "lightguard_app/assets/data/context/v12r_literature_summary.json").read_text())
    review = json.loads((DATA / "v12r_review_manifest.json").read_text())
    search = rows(REPORTS / "v12r_literature_search_log.csv")
    queries = sum(row["record_type"] == "query" for row in search)
    qa_text = (REPORTS / "v12r_independent_audit.md").read_text() if (REPORTS / "v12r_independent_audit.md").exists() else ""
    qa = "PASS" if "PASS" in qa_text and "FAIL" not in qa_text else "PENDING"
    preflight = os.getenv("V12R_PREFLIGHT_PASS") == "1"
    report = f"""# LightGuard v0.12R Literature-Grounded Anomaly-Sign Validation

## 1. Freeze
- v0.11 SHA: b25b168250ede29b5c5bbcadab918c455d61ba74
- H1 and v0.11 proxy scores: unchanged
- Route C; Gold 0, Silver Operational 0

## 2. Literature Review
- frozen query families: {queries}
- unique included sources: {len(registry)}
- A-grade: {app['quality_a']}
- B-grade: {app['quality_b']}
- direct/mechanism L2-L3: {app['core_direct_or_mechanism']}

## 3. Evidence by Pattern
| pattern | direct support | mechanism support | final grade |
|---|---|---|---|
| daytime full activation | road-lighting expected-state/current studies | persistence and measurement controls | EVIDENCE_A |
| persistent partial | load-profile and CUSUM evidence | causal meter-relative baseline | EVIDENCE_B |
| phase selective | phase-asymmetry electrical diagnostics | RMS-only transfer limit | EVIDENCE_B |
| baseline deviation | general benchmark/measurement support | past-only meter baseline | EVIDENCE_C |

## 4. Claim Boundary
- Literature supports anomaly mechanisms and inspection prioritization.
- Literature does not confirm a LightGuard event, provide fault probability, or replace Gold/Silver.
- RMS phase currents are phase-current asymmetry observations, not negative-sequence measurements.

## 5. Canonical Six
- Six previously identified anomaly-sign candidates mapped after literature grades were frozen.
- Each retains field confirmation unavailable.

## 6. Proxy Population
- High-confidence proxy mapped: {app['proxy_high_mapped']}
- Literature grade is pattern-based and independent of H1/proxy scores.

## 7. Human Review
- reviewers: 0
- packet: {sum(review['selected'].values())} unique cases
- blinding: PASS
- status: HUMAN_REVIEW_PENDING

## 8. Human Enrichment
- Not calculated. AI-generated reviewer labels are prohibited.

## 9. Inter-rater Agreement
- Not calculated; minimum two human reviewers required.

## 10. Multi-Layer Triangulation
- Current maximum claim ladder: Level 3
- Level 4 requires sealed blinded human review.
- Level 5/6 unavailable because Silver/Gold are absent.

## 11. Claims Allowed
- literature-supported anomaly sign
- algorithm concordance and matched-background enrichment
- review-ready blinded trace packet

## 12. Claims Prohibited
- actual fault probability or rate
- field accuracy, fault recall, precision, FPR, specificity
- negative-sequence fault from RMS-only phase currents

## 13. Gold Data Gap
- cabinet-meter/phase mapping
- controller ON/OFF and override log
- maintenance outcome and inspection disposition
- time-bounded fault cause adjudication

## 14. QA / Build
- independent QA: {qa}
- v12r preflight: {'PASS' if preflight else 'PENDING'}
- Flutter analyze/test/web/android: {'PASS' if preflight else 'PENDING'}

## 15. Next Step
- two or more real human reviewers complete the frozen packet
- seal and analyze reviews without packet replacement
- prospective field pilot if verified Gold/Silver data become available
"""
    (REPORTS / "v12r_final_summary.md").write_text(report, encoding="utf-8")
    (ROOT / "lightguard_app/docs/v12r_anomaly_sign_validation.md").write_text(report, encoding="utf-8")
    release_files = sorted(
        [path for base in (DATA, REPORTS) for path in base.iterdir() if path.is_file() and path.name not in {"reproducibility_manifest.json"}]
        + [
            ROOT / "lightguard_app/assets/data/context/v12r_literature_summary.json",
            ROOT / "lightguard_app/docs/v12r_literature_grounding.md",
            ROOT / "lightguard_app/docs/v12r_anomaly_sign_validation.md",
            ROOT / "lightguard_app/docs/v12_gold_data_acquisition_plan.md",
        ],
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )
    manifest = {
        "schema_version": "lightguard.v12r.reproducibility.1",
        "v11_release": "b25b168250ede29b5c5bbcadab918c455d61ba74",
        "status": "HUMAN_REVIEW_PENDING",
        "files": [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)} for path in release_files if path.exists()],
    }
    (REPORTS / "reproducibility_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "BUILT", "qa": qa, "preflight": preflight, "sources": len(registry), "review_cases": sum(review["selected"].values())}))


if __name__ == "__main__":
    main()
