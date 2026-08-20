#!/usr/bin/env python3
"""Build v0.10 final narrative, Flutter summary, and reproducibility manifest."""

import csv
import hashlib
import json
import platform
import subprocess
from collections import Counter
from pathlib import Path

from v10_ami import ROOT, sha256_file

DATA = ROOT / "lightguard_v0_1/data/validation/v10"
REPORTS = ROOT / "lightguard_v0_1/reports/v10"
APP = ROOT / "lightguard_app/assets/data/context/v10_real_background_summary.json"

def load_json(name): return json.loads((DATA / name).read_text(encoding="utf-8"))
def csv_rows(path):
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle))
def git(*args): return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()

raw = load_json("v10_raw_ami_manifest.json"); pool = load_json("v10_background_pool_manifest.json"); injections = load_json("v10_injection_manifest.json")
transport = csv_rows(REPORTS / "v10_frozen_h1_transport.csv")[0]
shadow = csv_rows(DATA / "v10_shadow_replay.csv"); canonical = csv_rows(REPORTS / "v10_canonical_shadow_replay.csv")
constructable = sum(row["status"] == "constructable" for row in injections["rows"])
evaluable = [row for row in shadow if row["state"] == "evaluable"]
summary = {
    "schema_version": "lightguard.v10.real-background-summary.1",
    "source_mode": "anonymized_competition_ami",
    "meters": 5, "period": "2026-04-01/2026-06-30", "background_pool_units": pool["unit_count"],
    "constructable_pairs": constructable, "informative_anomaly_pairs": int(transport["informative_anomaly_pairs"]),
    "injection_recovery_rate": float(transport["injection_recovery_rate"]), "irr_wilson_95": json.loads(transport["irr_wilson_95"]),
    "worst_meter_irr": float(transport["worst_meter_irr"]), "worst_operator_irr": float(transport["worst_operator_irr"]),
    "benign_escalation_rate": float(transport["benign_escalation_rate"]), "median_score_uplift": float(transport["median_score_uplift"]),
    "transport_gate": transport["transport_gate"], "r1_triggered": transport["r1_triggered"].lower() == "true",
    "shadow_meter_days": len(shadow), "shadow_evaluable_meter_days": len(evaluable),
    "shadow_inspect_count": sum(int(row["inspect_count"]) for row in evaluable), "shadow_observe_count": sum(int(row["observe_count"]) for row in evaluable),
    "canonical_actions": {row["event_id"]: row["action"] for row in canonical},
    "actual_ami_is_truth": False, "unmodified_background_is_normal_truth": False, "field_fault_accuracy": False,
    "claim": "semi-synthetic real-background counterfactual transport validation",
    "disclaimer": "Not field fault accuracy. Anonymous AMI has no maintenance or fault truth.",
    "context_policy": "no municipal/KMA/KASI/rated-load join",
}
APP.parent.mkdir(parents=True, exist_ok=True); APP.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

source = raw["source"]
lines = ["# LightGuard v0.10 Real-Background Transport Final Summary", "", "## 1. Repository / Freeze", f"- branch: `{git('branch','--show-current')}`", f"- git SHA: `{git('rev-parse','HEAD')}`", "- v0.9 H1: frozen; no Track-A retuning", f"- H1 config SHA: `{transport['config_sha256']}`", "", "## 2. Actual AMI Source", f"- source: `{source['filename']}` (ignored/untracked)", f"- SHA-256: `{source['sha256']}`", f"- rows/meters: `{source['source_nonempty_row_count']}` / `{source['source_meter_count']}`", "- target: 5 meters, 2026-04-01 through 2026-06-30, 15-minute interval-end", "", "## 3. Background Pool", f"- eligible frozen units: `{pool['unit_count']}`; 40 per meter", f"- pool SHA: `{pool['pool_sha256']}`", "- source-only selection; canonical +/-4h buffers excluded; H1 output unused", "", "## 4. Counterfactual Injection", f"- constructable/pool: `{constructable}/{pool['unit_count']}`", "- current-only identity residual graft; energy unchanged; raw values uncommitted", "", "## 5. Frozen H1 Transport", f"- informative pairs: `{transport['informative_anomaly_pairs']}`", f"- IRR: `{transport['injection_recovery_rate']}`", f"- worst-meter/operator IRR: `{transport['worst_meter_irr']}` / `{transport['worst_operator_irr']}`", f"- benign escalation: `{transport['benign_escalation_rate']}`", f"- median score uplift: `{transport['median_score_uplift']}`", f"- gate: `{transport['transport_gate']}`; R1 triggered: `{transport['r1_triggered']}`", "", "## 6. Causal Shadow Replay", f"- meter-days/evaluable: `{len(shadow)}/{len(evaluable)}`", f"- inspect/observe: `{summary['shadow_inspect_count']}/{summary['shadow_observe_count']}`", "- canonical six are replay coverage only, never actual recall", "", "## 7. Evidence Availability", "- solar/load/policy: unavailable", "- persistence: current-derived", "- phase: native measured phases only", "", "## 8. Claims Allowed", "- Real-background counterfactual transport validation passed for frozen H1 on the defined semi-synthetic protocol.", "- Past-only shadow replay describes candidate density and meter drift.", "", "## 9. Claims Prohibited", "- Field accuracy, actual fault recall, real-background FPR/specificity, municipal performance, and production readiness.", "", "## 10. Remaining Gap", "- cabinet-linked municipal AMI, maintenance labels, cabinet-meter mapping, and prospective field shadow pilot."]
(REPORTS / "v10_final_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

paths = sorted(path for base in (DATA, REPORTS, ROOT / "docs/agent_learning_v10") if base.exists() for path in base.rglob("*") if path.is_file() and path.name != "reproducibility_manifest.json")
manifest = {"schema_version": "lightguard.v10.reproducibility.1", "git_branch": git("branch","--show-current"), "git_sha": git("rev-parse","HEAD"), "python_version": platform.python_version(), "random_seeds": {"pool_namespace": "LG-v10-POOL-20260820", "bootstrap": 20261020}, "commands": ["python3 scripts/audit_v10_raw_ami.py", "python3 scripts/build_v10_freeze.py", "python3 scripts/build_v10_background_pool.py", "python3 scripts/build_v10_counterfactual_pairs.py", "python3 scripts/run_v10_h1_transport.py", "python3 scripts/run_v10_shadow_replay.py", "python3 scripts/analyze_v10_meter_drift.py", "python3 scripts/run_v10_cluster_bootstrap.py", "python3 scripts/build_v10_final_report.py"], "raw_source_sha256": source["sha256"], "pool_sha256": pool["pool_sha256"], "injection_manifest_sha256": injections["injection_manifest_sha256"], "h1_config_sha256": transport["config_sha256"], "files": [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path)} for path in paths]}
(REPORTS / "reproducibility_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"transport_gate": summary["transport_gate"], "constructable_pairs": constructable, "manifest_files": len(paths)}))

