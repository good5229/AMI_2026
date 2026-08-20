#!/usr/bin/env python3
"""REFIT gate: truthfully report blocked status unless official source files exist."""
from __future__ import annotations

from v13_common import CLAIM_BOUNDARY, RAW_ROOT, V13_REPORTS, atomic_write_csv


def main() -> None:
    refit = RAW_ROOT / "REFIT"
    status = "BLOCKED_EXTERNAL_DATA" if not refit.is_dir() else "BLOCKED_UNVERIFIED_LABEL_RULE_AND_PRETEST_SPLIT"
    atomic_write_csv(
        V13_REPORTS / "v13_refit_results.csv",
        ["dataset", "status", "metrics_published", "reason", "claim_boundary"],
        [{
            "dataset": "External REFIT", "status": status, "metrics_published": False,
            "reason": "Official REFIT annotation files are unavailable." if not refit.is_dir() else "No frozen label rule and pre-test split are available.",
            "claim_boundary": CLAIM_BOUNDARY,
        }],
    )
    print(status)


if __name__ == "__main__":
    main()
