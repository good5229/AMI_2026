#!/usr/bin/env python3
"""Carry the canonical six forward without adding probability columns."""
from v14_common import CLAIM, DATA, V13_DATA, read_csv, write_csv


def main() -> None:
    source = read_csv(V13_DATA / "v13_case_evidence_matrix.csv")
    rows = []
    for row in source:
        rows.append({"event_id": row["event_id"], "pattern": row["pattern"],
                     "v13_external_empirical_grade": row["external_empirical_grade"],
                     "v14_physical_replication": "EXTERNAL_MECHANISM_ONLY_NOT_CASE_ADJUDICATION",
                     "field_confirmation": row["field_confirmation"], "final_claim": CLAIM})
    write_csv(DATA / "v14_case_evidence_matrix.csv",
              ["event_id", "pattern", "v13_external_empirical_grade", "v14_physical_replication", "field_confirmation", "final_claim"], rows)
    print("v0.14 canonical-six evidence matrix built")


if __name__ == "__main__":
    main()

