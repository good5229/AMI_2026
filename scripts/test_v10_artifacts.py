#!/usr/bin/env python3
"""Fail-closed artifact contracts for LightGuard v0.10."""

import csv
import json
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path

from v10_ami import ROOT, sha256_file

DATA = ROOT / "lightguard_v0_1/data/validation/v10"; REPORTS = ROOT / "lightguard_v0_1/reports/v10"
load = lambda name: json.loads((DATA / name).read_text(encoding="utf-8"))
def rows(path):
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle))

freeze = load("v09_freeze_manifest.json")
assert freeze["candidate"]["name"] == "H1" and freeze["candidate"]["v10_track_a_retuning_permitted"] is False
for item in freeze["frozen_files"]: assert sha256_file(ROOT / item["path"]) == item["sha256"]
raw = load("v10_raw_ami_manifest.json")
assert raw["availability_gate"] == "PASS" and len(raw["meters"]) == 5 and raw["source"]["tracked_in_git"] is False
tracked = set(subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines())
assert not any(name.startswith("official_docs/") or name.startswith("harness_docs/") for name in tracked)
assert not any(name == ".env" or Path(name).suffix.lower() in {".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"} for name in tracked)
pool = load("v10_background_pool_manifest.json")
assert pool["unit_count"] == 200 and pool["detector_output_used"] is False
assert Counter(row["meter_id"] for row in pool["units"]) == Counter({meter: 40 for meter in ("B-L-9", "B-L-12", "B-L-13", "B-L-14", "B-L-35")})
assert all(row["operator"] != "phase_selective" or len(row["phases"]) == 3 for row in pool["units"])
injection = load("v10_injection_manifest.json")
assert len(injection["rows"]) == 200 and injection["raw_values_committed"] is False and injection["energy_reconstruction"] is False
assert all(row["energy_unchanged"] and row["missingness_preserved"] and row["scale"] == 1.0 for row in injection["rows"])
assert len({row["pool_unit_hash"] for row in injection["rows"]}) == 200
constructable = [row for row in injection["rows"] if row["status"] == "constructable"]
for row in constructable:
    cells = row["cell_provenance"]
    assert len(cells) == row["copied_cell_count"]
    assert all(cell["source_semantic"] == "interval_current_ampere" and cell["source_quality"] == "observed_finite_nonnegative" and cell["operation"] == "identity_current_residual_graft" and cell["scale"] == 1.0 and cell["physical_review"] == "PASS_CONSTRAINED_CURRENT_ONLY" and cell["energy_unchanged"] for cell in cells)
assert (REPORTS / "v10_b_l_12_reconciliation.md").exists()
transport = rows(REPORTS / "v10_frozen_h1_transport.csv")[0]
assert transport["candidate"] == "H1" and transport["transport_gate"] == "PASS" and transport["r1_triggered"].lower() == "false"
assert float(transport["injection_recovery_rate"]) >= .80 and float(transport["worst_meter_irr"]) >= .60
assert float(transport["benign_escalation_rate"]) <= .05 and float(transport["median_score_uplift"]) > 0
shadow = rows(DATA / "v10_shadow_replay.csv")
assert len(shadow) == 455
for row in shadow:
    if row["state"] == "evaluable":
        assert row["causal_proof"].lower() == "true"
        assert datetime.fromisoformat(row["max_history_time"]) < datetime.fromisoformat(row["history_cutoff_exclusive"])
origin = rows(DATA / "v10_shadow_origin_audit.csv")
assert len(origin) == 43582 and all(row["causal_proof"].lower() == "true" for row in origin)
assert all(row["state_before_sha256"] and row["state_after_sha256"] and row["history_membership_xor"] for row in origin)
causal = json.loads((REPORTS / "v10_shadow_causality_audit.json").read_text(encoding="utf-8"))
assert causal["origin_count"] == 43582 and causal["prefix_invariance"] == "PASS" and causal["prefix_mismatches"] == 0
assert causal["same_time_permutation"] == "PASS_VACUOUS_NO_DUPLICATES" and causal["canonical_loaded_after_seal"] is True
canonical = rows(REPORTS / "v10_canonical_shadow_replay.csv")
assert len(canonical) == 6 and all(row["truth_available"].lower() == "false" for row in canonical)
app = json.loads((ROOT / "lightguard_app/assets/data/context/v10_real_background_summary.json").read_text(encoding="utf-8"))
assert app["transport_gate"] == "PASS" and app["r1_triggered"] is False
assert app["actual_ami_is_truth"] is False and app["unmodified_background_is_normal_truth"] is False and app["field_fault_accuracy"] is False
assert not (DATA / "optional_v10_r1_config.json").exists() and not (REPORTS / "optional_v10_r1_results.csv").exists()
print("v0.10 artifact contracts: PASS")
