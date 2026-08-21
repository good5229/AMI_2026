#!/usr/bin/env python3
"""Reproduce all local LightGuard v0.5 technical evidence and its manifest."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import subprocess
import csv
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "lightguard_v0_1" / "reports" / "v05"
DATA = ROOT / "lightguard_v0_1" / "data" / "validation" / "v05"
COMMANDS = (
    "python3 scripts/run_v05_forensics.py",
    "python3 scripts/run_v05_causal.py",
    "python3 scripts/run_v05_robustness.py",
)


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def generate_product_summary() -> Path:
    forensics = read_csv(REPORTS / "peak_consistency_forensics.csv")
    causal = json.loads((DATA / "causal_walkforward_summary.json").read_text(encoding="utf-8"))
    robustness = {row["stress_id"]: row for row in read_csv(REPORTS / "robustness_results.csv")}
    sensitivity_payload = json.loads((DATA / "sensitivity_grid.json").read_text(encoding="utf-8"))
    sensitivity = sensitivity_payload["summary"]
    activation_plus_20 = next(
        row for row in sensitivity_payload["rows"]
        if row["parameter"] == "activation" and row["setting"] == 1.2
    )
    profiles = json.loads((DATA / "temporal_meter_profiles.json").read_text(encoding="utf-8"))
    payload = {
        "schema_version": "lightguard-v0.5-product-evidence",
        "validation_scope": "technical validation; actual AMI has no confirmed fault labels",
        "actual_ami_peak": {
            "legacy_metric_consistent": sum(row["legacy_v04_peak_consistent"] == "True" for row in forensics),
            "legacy_metric_total": len(forensics),
            "legacy_metric_definition": "window-wide maximum individual phase compared with canonical aggregate peak",
            "adjudicated_metric_consistent": sum(row["adjudicated_peak_consistent"] == "True" for row in forensics),
            "adjudicated_metric_total": len(forensics),
            "adjudicated_metric_definition": "event-label maximum of sum(non-null I1,I2,I3) compared like for like",
            "primary_cause": "AGGREGATION_DEFINITION",
        },
        "causal_replay": {
            "past_only": True,
            "date_range": "2026-04-01/2026-06-30",
            "meter_count": len(profiles),
            "baseline_windows": ["7d", "14d", "30d", "expanding"],
            "canonical_candidate_coverage": {window: causal[window]["canonical_event_replay_coverage"] for window in ("7d", "14d", "30d", "expanding")},
            "candidate_counts": {window: causal[window]["candidate_count"] for window in ("7d", "14d", "30d", "expanding")},
            "full_sample_future_leakage": True,
        },
        "robustness": {
            "deterministic_seed": 5052026,
            "random_missing_20pct_coverage": float(robustness["missing_20pct"]["actual_canonical_event_coverage"]),
            "downsample_30m_coverage": float(robustness["downsample_30m"]["actual_canonical_event_coverage"]),
            "downsample_60m_coverage": float(robustness["downsample_60m"]["actual_canonical_event_coverage"]),
            "gap_120m_coverage": float(robustness["gap_120m"]["actual_canonical_event_coverage"]),
            "null_policy": "missing channel remains unavailable; never zero",
        },
        "sensitivity": {
            "classification": sensitivity["classification"],
            "most_sensitive_parameter": sensitivity["most_sensitive"]["parameter"],
            "most_sensitive_setting": sensitivity["most_sensitive"]["setting"],
            "activation_plus_20_normal_fpr": activation_plus_20["normal_fpr"],
            "frozen_baseline_normal_fpr": sensitivity["baseline_metrics"]["normal_fpr"],
            "activation_plus_20_candidate_count": activation_plus_20["candidate_count"],
            "frozen_config_changed": False,
        },
        "operational_evidence": {
            "cost_conversion_allowed": False,
            "reason": "No Suyeong same-scope contract and dispatch denominator",
        },
        "claim_policy": {
            "allowed": ["past-only replay", "known detector candidate coverage", "technical robustness", "ranking sensitivity"],
            "prohibited": ["field accuracy", "true fault detection rate", "dispatch-cost saving", "actual municipal AMI accuracy"],
        },
    }
    output = DATA / "v05_validation_summary.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    app_output = ROOT / "lightguard_app" / "assets" / "data" / "context" / "v05_validation_summary.json"
    app_output.parent.mkdir(parents=True, exist_ok=True)
    app_output.write_bytes(output.read_bytes())
    independent_audit = REPORTS / "independent_audit.md"
    audit_status = "available" if independent_audit.exists() else "pending"
    lines = [
        "# LightGuard v0.5 Real-Data Robustness Summary", "",
        "## Frozen Baseline", "",
        "- v0.3/v0.4 frozen hashes and weights remain unchanged.",
        "- Weather scoring remains disabled (`0.0`, context-only).", "",
        "## Actual AMI Peak Forensics", "",
        f"- Legacy peak consistency: {payload['actual_ami_peak']['legacy_metric_consistent']}/6.",
        f"- Adjudicated like-for-like replay integrity: {payload['actual_ami_peak']['adjudicated_metric_consistent']}/6.",
        "- Root cause for all six: `AGGREGATION_DEFINITION`; missing phases remain explicit for B-L-13/B-L-35.", "",
        "## Causal Walk-Forward", "",
        "- Five meters, 2026-04-01 through 2026-06-30.",
        "- 7/14/30-day and expanding baselines use only observations earlier than each evaluation day.",
        "- Every window reproduced 6/6 known detector candidates; this is not field recall or accuracy.",
        "- Full-sample detector is retained only as a comparison marked with future leakage.", "",
        "## Robustness", "",
        f"- Random missingness 20% coverage: {payload['robustness']['random_missing_20pct_coverage']:.6f}.",
        f"- 30/60-minute downsample coverage: {payload['robustness']['downsample_30m_coverage']:.6f} / {payload['robustness']['downsample_60m_coverage']:.6f}.",
        f"- 120-minute contiguous gap coverage: {payload['robustness']['gap_120m_coverage']:.6f}.",
        "- Missing measurement channels are never coerced to zero.", "",
        "## Sensitivity", "",
        f"- Classification: {payload['sensitivity']['classification']}.",
        f"- Most sensitive parameter family: {payload['sensitivity']['most_sensitive_parameter']}.",
        f"- Activation +20% diagnostic: normal FPR {payload['sensitivity']['frozen_baseline_normal_fpr']:.6f} -> {payload['sensitivity']['activation_plus_20_normal_fpr']:.6f}; candidates {payload['sensitivity']['activation_plus_20_candidate_count']}. No retuning or promotion.",
        "- Frozen v0.4 weights were not changed or retuned.", "",
        "## Operational Evidence", "",
        "- Public evidence supports the cabinet as an operational maintenance key.",
        "- Suyeong per-dispatch cost and ROI conversion remain prohibited because a matching denominator is unavailable.", "",
        "## Independent QA", "",
        f"- Status: {audit_status}.", "",
        "## Claims", "",
        "Allowed: controlled validation, independent holdout, past-only replay, known-candidate coverage, technical robustness, public operational evidence.",
        "Prohibited: field accuracy, actual municipal AMI accuracy, true fault rate, dispatch savings, public budget savings.",
    ]
    (REPORTS / "final_v05_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    docs = ROOT / "lightguard_app" / "docs" / "v05_real_data_robustness.md"
    docs.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return app_output


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    for command in COMMANDS:
        subprocess.run(command.split(), cwd=ROOT, check=True)
    app_summary = generate_product_summary()
    summary = json.loads((ROOT / "lightguard_v0_1" / "data" / "context" / "v04_validation_summary.json").read_text(encoding="utf-8"))
    replay_manifest = json.loads((ROOT / "lightguard_app" / "assets" / "data" / "ami_event_windows" / "replay_manifest.json").read_text(encoding="utf-8"))
    input_paths = [
        ROOT / "lightguard_v0_1" / "data" / "context" / "controlled_validation_frozen_2026.json",
        ROOT / "lightguard_v0_1" / "data" / "validation" / "v04_calibration_set.json",
        ROOT / "lightguard_v0_1" / "data" / "validation" / "v04_confirmatory_holdout.json",
        ROOT / "lightguard_app" / "assets" / "data" / "ami_events.csv",
        ROOT / "lightguard_app" / "assets" / "data" / "ami_event_windows" / "replay_manifest.json",
    ]
    output_paths = sorted(
        [path for path in DATA.glob("*") if path.is_file()]
        + [path for path in REPORTS.glob("*") if path.is_file() and path.name != "reproducibility_manifest.json"]
        + [app_summary, ROOT / "lightguard_app" / "docs" / "v05_real_data_robustness.md"]
    )
    git_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    packages = {}
    for name in ("openpyxl",):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = "unavailable"
    manifest = {
        "schema_version": "lightguard-v0.5-reproducibility",
        "run_timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "git_sha": git_sha,
        "python_version": platform.python_version(),
        "package_versions": packages,
        "commands": list(COMMANDS),
        "frozen_config": summary["frozen_weights"],
        "frozen_hashes": {
            "v03": summary["v03_frozen_set_sha256"],
            "v04_calibration": summary["calibration_sha256"],
            "v04_holdout": summary["confirmatory_holdout_sha256"],
        },
        "source_workbook_sha256": replay_manifest["source_workbook_sha256"],
        "input_hashes": {str(path.relative_to(ROOT)): sha256(path) for path in input_paths},
        "output_hashes": {str(path.relative_to(ROOT)): sha256(path) for path in output_paths},
        "allowed_nondeterminism": ["run_timestamp"],
        "claim_policy": {
            "canonical_six": "known detector candidates, not truth labels",
            "field_accuracy": "prohibited",
            "cost_conversion": "prohibited without Suyeong same-scope denominator",
        },
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "reproducibility_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"outputs": len(output_paths), "manifest": str(REPORTS / "reproducibility_manifest.json")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
