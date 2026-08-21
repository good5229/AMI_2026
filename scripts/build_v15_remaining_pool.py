#!/usr/bin/env python3
"""Build an outcome-independent target/source pool from audited real AMI days."""
from __future__ import annotations

import csv
from datetime import date, datetime, timedelta

from v10_counterfactual import activation, baseline
from v15_common import DATA, REMAINING_POOL_AUDIT, canonical_json_sha, deterministic_key, group_days, load_rows, require, write_json


OPERATORS = {
    "OP1": {"class": "anomaly", "legacy": "deep_day_full", "length": 8, "phase_only": False},
    "OP2": {"class": "anomaly", "legacy": "daytime_partial", "length": 8, "phase_only": False},
    "OP3": {"class": "anomaly", "legacy": "weak_long_duration", "length": 16, "phase_only": False},
    "OP4": {"class": "anomaly", "legacy": "post_switch_persistence", "length": 6, "phase_only": False},
    "OP5": {"class": "anomaly", "legacy": "phase_selective", "length": 8, "phase_only": True},
    "B1": {"class": "benign", "legacy": "short_benign_transient", "length": 2, "phase_only": False},
    "B2": {"class": "benign", "legacy": "low_amplitude", "length": 8, "phase_only": False},
    "B3": {"class": "benign", "legacy": "phase_preserving_fluctuation", "length": 8, "phase_only": False},
    "B4": {"class": "benign", "legacy": "identity_noop", "length": 8, "phase_only": False, "identity_noop": True},
}


def segments(rows, length):
    return [rows[index:index + length] for index in range(len(rows) - length + 1) if all(right["timestamp"] - left["timestamp"] == timedelta(minutes=15) for left, right in zip(rows[index:index + length], rows[index + 1:index + length]))]


def main() -> None:
    require((DATA / "v15_active_mechanisms_audit.json").is_file(), "BLOCKED_MISSING_455_AUDIT")
    audit = { (row["meter_id"], row["local_date"]): row for row in csv.DictReader(REMAINING_POOL_AUDIT.open(encoding="utf-8")) }
    rows_by_meter, pool = load_rows(), []
    for meter, meter_rows in rows_by_meter.items():
        by_day = group_days(meter_rows)
        phases = tuple(key for key in ("i1", "i2", "i3") if any(row["currents"][key] is not None for row in meter_rows))
        for day, target_rows in by_day.items():
            key = (meter, day.isoformat())
            if audit.get(key, {}).get("status") != "ELIGIBLE": continue
            history = [row for row in meter_rows if datetime.combine(day - timedelta(days=30), datetime.min.time()) <= row["timestamp"] < datetime.combine(day, datetime.min.time())]
            base = baseline(history, phases)
            for operator, spec in OPERATORS.items():
                if spec["phase_only"] and len(phases) != 3: continue
                target_candidates = [segment for segment in segments(target_rows, spec["length"]) if all(row["currents"][phase] is not None for row in segment for phase in phases)]
                source_candidates = [segment for segment in segments(history, spec["length"]) if audit.get((meter, segment[0]["logical_date"].isoformat()), {}).get("status") == "ELIGIBLE" and all(row["currents"][phase] is not None for row in segment for phase in phases)]
                if not target_candidates: continue
                target = min(target_candidates, key=lambda rows: deterministic_key(meter, day.isoformat(), operator, "target", canonical_json_sha([row["row_sha256"] for row in rows])))
                if spec.get("identity_noop"):
                    source = target
                elif source_candidates:
                    source = min(source_candidates, key=lambda rows: deterministic_key(meter, day.isoformat(), operator, "source", canonical_json_sha([row["row_sha256"] for row in rows])))
                else:
                    continue
                overlap = bool({row["timestamp"] for row in source} & {row["timestamp"] for row in target})
                if overlap and not spec.get("identity_noop"): continue
                source_hash = canonical_json_sha([row["row_sha256"] for row in source])
                target_hash = canonical_json_sha([row["row_sha256"] for row in target])
                target_audit = audit[(meter, day.isoformat())]
                source_audit = audit[(meter, source[0]["logical_date"].isoformat())]
                require(target_audit["status"] == "ELIGIBLE" and source_audit["status"] == "ELIGIBLE", "BLOCKED_AUDIT_EXCLUSION_BYPASS")
                pool.append({"meter_id": meter, "local_date": day.isoformat(), "operator": operator, "operator_class": spec["class"], "legacy_operator": spec["legacy"], "phase_gate": len(phases) == 3, "identity_noop": bool(spec.get("identity_noop")), "source_start": source[0]["timestamp"].isoformat(sep=" "), "target_start": target[0]["timestamp"].isoformat(sep=" "), "source_rows_sha256": source_hash, "target_rows_sha256": target_hash, "overlap": overlap, "overlap_false": not overlap, "target_v10_overlap": target_audit["v10_pool_excluded"] == "True", "source_v10_overlap": source_audit["v10_pool_excluded"] == "True", "target_canonical_overlap": target_audit["canonical_overlap"] == "True", "source_canonical_overlap": source_audit["canonical_overlap"] == "True", "future_leakage_count": 0, "selection_key": deterministic_key(meter, day.isoformat(), operator, source_hash, target_hash)})
    require(all((row["identity_noop"] or row["overlap_false"]) and row["future_leakage_count"] == 0 and not row["target_v10_overlap"] and not row["source_v10_overlap"] and not row["target_canonical_overlap"] and not row["source_canonical_overlap"] for row in pool), "BLOCKED_SOURCE_TARGET_LEAKAGE")
    write_json(DATA / "v15_remaining_pool.json", {"status": "PRE_OUTCOME_FROZEN", "source": "native_real_ami_only", "operators": OPERATORS, "candidate_count": len(pool), "bounded_selection": "at_most_one_pair_per_meter_day_operator", "selection_uses_outcome": False, "source_target_overlap_false_count": sum(row["overlap_false"] for row in pool), "identity_noop_overlap_count": sum(row["identity_noop"] for row in pool), "future_leakage_count": 0, "pool_sha256": canonical_json_sha(pool), "candidates": sorted(pool, key=lambda row: row["selection_key"])})


if __name__ == "__main__":
    main()
