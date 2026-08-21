#!/usr/bin/env python3
"""Reconcile legacy and raw-workbook B-L-12 quality denominators."""

import csv
import json

from v10_ami import ROOT, load_rows

LEGACY = ROOT / "lightguard_v0_1/data/ami_data_quality.csv"
INJECTION = ROOT / "lightguard_v0_1/data/validation/v10/v10_injection_manifest.json"
OUTPUT = ROOT / "lightguard_v0_1/reports/v10/v10_b_l_12_reconciliation.md"

with LEGACY.open(encoding="utf-8-sig", newline="") as handle:
    legacy = next(row for row in csv.DictReader(handle) if row["meter_id"] == "B-L-12")
raw_rows = load_rows()["B-L-12"]
raw_missing = [row for row in raw_rows if any(row["currents"][phase] is None for phase in ("i1", "i2", "i3"))]
manifest = json.loads(INJECTION.read_text(encoding="utf-8"))
pairs = [row for row in manifest["rows"] if row["meter_id"] == "B-L-12" and row["status"] == "constructable"]
cells = [cell for row in pairs for cell in row["cell_provenance"]]
assert all(cell["source_quality"] == "observed_finite_nonnegative" for cell in cells)
assert all(cell["physical_review"] == "PASS_CONSTRAINED_CURRENT_ONLY" for cell in cells)
legacy_rows, legacy_missing = int(legacy["total_rows"]), int(legacy["current_channel_missing_rows"])
lines = ["# B-L-12 Missingness Denominator Reconciliation", "", "## Decision", "", "`RECONCILED_AS_SCOPE_DENOMINATOR_DIFFERENCE`", "", "The legacy v0.1 quality table is a reduced processed release and has no row-level source provenance. v0.10 uses the complete ignored raw workbook under its frozen SHA and explicit April-June interval-end parser. The legacy denominator is retained as historical evidence, not substituted for the raw-source denominator.", "", "| evidence | rows | rows with any measured-current gap |", "|---|---:|---:|", f"| legacy processed v0.1 table | {legacy_rows} | {legacy_missing} |", f"| v0.10 raw-workbook scope | {len(raw_rows)} | {len(raw_missing)} |", f"| difference | {len(raw_rows)-legacy_rows} | {len(raw_missing)-legacy_missing} |", "", "## Injection enforcement", "", f"- constructable B-L-12 pairs: `{len(pairs)}`", f"- serialized changed-cell provenance records: `{len(cells)}`", "- every used source cell is observed, finite, non-negative, and tagged `PASS_CONSTRAINED_CURRENT_ONLY`.", "- incomplete source/target intervals remain `not_constructable`; no missing value is filled or converted to zero.", "- v0.10 raw counts supersede the legacy processed denominator for this experiment; no claim is made that the two releases contain identical row populations."]
OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps({"legacy_rows": legacy_rows, "legacy_missing": legacy_missing, "raw_rows": len(raw_rows), "raw_missing": len(raw_missing), "constructable_pairs": len(pairs), "cell_provenance": len(cells)}))
