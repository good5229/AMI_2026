#!/usr/bin/env python3
from __future__ import annotations

import csv

from v16_common import DATA, REPORT, write_csv


def truth(value): return str(value).lower() in {"true", "1", "yes"}


def main() -> None:
    with (DATA / "v16_service_policy_results.csv").open(newline="", encoding="utf-8") as stream: rows = list(csv.DictReader(stream))
    table = {(row["pair_id"], row["policy"]): row for row in rows}
    result = []
    for endpoint, field, operator_class in (("R", "anomaly_dispatch_capture", "anomaly"), ("B", "benign_dispatch_escalation", "benign")):
        ids = sorted({row["pair_id"] for row in rows if row["operator_class"] == operator_class})
        pairs = []
        for pair_id in ids:
            p0, p1 = table[(pair_id, "P0_COLLAPSED_NON_NORMAL")], table[(pair_id, "P1_GUARDED_LANES")]
            pairs.append((p0["meter_id"], truth(p1[field]), truth(p0[field])))
        n = len(pairs)
        n10 = sum(p1 and not p0 for _, p1, p0 in pairs)
        n01 = sum(not p1 and p0 for _, p1, p0 in pairs)
        rd = sum(p1 - p0 for _, p1, p0 in pairs) / n
        result.append({"endpoint": endpoint, "comparison": "P1_MINUS_P0", "pairs": n, "p1_rate": f"{sum(p1 for _,p1,_ in pairs)/n:.8f}", "p0_rate": f"{sum(p0 for _,_,p0 in pairs)/n:.8f}", "paired_rd": f"{rd:.8f}", "n10": n10, "n01": n01, "analysis_status": "POST_HOC_DESCRIPTIVE_ONLY", "prospective_target": "R_RD>=-0.10" if endpoint == "R" else "B_RD<=-0.10"})
    fields = list(result[0])
    write_csv(REPORT / "v16_paired_service_utility.csv", fields, result)
    strata = []
    for key in ("meter_id", "operator", "expected_phase_count"):
        for value in sorted({row[key] for row in rows}, key=str):
            group = [row for row in rows if str(row[key]) == str(value) and row["policy"] == "P1_GUARDED_LANES"]
            strata.append({"stratum_type": key, "stratum": value, "rows": len(group), "field_candidates": sum(row["injected_lane"] == "FIELD_INSPECTION_CANDIDATE" for row in group), "data_quality_reviews": sum(row["injected_lane"] == "DATA_QUALITY_REVIEW" for row in group), "remote_monitors": sum(row["injected_lane"] == "REMOTE_MONITOR" for row in group)})
    write_csv(REPORT / "v16_service_strata.csv", list(strata[0]), strata)
    natural = []
    for row in rows:
        if row["policy"] == "P1_GUARDED_LANES":
            natural.append({"pair_id": row["pair_id"], "meter_id": row["meter_id"], "local_date": row["local_date"], "policy": row["policy"], "target_side_lane": row["control_lane"], "interpretation": "TRUTH_FREE_ORIGINAL_TARGET_SIDE"})
    write_csv(DATA / "v16_natural_shadow.csv", list(natural[0]), natural)


if __name__ == "__main__":
    main()
