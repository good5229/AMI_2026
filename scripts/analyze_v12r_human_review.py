#!/usr/bin/env python3
"""Analyze human reviews only after at least two real reviewers are present."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v12r"
REPORT = ROOT / "lightguard_v0_1/reports/v12r/v12r_human_review_analysis.md"


def main() -> None:
    with (DATA / "v12r_review_results.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    reviewers = {row["reviewer_id"] for row in rows if row["reviewer_id"]}
    if len(reviewers) < 2:
        REPORT.write_text("# v0.12R Human Review Analysis\n\nStatus: **HUMAN_REVIEW_PENDING**\n\nNo agent-generated labels are permitted. At least two real reviewers are required before agreement or enrichment is calculated.\n", encoding="utf-8")
        print(json.dumps({"status": "HUMAN_REVIEW_PENDING", "reviewers": len(reviewers), "labels": len(rows)}))
        return
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["blind_id"]].append(row["label"])
    consensus = []
    for blind_id, labels in sorted(grouped.items()):
        winner, count = Counter(labels).most_common(1)[0]
        consensus.append({"blind_id": blind_id, "consensus_label": winner, "reviewer_count": len(labels), "agreement": round(count / len(labels), 8)})
    with (DATA / "v12r_consensus_labels.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(consensus[0]))
        writer.writeheader(); writer.writerows(consensus)
    REPORT.write_text(f"# v0.12R Human Review Analysis\n\nStatus: **REVIEW_IMPORTED_ANALYSIS_REQUIRED**\n\nReviewers: {len(reviewers)}  \nCases: {len(consensus)}\n\nAgreement and preregistered permutation/bootstrap analysis must be completed before unblinding claims.\n", encoding="utf-8")
    print(json.dumps({"status": "REVIEW_IMPORTED_ANALYSIS_REQUIRED", "reviewers": len(reviewers), "cases": len(consensus)}))


if __name__ == "__main__":
    main()
