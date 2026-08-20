#!/usr/bin/env python3
"""Import real human review CSVs without synthesizing missing labels."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v12r"
INPUT = DATA / "reviewer_inputs"
LABELS = {"STRONG_ANOMALY_SIGN", "POSSIBLE_ANOMALY_SIGN", "LOW_CONCERN", "INSUFFICIENT_DATA"}
REASONS = {"unexpected_level", "unexpected_duration", "phase_pattern", "abrupt_change", "baseline_deviation", "data_quality", "unclear", "other"}


def main() -> None:
    manifest = json.loads((DATA / "v12r_review_manifest.json").read_text())
    valid_ids = {row["blind_id"] for row in manifest["key_rows"]}
    paths = sorted(INPUT.glob("*.csv")) if INPUT.exists() else []
    if not paths:
        print(json.dumps({"status": "HUMAN_REVIEW_PENDING", "files": 0, "labels": 0}))
        return
    rows, pairs = [], set()
    for path in paths:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                pair = (row["reviewer_id"].strip(), row["blind_id"].strip())
                if not pair[0] or pair[1] not in valid_ids or pair in pairs:
                    raise RuntimeError(f"invalid or duplicate reviewer/case in {path.name}")
                if row["label"] not in LABELS or row["reason"] not in REASONS or not 1 <= int(row["confidence"]) <= 5:
                    raise RuntimeError(f"invalid review value in {path.name}: {pair}")
                pairs.add(pair)
                rows.append({key: row.get(key, "") for key in ("reviewer_id", "blind_id", "label", "confidence", "reason", "notes")})
    with (DATA / "v12r_review_results.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"status": "IMPORTED_HUMAN_REVIEW", "files": len(paths), "labels": len(rows), "reviewers": len({row["reviewer_id"] for row in rows})}))


if __name__ == "__main__":
    main()
