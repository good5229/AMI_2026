#!/usr/bin/env python3
"""Freeze v0.15 replay plus a pre-outcome B-L-12 coverage extension."""
from collections import Counter
from datetime import date, datetime, timedelta

from build_v15_remaining_pool import OPERATORS, segments
from v15_common import canonical_windows, group_days, load_rows, measured_phases
from v16_common import DATA, SEED, V10, V15, canonical_sha, load_json, require, write_json


def complete(segment, phases):
    return all(row["currents"][phase] is not None for row in segment for phase in phases)


def main() -> None:
    freeze = load_json(DATA / "v16_protocol_freeze.json")
    v15_holdout = load_json(V15 / "v15_background_holdout_manifest.json")
    selected = [{**row, "corpus_role": "POST_HOC_V15_REPLAY"} for row in v15_holdout["pairs"]]
    meter = "B-L-12"
    meter_rows = load_rows()[meter]
    phases = measured_phases(meter_rows)
    require(len(phases) == 3, "BLOCKED_B_L_12_PHASE_SCOPE")
    days = group_days(meter_rows)
    v10 = load_json(V10 / "v10_background_pool_manifest.json")
    blocked = {row["local_date"] for row in v10["units"] if row["meter_id"] == meter}
    for start, end in canonical_windows()[meter]:
        cursor = start.date()
        while cursor <= end.date():
            blocked.add(cursor.isoformat()); cursor += timedelta(days=1)
    candidates = []
    for day in sorted(days):
        if day < date(2026, 5, 1) or day.isoformat() in blocked:
            continue
        history = [row for row in meter_rows if datetime.combine(day - timedelta(days=30), datetime.min.time()) <= row["timestamp"] < datetime.combine(day, datetime.min.time()) and row["logical_date"].isoformat() not in blocked]
        for operator, spec in OPERATORS.items():
            targets = [segment for segment in segments(days[day], spec["length"]) if complete(segment, phases)]
            if not targets:
                continue
            target = min(targets, key=lambda segment: canonical_sha([SEED, day.isoformat(), operator, "target", [row["row_sha256"] for row in segment]]))
            if spec.get("identity_noop"):
                source = target
            else:
                sources = [segment for segment in segments(history, spec["length"]) if complete(segment, phases)]
                if not sources:
                    continue
                source = min(sources, key=lambda segment: canonical_sha([SEED, day.isoformat(), operator, "source", [row["row_sha256"] for row in segment]]))
            source_hash = canonical_sha([row["row_sha256"] for row in source])
            target_hash = canonical_sha([row["row_sha256"] for row in target])
            candidates.append({
                "meter_id": meter, "local_date": day.isoformat(), "operator": operator, "operator_class": spec["class"], "legacy_operator": spec["legacy"], "phase_gate": True,
                "identity_noop": bool(spec.get("identity_noop")), "source_start": source[0]["timestamp"].isoformat(sep=" "), "target_start": target[0]["timestamp"].isoformat(sep=" "),
                "source_rows_sha256": source_hash, "target_rows_sha256": target_hash, "overlap": bool(spec.get("identity_noop")), "overlap_false": not bool(spec.get("identity_noop")),
                "target_v10_overlap": False, "source_v10_overlap": False, "target_canonical_overlap": False, "source_canonical_overlap": False, "future_leakage_count": 0,
                "selection_key": canonical_sha([SEED, meter, day.isoformat(), operator, source_hash, target_hash]), "corpus_role": "PRE_OUTCOME_B_L_12_EXTENSION",
            })
    used_days = {(row["meter_id"], row["local_date"]) for row in selected}
    extension = []
    for operator in OPERATORS:
        options = [row for row in candidates if row["operator"] == operator and (meter, row["local_date"]) not in used_days]
        if not options:
            continue
        row = dict(min(options, key=lambda item: item["selection_key"]))
        row["pair_id"] = canonical_sha([SEED, row["meter_id"], row["local_date"], row["operator"], row["source_rows_sha256"], row["target_rows_sha256"]])[:24]
        extension.append(row); selected.append(row); used_days.add((meter, row["local_date"]))
    counts = Counter(row["operator"] for row in selected)
    require(len(v15_holdout["pairs"]) == 71, "BLOCKED_V15_REPLAY_CORPUS_DRIFT")
    require(len(extension) >= 5, "BLOCKED_B_L_12_EXTENSION_TOO_SMALL")
    require({row["meter_id"] for row in selected} == {"B-L-9", "B-L-12", "B-L-13", "B-L-14", "B-L-35"}, "BLOCKED_INCOMPLETE_METER_COVERAGE")
    require(len(used_days) == len(selected), "BLOCKED_DUPLICATE_METER_DAY")
    payload = {
        "schema_version": "lightguard.v16.replay-corpus.2", "status": "POST_HOC_REPLAY_WITH_PRE_OUTCOME_COVERAGE_EXTENSION", "protocol_freeze_sha256": freeze["freeze_sha256"], "seed": SEED,
        "source_v15_holdout_sha256": v15_holdout["holdout_sha256"], "selected_count": len(selected), "v15_reused_pair_count": 71, "b_l_12_extension_count": len(extension),
        "meter_count": 5, "operator_counts": dict(sorted(counts.items())), "one_operator_per_meter_day": True, "v10_overlap_count": 0, "canonical_overlap_count": 0,
        "selection_uses_outcome": False, "independent_validation": False, "reuse_reason": "v0.15 consumed all zero-missing eligible meter-days; B-L-12 sparse-gap extension was frozen before v0.16 outcomes",
        "pairs": sorted(selected, key=lambda row: row["pair_id"]),
    }
    payload["holdout_sha256"] = canonical_sha(payload["pairs"])
    write_json(DATA / "v16_service_holdout_manifest.json", payload)


if __name__ == "__main__":
    main()
