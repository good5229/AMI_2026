#!/usr/bin/env python3
"""UCR DG-C gate.  License-unknown data is withheld before any metric computation."""
from __future__ import annotations

from v13_common import CLAIM_BOUNDARY, V13_DATA, V13_REPORTS, atomic_write_csv, load_json


def main() -> None:
    registry = load_json(V13_DATA / "v13_external_dataset_registry.json")
    record = next(item for item in registry["records"] if item["dataset_id"] == "UCR_ANOMALY_ARCHIVE_ITALIANPOWERDEMAND_2021")
    allowed = record.get("license") != "UNKNOWN" and record.get("execution_eligibility") is True
    status = "LICENSED_EXECUTION_NOT_IMPLEMENTED_DG_C_ONLY" if allowed else "WITHHELD_LICENSE_UNKNOWN"
    rows = [{
        "dataset": "External UCR ItalianPowerDemand", "file_id": file_id, "quality_grade": "DG-C",
        "status": status, "metrics_published": False,
        "claim_boundary": "Generic temporal stress only; not electrical mechanism validity, streetlight field accuracy, or fault probability.",
    } for file_id in ("210", "211", "212")]
    atomic_write_csv(V13_REPORTS / "v13_ucr_results.csv", ["dataset", "file_id", "quality_grade", "status", "metrics_published", "claim_boundary"], rows)
    print(status)


if __name__ == "__main__":
    main()
