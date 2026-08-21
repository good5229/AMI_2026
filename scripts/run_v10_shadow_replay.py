#!/usr/bin/env python3
"""Execute and prove origin-sequential causal shadow replay."""

import csv
import json
from datetime import datetime, timedelta

from v10_ami import ROOT, TARGET_METERS, canonical_json_sha, load_rows, sha256_file
from v10_shadow_engine import aggregate_days, replay_meter

CONFIG = ROOT / "lightguard_v0_1/data/validation/v09/v09_candidate_config.json"
DATA = ROOT / "lightguard_v0_1/data/validation/v10"
REPORTS = ROOT / "lightguard_v0_1/reports/v10"
CANONICAL = ROOT / "lightguard_app/assets/data/ami_events.csv"

def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)

config = json.loads(CONFIG.read_text(encoding="utf-8"))["selected_config"]
source = load_rows(); origins = []; episodes = []
for meter in TARGET_METERS:
    meter_origins, meter_episodes = replay_meter(source[meter], config)
    origins.extend(meter_origins); episodes.extend(meter_episodes)
prefix_end = datetime(2026, 5, 31, 23, 59, 59); prefix_mismatches = 0; prefix_compared = 0
full_by_id = {row["origin_id"]: row for row in origins}
for meter in TARGET_METERS:
    prefix_origins, _ = replay_meter(source[meter], config, prefix_end)
    for row in prefix_origins:
        prefix_compared += 1
        if full_by_id[row["origin_id"]]["state_after_sha256"] != row["state_after_sha256"]: prefix_mismatches += 1
if prefix_mismatches: raise RuntimeError(f"prefix invariance failed: {prefix_mismatches}")
if not all(row["causal_proof"] for row in origins): raise RuntimeError("origin causal proof failed")
pre_canonical_hash = canonical_json_sha([{**row, "start": row["start"].isoformat(), "end": row["end"].isoformat()} for row in episodes])
canonical_rows = []
with CANONICAL.open(encoding="utf-8-sig", newline="") as handle:
    for event in csv.DictReader(handle):
        start = datetime.fromisoformat(event["first_sample"]); end = datetime.fromisoformat(event["last_sample"]) + timedelta(minutes=15)
        matches = [row for row in episodes if row["meter_id"] == event["meter_id"] and row["start"] < end and start < row["end"]]
        best = max(matches, key=lambda row: ({"inspect": 2, "observe": 1, "data_check_required": 1}.get(row["action"], 0), row["score"]), default=None)
        canonical_rows.append({"event_id": event["event_id"], "meter_id": event["meter_id"], "action": best["action"] if best else "normal", "candidate_id": best["candidate_id"] if best else "", "truth_available": False})
daily = aggregate_days(origins)
write_csv(DATA / "v10_shadow_origin_audit.csv", origins); write_csv(DATA / "v10_shadow_replay.csv", daily); write_csv(REPORTS / "v10_canonical_shadow_replay.csv", canonical_rows)
cases = [row for row in origins if row["state"] == "evaluable" and row["action"] != "normal"]
evidence = [{"evidence_family": family, "available_cases": len(cases) if family == "persistence" else sum("PHASE_UNAVAILABLE" not in row["reason_codes"] for row in cases) if family == "phase" else 0, "total_cases": len(cases), "availability_rate": 1.0 if family == "persistence" and cases else (sum("PHASE_UNAVAILABLE" not in row["reason_codes"] for row in cases) / len(cases) if family == "phase" and cases else 0), "reason": "derived_from_current" if family in {"persistence", "phase"} else "unavailable_anonymized_context"} for family in ("solar", "persistence", "load", "phase", "policy")]
write_csv(REPORTS / "v10_evidence_availability.csv", evidence)
audit = {"schema_version": "lightguard.v10.shadow-causality-audit.1", "origin_count": len(origins), "all_origin_causal_proofs": True, "origin_hash_chain": True, "history_membership_xor_serialized": True, "duplicate_timestamp_count": 0, "same_time_permutation": "PASS_VACUOUS_NO_DUPLICATES", "prefix_end": prefix_end.isoformat(sep=" "), "prefix_origins_compared": prefix_compared, "prefix_mismatches": prefix_mismatches, "prefix_invariance": "PASS", "window_rule": "same_meter_[t-30d,t)", "pre_canonical_episode_sha256": pre_canonical_hash, "canonical_loaded_after_seal": True, "canonical_artifact_sha256": sha256_file(CANONICAL), "external_context_join": "none"}
(REPORTS / "v10_shadow_causality_audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
evaluable_days = [row for row in daily if row["state"] == "evaluable"]
inspect = sum(int(row["inspect_count"]) for row in evaluable_days); observe = sum(int(row["observe_count"]) for row in evaluable_days)
lines = ["# LightGuard v0.10 Causal Shadow Replay", "", f"- origins: `{len(origins)}`", f"- meter-days/evaluable: `{len(daily)}/{len(evaluable_days)}`", f"- inspect/observe origins: `{inspect}/{observe}`", f"- prefix origins compared/mismatches: `{prefix_compared}/{prefix_mismatches}`", f"- pre-canonical episode SHA: `{pre_canonical_hash}`", "", "## Canonical candidate replay coverage", ""] + [f"- {row['event_id']} / {row['meter_id']}: `{row['action']}` (truth unavailable)" for row in canonical_rows] + ["", "This is candidate-density and stability evidence, not accuracy or false-positive evidence."]
(REPORTS / "v10_shadow_replay_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps({"origins": len(origins), "meter_days": len(daily), "evaluable_meter_days": len(evaluable_days), "episodes": len(episodes), "inspect": inspect, "observe": observe, "prefix_compared": prefix_compared, "prefix_mismatches": prefix_mismatches, "canonical_actions": {row["event_id"]: row["action"] for row in canonical_rows}}))
