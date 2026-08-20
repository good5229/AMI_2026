#!/usr/bin/env python3
"""Build a claim-limited v0.13 canonical-six evidence matrix.

This join deliberately contains no probability, performance estimate, or field
truth.  External benchmark evidence is retained as mechanism evidence only.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V12 = ROOT / "lightguard_v0_1" / "reports" / "v12r"
V13_DATA = ROOT / "lightguard_v0_1" / "data" / "validation" / "v13"
V13_REPORTS = ROOT / "lightguard_v0_1" / "reports" / "v13"

FIELDS = [
    "event_id", "pattern", "literature_grade", "external_empirical_grade",
    "H1_action", "proxy_grade", "human_review_if_any", "field_confirmation",
    "final_claim",
]
CLAIM = (
    "External evidence supports signal-mechanism context only; not streetlight "
    "field accuracy, fault probability, or confirmed fault."
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def empirical_grade(status: str) -> str:
    return {
        "PASS": "EV-A_AUTHOR_SPLIT_LIMITED",
        "FAIL": "NO_EV_GRADE_NOT_SUPPORTED",
        "NOT_EVALUABLE_INCOMPLETE_COVERAGE": "NO_EV_GRADE_NOT_EVALUABLE",
    }[status]


def main() -> None:
    canonical = read_csv(ROOT / "lightguard_v0_1" / "reports" / "v11" / "v11_canonical_six_proxy_review.csv")
    if len(canonical) != 6:
        raise RuntimeError("v0.13 canonical evidence requires exactly six frozen v0.11 cases")
    literature = V12 / "v12r_canonical_six_evidence.md"
    if not literature.is_file():
        raise RuntimeError("missing v0.12R canonical literature evidence")
    summary = json.loads((ROOT / "lightguard_app" / "assets" / "data" / "context" / "v12r_literature_summary.json").read_text(encoding="utf-8"))
    if summary.get("review_status") != "HUMAN_REVIEW_PENDING":
        raise RuntimeError("v0.13 must not replace the v0.12R human-review state")
    mapping = json.loads((V13_DATA / "v13_feature_mapping.json").read_text(encoding="utf-8"))
    if mapping.get("status") != "PRE_OUTCOME_FROZEN":
        raise RuntimeError("feature mapping was not frozen before evidence join")
    mad = read_csv(V13_REPORTS / "v13_mad_confirmatory_results.csv")
    primary = [row for row in mad if row.get("candidate") == "SC3 primary gate"]
    if len(primary) != 1 or primary[0].get("status") not in {
        "PASS", "FAIL", "NOT_EVALUABLE_INCOMPLETE_COVERAGE",
    }:
        raise RuntimeError("missing truthful primary MAD status")
    ev_grade = empirical_grade(primary[0]["status"])
    rows = []
    for item in canonical:
        rows.append({
            "event_id": item["event"],
            "pattern": "frozen v0.11 canonical anomaly-sign candidate",
            "literature_grade": "EVIDENCE_A_TO_C_PATTERN_BOUND",
            "external_empirical_grade": ev_grade,
            "H1_action": item["h1"],
            "proxy_grade": f"proxy_family_count={item['proxy_family_count']}",
            "human_review_if_any": "PENDING",
            "field_confirmation": "NOT_AVAILABLE",
            "final_claim": CLAIM,
        })
    V13_DATA.mkdir(parents=True, exist_ok=True)
    destination = V13_DATA / "v13_case_evidence_matrix.csv"
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"canonical_cases": len(rows), "columns": len(FIELDS)}, sort_keys=True))


if __name__ == "__main__":
    main()
