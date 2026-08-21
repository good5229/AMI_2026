#!/usr/bin/env python3
"""Origin-sequential, prefix-invariant shadow replay engine."""

from __future__ import annotations

import hashlib
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from v09_detector import decide
from v10_ami import canonical_json_sha, measured_phases
from v10_counterfactual import activation, baseline, feature_case


SEVERITY = {"normal": 0, "abstain": -1, "observe": 1, "data_check_required": 1, "inspect": 2}


def replay_meter(meter_rows: list[dict], config: dict, end_time: datetime | None = None) -> tuple[list[dict], list[dict]]:
    rows = [row for row in meter_rows if end_time is None or row["timestamp"] <= end_time]
    phases = measured_phases(rows)
    first_time = rows[0]["timestamp"]
    left = 0
    history_xor = 0
    origins, episodes = [], []
    active_group: list[dict] = []
    active_episode = None
    previous_state_hash = hashlib.sha256(f"INIT|{rows[0]['meter_id']}".encode()).hexdigest()
    for index, row in enumerate(rows):
        cutoff = row["timestamp"]
        window_start = cutoff - timedelta(days=30)
        while left < index and rows[left]["timestamp"] < window_start:
            history_xor ^= int(rows[left]["row_sha256"], 16)
            left += 1
        history = rows[left:index]
        history_count = len(history)
        usable = sum(all(item["currents"][phase] is not None for phase in phases) for item in history)
        max_gap = max(((right["timestamp"] - prior["timestamp"]).total_seconds() / 60 for prior, right in zip(history, history[1:])), default=0)
        state = "evaluable"
        if cutoff - first_time < timedelta(days=30): state = "not_evaluable_warmup"
        elif usable < 2736 or max_gap > 360: state = "not_evaluable_quality"
        action, score, reasons = "normal", 0.0, []
        base = None
        if state == "evaluable":
            try: base = baseline(history, phases)
            except ValueError: state = "not_evaluable_quality"
        if state == "evaluable" and base is not None:
            value = activation(row, base, phases)
            is_active = 9 <= cutoff.hour < 17 and value is not None and value >= .20
            if is_active:
                if not active_group or cutoff - active_group[-1]["timestamp"] <= timedelta(minutes=30): active_group.append(row)
                else: active_group = [row]; active_episode = None
                outcome = decide(feature_case(active_group, base, phases), "H1", config)
                action, score, reasons = outcome["action"], outcome["score"], outcome["reason_codes"]
                if SEVERITY[action] > 0:
                    if active_episode is None:
                        active_episode = {"candidate_id": canonical_json_sha([row["meter_id"], cutoff.isoformat(), row["row_sha256"]])[:16], "meter_id": row["meter_id"], "start": active_group[0]["timestamp"], "end": cutoff + timedelta(minutes=15), "action": action, "score": score, "source_origin_hashes": [row["row_sha256"]]}
                        episodes.append(active_episode)
                    else:
                        active_episode["end"] = cutoff + timedelta(minutes=15)
                        if SEVERITY[action] >= SEVERITY[active_episode["action"]]: active_episode["action"], active_episode["score"] = action, max(score, active_episode["score"])
                        active_episode["source_origin_hashes"].append(row["row_sha256"])
            else:
                active_group = []; active_episode = None
        else:
            active_group = []; active_episode = None
        max_history = history[-1]["timestamp"] if history else None
        state_before = canonical_json_sha({"previous_state": previous_state_hash, "history_xor": f"{history_xor:064x}", "history_count": history_count, "window_start": window_start.isoformat(), "cutoff": cutoff.isoformat(), "active_group": [item["row_sha256"] for item in active_group[:-1]]})
        state_after = canonical_json_sha({"state_before": state_before, "origin": row["row_sha256"], "state": state, "action": action, "score": round(score, 8), "active_group": [item["row_sha256"] for item in active_group]})
        origins.append({"origin_id": row["row_sha256"][:20], "meter_id": row["meter_id"], "logical_date": row["logical_date"].isoformat(), "availability_time": cutoff.isoformat(sep=" "), "source_row_sha256": row["row_sha256"], "measured_phases": ";".join(phases), "current_channel_state": "available" if all(row["currents"][phase] is not None for phase in phases) else "unavailable", "duplicate_disposition": "unique", "history_window_start": window_start.isoformat(sep=" "), "history_cutoff_exclusive": cutoff.isoformat(sep=" "), "history_row_count": history_count, "history_usable_count": usable, "history_membership_xor": f"{history_xor:064x}", "max_history_availability_time": max_history.isoformat(sep=" ") if max_history else "", "causal_proof": max_history is None or max_history < cutoff, "off_baseline_a": round(base["off"], 8) if base else "", "on_baseline_a": round(base["on"], 8) if base else "", "activation_separation_a": round(base["separation"], 8) if base else "", "state_before_sha256": state_before, "state_after_sha256": state_after, "state": state, "action": action, "score": round(score, 8), "reason_codes": ";".join(sorted(set(reasons + (["SOLAR_UNAVAILABLE", "LOAD_UNAVAILABLE", "POLICY_UNAVAILABLE"] if state == "evaluable" else []))))})
        previous_state_hash = state_after
        history_xor ^= int(row["row_sha256"], 16)
    for episode in episodes: episode["source_origins_sha256"] = canonical_json_sha(episode.pop("source_origin_hashes"))
    return origins, episodes


def aggregate_days(origins: list[dict]) -> list[dict]:
    grouped = defaultdict(list)
    for row in origins: grouped[(row["meter_id"], row["logical_date"])].append(row)
    output = []
    for (meter, day), values in sorted(grouped.items()):
        actions = Counter(row["action"] for row in values if row["state"] == "evaluable")
        states = Counter(row["state"] for row in values)
        evaluable = [row for row in values if row["state"] == "evaluable"]
        candidate_origins = [row for row in evaluable if SEVERITY[row["action"]] > 0]
        output.append({"meter_id": meter, "local_date": day, "state": "evaluable" if evaluable else max(states, key=states.get), "source_rows": len(values), "data_coverage": round(len(values) / 96, 8), "history_rows": int(evaluable[-1]["history_row_count"]) if evaluable else int(values[-1]["history_row_count"]), "history_usable_slots": int(evaluable[-1]["history_usable_count"]) if evaluable else int(values[-1]["history_usable_count"]), "history_start": evaluable[-1]["history_window_start"] if evaluable else values[-1]["history_window_start"], "history_cutoff_exclusive": evaluable[-1]["history_cutoff_exclusive"] if evaluable else values[-1]["history_cutoff_exclusive"], "max_history_time": evaluable[-1]["max_history_availability_time"] if evaluable else values[-1]["max_history_availability_time"], "causal_proof": all(row["causal_proof"] for row in values), "off_baseline_a": evaluable[-1]["off_baseline_a"] if evaluable else "", "on_baseline_a": evaluable[-1]["on_baseline_a"] if evaluable else "", "activation_separation_a": evaluable[-1]["activation_separation_a"] if evaluable else "", "candidate_count": len(candidate_origins), "inspect_count": actions["inspect"], "observe_count": actions["observe"], "normal_count": actions["normal"], "data_check_count": actions["data_check_required"], "missing_or_warmup_count": sum(row["state"] != "evaluable" for row in values), "field_truth_available": False, "context_join": "none_anonymized_ami", "daily_origin_sha256": canonical_json_sha([row["state_after_sha256"] for row in values])})
    return output
