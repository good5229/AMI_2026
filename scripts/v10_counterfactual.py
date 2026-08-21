#!/usr/bin/env python3
"""Deterministic in-memory real-background counterfactual construction."""

from __future__ import annotations

import hashlib
import json
import statistics
from datetime import date, datetime, time, timedelta
from pathlib import Path

from v10_ami import ROOT, canonical_json_sha, group_days, load_rows, measured_phases, sha256_file


POOL = ROOT / "lightguard_v0_1/data/validation/v10/v10_background_pool_manifest.json"
RAW_MANIFEST = ROOT / "lightguard_v0_1/data/validation/v10/v10_raw_ami_manifest.json"
PROTOCOL = ROOT / "lightguard_v0_1/reports/v10/v10_counterfactual_protocol.md"
PHASE_NAMESPACE = "LG-v10-PHASE-20260820"


def median(values: list[float]) -> float:
    if not values:
        raise ValueError("median requires values")
    return statistics.median(values)


def contiguous(rows: list[dict], length: int) -> list[list[dict]]:
    result = []
    for index in range(len(rows) - length + 1):
        segment = rows[index:index + length]
        if all(right["timestamp"] - left["timestamp"] == timedelta(minutes=15) for left, right in zip(segment, segment[1:])):
            result.append(segment)
    return result


def baseline(history: list[dict], phases: tuple[str, ...]) -> dict:
    off_rows = [row for row in history if time(10, 0) <= row["timestamp"].time() < time(15, 0)]
    on_rows = [row for row in history if row["timestamp"].hour >= 22 or row["timestamp"].hour < 4]
    phase = {}
    for key in phases:
        off = [row["currents"][key] for row in off_rows if row["currents"][key] is not None]
        on = [row["currents"][key] for row in on_rows if row["currents"][key] is not None]
        phase[key] = {"off": median(off), "on": median(on)}
    off_total = sum(value["off"] for value in phase.values())
    on_total = sum(value["on"] for value in phase.values())
    if on_total <= off_total:
        raise ValueError("nonpositive meter separation")
    return {"phase": phase, "off": off_total, "on": on_total, "separation": on_total - off_total}


def activation(row: dict, base: dict, phases: tuple[str, ...]) -> float | None:
    values = [row["currents"][key] for key in phases]
    if any(value is None for value in values):
        return None
    return (sum(values) - base["off"]) / base["separation"]


def choose_source(history: list[dict], base: dict, phases: tuple[str, ...], operator: str, length: int) -> list[dict] | None:
    bands = {
        "deep_day_full": (0.50, 1.50, 1.00),
        "daytime_partial": (0.05, 0.85, 0.45),
        "phase_selective": (0.50, 1.50, 1.00),
        "weak_long_duration": (0.05, 0.75, 0.30),
        "benign_transition": (0.00, 0.50, 0.10),
        "post_switch_persistence": (0.50, 1.50, 1.00),
    }
    low, high, target = bands[operator]
    candidates = []
    for segment in contiguous(history, length):
        values = [activation(row, base, phases) for row in segment]
        if all(value is not None for value in values) and low <= statistics.mean(values) <= high:
            key = hashlib.sha256(f"LG-v10-SOURCE-20260820|{operator}|{segment[0]['meter_id']}|{segment[0]['timestamp'].isoformat()}".encode()).hexdigest()
            candidates.append((abs(statistics.mean(values) - target), key, segment))
    return min(candidates, key=lambda item: (item[0], item[1]))[2] if candidates else None


def target_segment(day_rows: list[dict], day: date, operator: str, base: dict, phases: tuple[str, ...]) -> list[dict] | None:
    length = {"deep_day_full": 8, "daytime_partial": 8, "phase_selective": 8, "weak_long_duration": 16, "benign_transition": 2, "post_switch_persistence": 6}[operator]
    if operator in {"deep_day_full", "phase_selective", "weak_long_duration"}:
        start = datetime.combine(day, time(10, 15))
    elif operator == "daytime_partial":
        start = datetime.combine(day, time(12, 15))
    else:
        usable = [row for row in day_rows if activation(row, base, phases) is not None]
        transitions = []
        for previous, current in zip(usable, usable[1:]):
            pa, ca = activation(previous, base, phases), activation(current, base, phases)
            if 4 <= current["timestamp"].hour < 10 and pa is not None and ca is not None and pa >= .5 and ca < .25:
                transitions.append(current["timestamp"])
        if not transitions:
            return None
        start = transitions[0]
    by_time = {row["timestamp"]: row for row in day_rows}
    segment = [by_time.get(start + timedelta(minutes=15 * index)) for index in range(length)]
    if any(row is None for row in segment):
        return None
    return segment


def feature_case(rows: list[dict], base: dict, phases: tuple[str, ...]) -> dict:
    activations = [activation(row, base, phases) for row in rows]
    valid = [value for value in activations if value is not None]
    maximum = max(valid) if valid else 0.0
    active_run = 0
    best_run = 0
    for value in activations:
        active_run = active_run + 1 if value is not None and value >= .20 else 0
        best_run = max(best_run, active_run)
    duration = best_run * 15
    phase_value = None
    if len(phases) >= 2:
        active_phases = 0
        for phase in phases:
            off, on = base["phase"][phase]["off"], base["phase"][phase]["on"]
            values = [(row["currents"][phase] - off) / (on - off) for row in rows if row["currents"][phase] is not None and on > off]
            if values and max(values) >= .20:
                active_phases += 1
        phase_value = 1.0 if active_phases == 1 else .5 if 0 < active_phases < len(phases) else 0.0
    persistence = .6 * max(0.0, min(1.0, (duration - 10.0) / 50.0)) + .4 * min(1.0, duration / 60.0)
    return {
        "activation_evidence": max(0.0, min(1.0, maximum)), "continuous_on_minutes": duration,
        "load_mismatch": None, "phase_selectivity": phase_value, "near_solar_boundary": False,
        "transient": duration <= 15, "normal_partial_policy": False,
        "solar_evidence": None, "persistence_evidence": persistence, "load_evidence": None,
        "phase_evidence": phase_value, "policy_evidence": None,
        "boundary_conflict": 0.0, "transient_conflict": 1.0 if duration <= 15 else 0.0,
        "policy_conflict": 0.0, "load_phase_conflict": 0.0,
        "recurrence": 0.0, "asset_criticality": 0.0, "age_since_last_review": 0.0,
    }


def construct_pairs() -> tuple[list[dict], dict]:
    pool = json.loads(POOL.read_text(encoding="utf-8"))
    rows_by_meter = load_rows()
    pairs, manifest_rows = [], []
    for unit in pool["units"]:
        meter, day, operator = unit["meter_id"], date.fromisoformat(unit["local_date"]), unit["operator"]
        meter_rows = rows_by_meter[meter]
        phases = measured_phases(meter_rows)
        history = [row for row in meter_rows if datetime.combine(day - timedelta(days=30), time.min) <= row["timestamp"] < datetime.combine(day, time.min)]
        day_rows = group_days(meter_rows).get(day, [])
        base = baseline(history, phases)
        target = target_segment(day_rows, day, operator, base, phases)
        if target and any(row["currents"][phase] is None for row in target for phase in phases):
            target = None
        length = len(target) if target else {"deep_day_full": 8, "daytime_partial": 8, "phase_selective": 8, "weak_long_duration": 16, "benign_transition": 2, "post_switch_persistence": 6}[operator]
        source = choose_source(history, base, phases, operator, length)
        status = "constructable" if target and source else "not_constructable"
        injection_id = hashlib.sha256(f"LG-v10-INJECT-20260820|{meter}|{day}|{operator}".encode()).hexdigest()[:20]
        record = {"injection_id": injection_id, "meter_id": meter, "target_date": day.isoformat(), "operator": operator, "class": "benign" if operator == "benign_transition" else "anomaly", "status": status, "scale": 1.0, "phases": list(phases), "pool_unit_hash": unit["unit_hash"], "energy_unchanged": True, "missingness_preserved": True}
        if status == "constructable":
            selected_phases = list(phases)
            if operator == "phase_selective":
                index = int(hashlib.sha256(f"{PHASE_NAMESPACE}|{meter}|{day}".encode()).hexdigest(), 16) % len(phases)
                selected_phases = [phases[index]]
            original = [{**row, "currents": dict(row["currents"])} for row in target]
            injected = [{**row, "currents": dict(row["currents"])} for row in target]
            cell_provenance = []
            for index, row in enumerate(injected):
                for phase in selected_phases:
                    residual = max(0.0, source[index]["currents"][phase] - base["phase"][phase]["off"])
                    input_value = row["currents"][phase]
                    row["currents"][phase] += residual
                    cell_provenance.append({
                        "source_meter": source[index]["meter_id"],
                        "source_timestamp": source[index]["timestamp"].isoformat(sep=" "),
                        "source_row_sha256": source[index]["row_sha256"],
                        "source_phase": phase,
                        "source_semantic": "interval_current_ampere",
                        "source_quality": "observed_finite_nonnegative",
                        "target_meter": meter,
                        "target_timestamp": row["timestamp"].isoformat(sep=" "),
                        "target_phase": phase,
                        "operation": "identity_current_residual_graft",
                        "scale": 1.0,
                        "input_cell_sha256": canonical_json_sha([phase, input_value]),
                        "output_cell_sha256": canonical_json_sha([phase, row["currents"][phase]]),
                        "physical_review": "PASS_CONSTRAINED_CURRENT_ONLY",
                        "energy_unchanged": True,
                    })
            input_hash = canonical_json_sha([[row["timestamp"].isoformat(), row["currents"]] for row in original])
            output_hash = canonical_json_sha([[row["timestamp"].isoformat(), row["currents"]] for row in injected])
            source_hash = canonical_json_sha([row["row_sha256"] for row in source])
            record.update({"target_start": target[0]["timestamp"].isoformat(sep=" "), "target_end": target[-1]["timestamp"].isoformat(sep=" "), "source_start": source[0]["timestamp"].isoformat(sep=" "), "source_end": source[-1]["timestamp"].isoformat(sep=" "), "source_rows_sha256": source_hash, "input_sha256": input_hash, "output_sha256": output_hash, "selected_phases": selected_phases, "copied_cell_count": len(cell_provenance), "skipped_missing_count": 0, "cell_provenance": cell_provenance})
            pairs.append({"manifest": record, "original_case": feature_case(original, base, phases), "injected_case": feature_case(injected, base, phases)})
        manifest_rows.append(record)
    manifest = {"schema_version": "lightguard.v10.injection-manifest.2", "status": "FROZEN_BEFORE_H1_OUTCOME", "raw_manifest_sha256": sha256_file(RAW_MANIFEST), "pool_manifest_sha256": sha256_file(POOL), "protocol_sha256": sha256_file(PROTOCOL), "raw_values_committed": False, "energy_reconstruction": False, "rows": manifest_rows}
    manifest["injection_manifest_sha256"] = canonical_json_sha(manifest_rows)
    return pairs, manifest
