#!/usr/bin/env python3
"""Emit the preregistered London provenance block; do not score it."""
from v14_common import CLAIM, DATA, REPORTS, frozen, result_fields, write_csv


def main() -> None:
    frozen(DATA / "v14_track_a_config.json")
    write_csv(REPORTS / "v14_london_results.csv", result_fields(), [{
        "dataset_id": "LONDON_MET_11442", "unit_id": "DATASET_GATE", "status": "PRIMARY_BLOCKED_PROVENANCE",
        "role": "REAL_DISTRIBUTION_CANDIDATE", "partial_run": False, "independent_unit": "NOT_ESTABLISHED",
        "interpretation": "License, label generation, chronology, and independent block provenance are insufficient; no performance was computed.",
        "claim_boundary": CLAIM,
    }])
    print("London: PRIMARY_BLOCKED_PROVENANCE")


if __name__ == "__main__":
    main()

