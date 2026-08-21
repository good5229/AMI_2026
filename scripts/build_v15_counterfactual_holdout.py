#!/usr/bin/env python3
"""Select up to 150 balanced, one-operator-per-meter-day counterfactual pairs."""
from __future__ import annotations

from collections import defaultdict

from v15_common import DATA, HOLDOUT_MANIFEST, INJECTION_MANIFEST, LEGACY_HOLDOUT_MANIFEST, RESULT_FIELDS, SEED, canonical_json_sha, load_json, require, write_json


def main() -> None:
    pool = load_json(DATA / "v15_remaining_pool.json")
    candidates = pool["candidates"]
    buckets = defaultdict(list)
    for row in candidates:
        buckets[(row["operator"], row["operator_class"])].append(row)
    selected, used_days = [], set()
    # Round robin yields balanced operator/classes until a stratum is exhausted.
    ordered = sorted(buckets)
    while len(selected) < 150:
        progressed = False
        for bucket in ordered:
            while buckets[bucket] and (buckets[bucket][0]["meter_id"], buckets[bucket][0]["local_date"]) in used_days:
                buckets[bucket].pop(0)
            if not buckets[bucket] or len(selected) >= 150: continue
            row = buckets[bucket].pop(0)
            unit = (row["meter_id"], row["local_date"])
            if unit in used_days: continue
            row = dict(row)
            row["pair_id"] = canonical_json_sha([SEED, unit, row["operator"], row["source_rows_sha256"], row["target_rows_sha256"]])[:24]
            row["pair_source_target_sha256"] = canonical_json_sha({"source": row["source_rows_sha256"], "target": row["target_rows_sha256"]})
            selected.append(row); used_days.add(unit); progressed = True
        if not progressed: break
    require(len(selected) > 0, "BLOCKED_NO_AVAILABLE_HOLDOUT")
    target = min(150, len({(row["meter_id"], row["local_date"]) for row in candidates}))
    require(len(selected) == target or len(selected) < 150, "BLOCKED_BAD_HOLDOUT_TARGET")
    require(len(used_days) == len(selected), "BLOCKED_MORE_THAN_ONE_OPERATOR_PER_METER_DAY")
    require(all(not row["target_v10_overlap"] and not row["source_v10_overlap"] and not row["target_canonical_overlap"] and not row["source_canonical_overlap"] for row in selected), "BLOCKED_HOLDOUT_PREDECESSOR_OVERLAP")
    payload = {"status": "PRE_OUTCOME_FROZEN", "seed": SEED, "target_count": target, "selected_count": len(selected), "selection_uses_outcome": False, "one_operator_per_meter_day": True, "v10_overlap_count": sum(row["target_v10_overlap"] or row["source_v10_overlap"] for row in selected), "canonical_overlap_count": sum(row["target_canonical_overlap"] or row["source_canonical_overlap"] for row in selected), "source_target_overlap_false_count": sum(row["overlap_false"] for row in selected), "identity_noop_overlap_count": sum(row["identity_noop"] for row in selected), "future_leakage_count": 0, "pairs": selected, "holdout_sha256": canonical_json_sha(selected)}
    injection = {**payload, "schema_version": "lightguard.v15.injection-manifest.1", "pair_result_schema": RESULT_FIELDS, "source_native_real_signal_graft": True, "b4_identity_noop_exception": "B4 has source==target and no current mutation; all non-B4 pairs require overlap_false=true.", "manifest_sha256": canonical_json_sha(payload)}
    write_json(HOLDOUT_MANIFEST, payload)
    write_json(LEGACY_HOLDOUT_MANIFEST, payload)
    write_json(INJECTION_MANIFEST, injection)


if __name__ == "__main__":
    main()
