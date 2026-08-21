#!/usr/bin/env python3
"""Build deterministic v0.8 reports and the Flutter summary asset."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v08"
REPORTS = ROOT / "lightguard_v0_1/reports/v08"
SUMMARY_PATH = DATA / "v08_confirmatory_summary.json"
FACTOR_PATH = REPORTS / "v08_factor_effects.csv"
FEATURE_PATH = REPORTS / "v08_feature_availability_results.csv"
FINAL_PATH = REPORTS / "v08_final_summary.md"
APP_DOC = ROOT / "lightguard_app/docs/v08_detector_validation.md"
APP_ASSET = ROOT / "lightguard_app/assets/data/context/v08_detector_summary.json"
MANIFEST = REPORTS / "reproducibility_manifest.json"


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metric_table(results: dict) -> str:
    rows = ["| model | recall | FPR | AP | balanced accuracy | worst-cell recall | abstention | gate |", "|---|---:|---:|---:|---:|---:|---:|---|"]
    for model in ("frozen_v04", "C1", "C2", "C3"):
        value = results[model]
        gate = "baseline" if model == "frozen_v04" else "FAIL: FPR > 0.05"
        rows.append(f"| {model} | {value['recall']:.4f} | {value['fpr']:.4f} | {value['average_precision']:.4f} | {value['balanced_accuracy']:.4f} | {value['worst_cell_recall']:.4f} | {value['abstention_rate']:.4f} | {gate} |")
    return "\n".join(rows)


def main() -> None:
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    factors = load_csv(FACTOR_PATH)
    features = load_csv(FEATURE_PATH)
    results = summary["model_results"]
    factor_ranges = {}
    for model in ("frozen_v04", "C1", "C2", "C3"):
        for factor in ("region", "season", "region_x_season"):
            rows = [row for row in factors if row["model"] == model and row["factor"] == factor and row["recall"]]
            recalls = [float(row["recall"]) for row in rows]
            fprs = [float(row["fpr"]) for row in rows if row["fpr"]]
            factor_ranges[f"{model}:{factor}"] = {
                "recall_range": round(max(recalls) - min(recalls), 8),
                "fpr_range": round(max(fprs) - min(fprs), 8),
            }
    feature_changes = sum(row["decision_changed"] == "true" for row in features if row["state"] != "as_observed")
    feature_abstentions = sum(row["abstained"] == "true" for row in features)
    app_summary = {
        "schema_version": "lightguard.v08-app-summary.v1",
        "validation_kind": summary["validation_kind"],
        "confirmatory_cases": summary["case_count"],
        "holdout_sha256": summary["holdout_sha256"],
        "selected_candidate": None,
        "candidate_gate": "failed_fpr_limit",
        "baseline": results["frozen_v04"],
        "experimental_c1": results["C1"],
        "experimental_c2": results["C2"],
        "experimental_c3": results["C3"],
        "weather_policy": summary["weather_policy"],
        "feature_availability": {
            "paired_cases": len(features),
            "decision_changes": feature_changes,
            "abstentions": feature_abstentions,
            "imputation": "none",
        },
        "chungju": {
            "rated_load": "unavailable",
            "fixture_count_stratum": "unavailable_all_zero",
            "imputation": "none",
        },
        "actual_external_regional_ami": "unavailable",
        "claim_boundary": summary["claim_boundary"],
    }
    APP_ASSET.parent.mkdir(parents=True, exist_ok=True)
    APP_ASSET.write_text(json.dumps(app_summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    per_type = []
    for anomaly_type, baseline in results["frozen_v04"]["per_type_recall"].items():
        per_type.append(f"| {anomaly_type} | {baseline:.4f} | {results['C1']['per_type_recall'][anomaly_type]:.4f} |")
    report = f"""# LightGuard v0.8 Weak-Signal Detector Recovery Final Summary

## 1. v0.7 Freeze

- Preflight: PASS
- Frozen git SHA: `383c91e2c22d9364232c80683b6f8e4b6dc09d35`
- Baseline controlled recall/FPR: 0.50 / 0.00 on the separate v0.7 set
- Role: regression-only; not used for v0.8 tuning

## 2. v0.7 Failure Forensics

- Missed: `post_sunrise_persistence` (score 0.445, margin -0.105)
- Missed: `daytime_partial` (score 0.500, margin -0.050)
- Cause: insufficient activation-duration accumulation; region, season, weather,
  and asset values were not score inputs.

## 3. Experimental Design

- Calibration: 288 cases, SHA `b9825d7b8d336de9421a5941d2c7f069202b3f402fa4090b2837abb7d3a38b2f`
- Confirmatory: 432 cases, SHA `{summary['holdout_sha256']}`
- Design: 3 regions x 4 seasons, balanced blocked fractional allocation
- Calibration and confirmatory case IDs, seeds, factor tuples, signal parameter IDs,
  and asset pools are disjoint.

## 4. Candidate Detector

- C1: expected-operation residual plus activation-duration interaction, load mismatch,
  and phase selectivity
- C2: C1 plus missing-feature mask, availability handling, and abstention
- C3: C2 plus exploratory KMA weather modifier
- Threshold: fixed at 0.55; never lowered

## 5. Same-Holdout Confirmatory

{metric_table(results)}

No candidate passed the predeclared FPR <= 0.05 and hard-negative FPR <= 0.05
constraints. C1/C2 improved recall from {results['frozen_v04']['recall']:.4f} to
{results['C1']['recall']:.4f}, but FPR remained {results['C1']['fpr']:.4f}; therefore
`selected_candidate = null` and no v0.8 candidate is promoted.

## 6. Per-Anomaly Recall

| anomaly type | frozen v0.4 | C1 experimental |
|---|---:|---:|
{chr(10).join(per_type)}

## 7. Cross-Context

- C1 region recall range: {factor_ranges['C1:region']['recall_range']:.4f}
- C1 season recall range: {factor_ranges['C1:season']['recall_range']:.4f}
- C1 region x season recall range: {factor_ranges['C1:region_x_season']['recall_range']:.4f}
- Effects are controlled generated-factor effects, not actual municipal effects.

## 8. Statistical Uncertainty

- Wilson intervals below use the full 216 abnormal / 216 normal holdout samples;
  abstentions are not counted as correct detections.
- Wilson recall 95% CI, frozen v0.4: {results['frozen_v04']['recall_wilson_95']}
- Wilson recall 95% CI, C1: {results['C1']['recall_wilson_95']}
- Wilson FPR 95% CI, C1: {results['C1']['fpr_wilson_95']}
- C2 evaluable-only recall/FPR after excluding abstentions:
  {results['C2']['recall_evaluable']:.4f} / {results['C2']['fpr_evaluable']:.4f}
- Bootstrap: 1,000 fixed-seed cell/class-stratified resamples; see
  `v08_uncertainty_summary.md`.

## 9. Chungju Missing Load

- Official recovery status: per-cabinet load `NOT_RECOVERABLE` from current public data
- Imputation: none
- Asset stratum: unstratified because rated load is unavailable and fixture count is
  zero in every current source row
- Paired feature-removal cases: {len(features)}; decision changes: {feature_changes};
  abstentions: {feature_abstentions}

## 10. Weather Candidate

- C2 recall/FPR/AP: {results['C2']['recall']:.4f} / {results['C2']['fpr']:.4f} / {results['C2']['average_precision']:.4f}
- C3 recall/FPR/AP: {results['C3']['recall']:.4f} / {results['C3']['fpr']:.4f} / {results['C3']['average_precision']:.4f}
- Decision: weather remains `context_only`

## 11. External AMI Readiness

- Gangneung: `REQUEST_REQUIRED`
- Chungju: `REQUEST_REQUIRED`
- Public cabinet-linked interval AMI: not found
- Next step: authorized cabinet-to-meter mapping plus interval phase/current and
  maintenance labels

## 12. Flutter/Test/Build

- Independent QA: initial integrated command was blocked by restricted Flutter SDK
  cache permissions; the approved-permission rerun resolved it.
- Final independent QA: PASS with non-critical residual risks; all 11 gates met
- Final approved-permission v0.8 preflight: PASS
- Flutter analyze: no issues
- Flutter tests: 21 passed
- Web release build: PASS
- Android release APK: PASS, 52.2MB

## 13. Claims Allowed

- Controlled regional-seasonal experiment was expanded and independently held out.
- Weak-signal recall improved in an experimental candidate.
- The candidate failed the predeclared FPR gate and was not promoted.
- Missing-feature behavior and weather incremental value were explicitly tested.

## 14. Claims Prohibited

- Actual regional generalization or field accuracy
- Gangneung/Chungju AMI performance
- Actual fault detection rate or cost savings
- Production readiness of C1, C2, or C3

## 15. Remaining Risks

- Hard-negative false positives exceed the acceptance limit.
- Generated scenario dependence remains despite blocked/bootstrap analysis.
- Calibration and confirmatory splits share the same twelve official KMA/KASI
  context episodes. C3 was not selected and weather remains context-only; a future
  weather candidate requires date/episode-separated context.
- No external cabinet-linked field AMI exists for confirmation.

## 16. Next Recommended Step

Keep v0.4 as the product baseline, carry the failed v0.8 candidate evidence forward
without retuning this holdout, acquire actual cabinet-linked AMI, and design a new
v0.9 calibration set focused on pre-sunset and hard-negative discrimination.
"""
    FINAL_PATH.write_text(report, encoding="utf-8")
    APP_DOC.write_text(
        "# v0.8 Detector Validation\n\n"
        "The 432-case independent controlled holdout did not promote a new detector. "
        f"C1/C2 improved recall to {results['C1']['recall']:.4f}, but FPR "
        f"{results['C1']['fpr']:.4f} exceeded the 0.05 gate. The production-facing "
        "baseline therefore remains frozen v0.4, while C1/C2/C3 are displayed only "
        "as failed experimental candidates. Weather remains context-only. Chungju "
        "rated load is unavailable with no imputation, and actual Gangneung/Chungju "
        "AMI performance remains unvalidated.\n",
        encoding="utf-8",
    )
    targets = [
        DATA / "v07_freeze_manifest.json",
        ROOT / "lightguard_v0_1/data/validation/v08_design_matrix.csv",
        DATA / "v08_design_matrix.csv",
        DATA / "v08_calibration_set.json",
        DATA / "v08_candidate_freeze.json",
        DATA / "v08_confirmatory_holdout.json",
        DATA / "v08_confirmatory_summary.json",
        DATA / "v08_feature_availability_cases.json",
        REPORTS / "v07_failure_matrix.csv",
        REPORTS / "v08_calibration_results.csv",
        REPORTS / "v08_confirmatory_results.csv",
        REPORTS / "v08_factor_effects.csv",
        REPORTS / "v08_feature_availability_results.csv",
        REPORTS / "v08_uncertainty_summary.md",
        REPORTS / "v08_weather_candidate_decision.md",
        FINAL_PATH,
        APP_ASSET,
        APP_DOC,
        REPORTS / "v08_independent_audit.md",
        ROOT / "docs/agent_learning_v08/luna_independent_qa.md",
    ]
    manifest = {"schema_version": "lightguard.v08-manifest.v1", "files": {str(path.relative_to(ROOT)): sha256(path) for path in targets}}
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"selected_candidate": None, "candidate_gate": "failed_fpr_limit", "manifest_files": len(targets)}))


if __name__ == "__main__":
    main()
