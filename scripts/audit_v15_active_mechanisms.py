#!/usr/bin/env python3
"""Audit all 455 source meter-days without running detector outcomes."""
from __future__ import annotations

from datetime import date, datetime, timedelta

from v10_counterfactual import baseline
from v15_common import DATA, LEGACY_REMAINING_POOL_AUDIT, PREDECESSOR_FREEZE, REMAINING_POOL_AUDIT, V10_POOL, POOL_DATES, TARGET_METERS, canonical_json_sha, canonical_windows, day_hash, group_days, load_json, load_rows, measured_phases, require, write_csv, write_json


def main() -> None:
    freeze = load_json(PREDECESSOR_FREEZE)
    v10_pool = load_json(V10_POOL)
    frozen_v10_days = {(row["meter_id"], row["local_date"]) for row in v10_pool["units"]}
    windows = canonical_windows()
    rows_by_meter = load_rows()
    fields = ["meter_id", "local_date", "day_sha256", "status", "row_count", "phase_count", "baseline_gate", "phase_gate", "history_quality", "v10_pool_excluded", "canonical_overlap", "overlap_false", "future_leakage", "exclusion_reason"]
    audit, eligible = [], []
    for meter in TARGET_METERS:
        days = group_days(rows_by_meter[meter])
        for offset in range(91):
            day = date(2026, 4, 1) + timedelta(days=offset)
            day_rows = days.get(day, [])
            start, end = datetime.combine(day, datetime.min.time()), datetime.combine(day, datetime.max.time())
            phases = measured_phases(day_rows)
            overlap = any(start <= right and left <= end for left, right in windows[meter])
            v10_pool_excluded = (meter, day.isoformat()) in frozen_v10_days
            history = [row for row in rows_by_meter[meter] if datetime.combine(day - timedelta(days=30), datetime.min.time()) <= row["timestamp"] < start]
            history_quality = len(history) >= 2736 and all(row["currents"][phase] is not None for row in history for phase in phases)
            baseline_gate = False
            if history_quality and phases:
                try:
                    baseline(history, phases); baseline_gate = True
                except ValueError:
                    pass
            phase_gate = len(phases) == 3 and all(row["currents"][phase] is not None for row in day_rows for phase in phases)
            reasons = []
            if not POOL_DATES[0] <= day <= POOL_DATES[1]: reasons.append("outside_v10_pool_dates")
            if v10_pool_excluded: reasons.append("v10_background_pool_member")
            if overlap: reasons.append("canonical_six_plus_minus_4h")
            if len(day_rows) < 90: reasons.append("insufficient_target_rows")
            if not history_quality: reasons.append("insufficient_or_low_quality_history")
            if not baseline_gate: reasons.append("baseline_gate_failed")
            status = "ELIGIBLE" if not reasons else "EXCLUDED"
            record = {"meter_id": meter, "local_date": day.isoformat(), "day_sha256": day_hash(meter, day, day_rows), "status": status, "row_count": len(day_rows), "phase_count": len(phases), "baseline_gate": baseline_gate, "phase_gate": phase_gate, "history_quality": history_quality, "v10_pool_excluded": v10_pool_excluded, "canonical_overlap": overlap, "overlap_false": not overlap and not v10_pool_excluded, "future_leakage": 0, "exclusion_reason": ";".join(reasons)}
            audit.append(record)
            if status == "ELIGIBLE": eligible.append(record)
    require(len(audit) == 455, "BLOCKED_AUDIT_NOT_455_METER_DAYS")
    write_csv(REMAINING_POOL_AUDIT, fields, audit)
    write_csv(LEGACY_REMAINING_POOL_AUDIT, fields, audit)
    write_json(DATA / "v15_active_mechanisms_audit.json", {"status": "PRE_OUTCOME_FROZEN", "predecessor_freeze_sha256": freeze["freeze_sha256"], "audited_meter_days": 455, "eligible_meter_days": len(eligible), "v10_pool_excluded_count": sum(row["v10_pool_excluded"] for row in audit), "canonical_overlap_count": sum(row["canonical_overlap"] for row in audit), "overlap_false_count": sum(row["overlap_false"] for row in audit), "future_leakage_count": 0, "audit_rows_sha256": canonical_json_sha(audit)})


if __name__ == "__main__":
    main()
