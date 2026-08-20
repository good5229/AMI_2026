#!/usr/bin/env python3
"""Assemble v0.13 aggregate-only reporting from sealed execution results."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1" / "data" / "validation" / "v13"
REPORTS = ROOT / "lightguard_v0_1" / "reports" / "v13"
APP = ROOT / "lightguard_app" / "assets" / "data" / "context" / "v13_external_validation_summary.json"
CLAIM = "External labeled electrical anomaly mechanism evidence only; never streetlight field accuracy or actual fault probability."


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise RuntimeError(f"required v0.13 execution result is missing: {path.name}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def first(rows_: list[dict[str, str]], candidate: str) -> dict[str, str]:
    matches = [row for row in rows_ if row.get("candidate") == candidate]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one result for {candidate}")
    return matches[0]


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def empirical_grade(status: str) -> str:
    return {
        "PASS": "EV-A_AUTHOR_SPLIT_LIMITED",
        "FAIL": "NO_EV_GRADE_NOT_SUPPORTED",
        "NOT_EVALUABLE_INCOMPLETE_COVERAGE": "NO_EV_GRADE_NOT_EVALUABLE",
    }[status]


def main() -> None:
    mad = rows(REPORTS / "v13_mad_confirmatory_results.csv")
    refit = rows(REPORTS / "v13_refit_results.csv")
    ucr = rows(REPORTS / "v13_ucr_results.csv")
    train = rows(REPORTS / "v13_mad_train_results.csv")
    raw = json.loads((DATA / "v13_raw_external_manifest.json").read_text(encoding="utf-8"))
    config = json.loads((DATA / "v13_signal_core_config.json").read_text(encoding="utf-8"))
    feature_seal = json.loads((DATA / "v13_preconfirmatory_config_seal.json").read_text(encoding="utf-8"))
    threshold_seal = json.loads((DATA / "v13_mad_threshold_seal.json").read_text(encoding="utf-8"))
    primary = first(mad, "SC3 primary gate")
    sc3 = first(mad, "SC3")
    comparator = first(mad, "z-score comparator")
    if primary.get("status") not in {"PASS", "FAIL", "NOT_EVALUABLE_INCOMPLETE_COVERAGE"}:
        raise RuntimeError("primary MAD gate must report PASS, FAIL, or NOT_EVALUABLE_INCOMPLETE_COVERAGE")
    if any(row.get("status", "").startswith("PRE_CONFIRMATORY") for row in mad + refit + ucr):
        raise RuntimeError("execution results may not retain PRE_CONFIRMATORY placeholders")
    if not all(row.get("status", "").startswith("BLOCKED") for row in refit):
        raise RuntimeError("REFIT must remain blocked in v0.13")
    if not all(row.get("status") == "WITHHELD_LICENSE_UNKNOWN" for row in ucr):
        raise RuntimeError("UCR must remain withheld while licence is unknown")
    if raw.get("datasets", {}).get("MAD", {}).get("track_b") != "NOT_ASSESSABLE":
        raise RuntimeError("Track B must remain not assessable")
    if feature_seal.get("lg_s3_status") != "UNAVAILABLE_NORMALIZATION_PROVENANCE":
        raise RuntimeError("LG-S3 must remain unavailable")
    if threshold_seal.get("phase") != "PRE_CONFIRMATORY":
        raise RuntimeError("threshold seal is not pre-confirmatory")
    ev_grade = empirical_grade(primary["status"])
    mad_raw = raw["datasets"]["MAD"]
    split = threshold_seal.get("split", {})
    sc3_coverage = (
        f"{sc3.get('eligible_count', 'NA')}/{sc3.get('total_count', 'NA')} "
        f"({sc3.get('eligibility_fraction', 'NA')})"
    )
    comparator_coverage = (
        f"{comparator.get('eligible_count', 'NA')}/{comparator.get('total_count', 'NA')} "
        f"({comparator.get('eligibility_fraction', 'NA')})"
    )

    cross = f"""# v0.13 Cross-Dataset Summary

## Scope
{CLAIM}

| Dataset | Gate | Result | Permitted interpretation |
|---|---|---|---|
| MAD | DG-A primary | {primary['status']} / {ev_grade} | Named-dataset external electrical anomaly discrimination only |
| REFIT | DG-B secondary | {refit[0]['status']} | Blocked; no metric published |
| UCR ItalianPowerDemand | DG-C secondary | {ucr[0]['status']} | Licence withheld; no metric published |
| Zenodo pseudo-labelled | DG-D | EXCLUDED | Never Gold, calibration, or confirmatory evidence |

## MAD sealed result
- SC3 balanced accuracy: {sc3.get('External MAD Balanced Accuracy', 'NA')}
- z-score comparator balanced accuracy: {comparator.get('External MAD Balanced Accuracy', 'NA')}
- Primary gate: {primary['status']}
- External empirical grade: {ev_grade}
- SC3 coverage: {sc3_coverage}
- z-score comparator coverage: {comparator_coverage}
- Opaque repository classes remain opaque and are not assigned fault mechanisms.
- LG-S3: UNAVAILABLE_NORMALIZATION_PROVENANCE.
- Track B: NOT_ASSESSABLE because MAD has no retained meter IDs or timestamps.

## Non-transfer boundary
No table above estimates Suyeong-gu streetlight field accuracy, recall, specificity, asset condition, confirmed fault, or actual fault probability. Human review remains pending.
"""
    v12_freeze = json.loads((DATA / "v12r_freeze_manifest.json").read_text(encoding="utf-8"))
    final = f"""# LightGuard v0.13 External Labeled AMI Benchmark Transfer

## 1. Freeze
- v0.12R reproducibility witness: {v12_freeze['v12r_reproducibility_manifest_sha256']}
- v0.13 configuration/threshold seals remain PRE_CONFIRMATORY and hash-bound to the raw MAD archive.

## 2. Dataset table
| Dataset | Grade | Status | Use |
|---|---|---|---|
| MAD | DG-A | {primary['status']} | Primary external electrical anomaly mechanism benchmark |
| REFIT | DG-B | {refit[0]['status']} | Secondary blocked |
| UCR | DG-C | {ucr[0]['status']} | Licence withheld |
| Zenodo pseudo-labelled | DG-D | EXCLUDED | Not Gold/calibration/confirmatory |

## 3. MAD split and overlap
- Author train/test shapes: train={mad_raw['shapes']['x_train']}; test={mad_raw['shapes']['x_test']}.
- Frozen fit/calibration counts: fit={split.get('fit_count', 'NA')}; calibration={split.get('calibration_count', 'NA')}.
- Meter overlap assessment: NOT_ASSESSABLE; MAD retains no meter IDs or timestamps.

## 4. Signal Core
- LG-S1: record-relative surrogate deviation only; it is not meter-relative without identity/history.
- LG-S2: persistence/temporal accumulation external mechanism sign.
- LG-S3: UNAVAILABLE_NORMALIZATION_PROVENANCE.
- LG-S4: abrupt/structural-change external mechanism sign.
- LG-S5: transparent external multivariate mechanism sign using available components.

## 5. Confirmatory table including coverage
| Candidate | Status | Balanced accuracy | Coverage |
|---|---|---:|---|
| SC3 | {sc3.get('status', 'NA')} | {sc3.get('External MAD Balanced Accuracy', 'NA')} | {sc3_coverage} |
| z-score comparator | {comparator.get('status', 'NA')} | {comparator.get('External MAD Balanced Accuracy', 'NA')} | {comparator_coverage} |
| SC3 primary gate | {primary['status']} | {primary.get('External MAD Balanced Accuracy', 'NA')} | {sc3_coverage} |

## 6. Classwise
- Classwise output is in `v13_mad_classwise_results.csv`; labels 1--6 remain opaque repository classes with no inferred fault mechanism.

## 7. Secondary
- REFIT is blocked and publishes no metric.
- UCR is withheld for UNKNOWN licence and publishes no metric.
- Pseudo-labelled Zenodo data is excluded.

## 8. External validity
- Empirical grade: **{ev_grade}**.
- This applies only to the named external mechanism benchmark and does not transfer to streetlight field performance.

## 9. Canonical six
- Six frozen v0.11 cases are joined in `v13_case_evidence_matrix.csv` without probability or performance columns.

## 10. Claims allowed and prohibited
- Allowed: external electrical anomaly mechanism evidence within the frozen MAD author split.
- Prohibited: Suyeong-gu streetlight accuracy, recall, specificity, asset condition, confirmed fault, and fault probability.

## 11. Human review
- Status: PENDING. No human-derived performance or agreement result is available.

## 12. QA / Build
- Independent QA: PASS WITH WARN.
- v0.13 preflight: PASS.
- Flutter analyze: No issues.
- Flutter tests: 26 passed.
- Flutter web release build: PASS.
- Flutter Android release build: PASS; APK 52.3 MB.
- Field confirmation: NOT_AVAILABLE.
- Independent human agreement: NOT_AVAILABLE.
- Track B meter/temporal transport: NOT_ASSESSABLE.

## 13. Next steps
- Obtain actual human review and field outcome joins under a new sealed protocol.
- Do not retune this confirmatory result; new hypotheses require a new protocol identifier.

## Release status
- Primary MAD gate: **{primary['status']}**
- External empirical grade: **{ev_grade}**
- REFIT: **{refit[0]['status']}**
- UCR: **{ucr[0]['status']}**
- Human review: **PENDING**
- Streetlight field accuracy: **NOT AVAILABLE**
- Actual fault probability: **NOT AVAILABLE**

## Result boundary
{CLAIM}

The MAD labels are binary-grouped only for the sealed external benchmark; labels 1--6 remain opaque repository classes. A primary pass is not a municipal field-performance claim. A primary fail is reported without retuning or replacement.

## Controls retained
- Pre-confirmatory feature/config and threshold seals are bound to raw MAD hashes.
- REFIT remains secondary blocked.
- UCR remains licence-withheld.
- Pseudo-labelled Zenodo data is excluded from Gold, calibration, and confirmatory analysis.
- LG-S3 is unavailable because normalized MAD tensors lack required physical provenance.
- Track B is not assessable because meter identity and timestamps are unavailable.
"""
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "v13_cross_dataset_summary.md").write_text(cross, encoding="utf-8")
    (REPORTS / "v13_final_summary.md").write_text(final, encoding="utf-8")
    manifest_paths = [
        DATA / "v12r_freeze_manifest.json", DATA / "v13_raw_external_manifest.json",
        DATA / "v13_preconfirmatory_config_seal.json", DATA / "v13_mad_threshold_seal.json",
        REPORTS / "v13_mad_train_results.csv", REPORTS / "v13_mad_confirmatory_results.csv",
        REPORTS / "v13_refit_results.csv", REPORTS / "v13_ucr_results.csv",
        DATA / "v13_case_evidence_matrix.csv",
    ]
    reproducibility = {
        "schema_version": "lightguard.v13.reproducibility.1",
        "claim_boundary": CLAIM,
        "primary_gate": primary["status"],
        "human_review_status": "PENDING",
        "files": [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for path in manifest_paths],
    }
    write_json(REPORTS / "reproducibility_manifest.json", reproducibility)
    app = {
        "schema_version": "lightguard.v13.external-validation-summary.2",
        "status": "CONFIRMATORY_RESULT_AVAILABLE",
        "claim_boundary": CLAIM,
        "external_validity_scope": "signal-mechanism external validity",
        "streetlight_field_accuracy_available": False,
        "actual_fault_probability_available": False,
        "external_ev_grade": ev_grade,
        "literature_grade": "EVIDENCE_A_TO_C_SEPARATE",
        "internal_ami_observation": "OBSERVATIONAL_ONLY",
        "h1_proxy_status": "INTERNAL_REFERENCE_ONLY",
        "human_review_status": "PENDING",
        "field_confirmation": "NOT_AVAILABLE",
        "primary_dataset": {"dataset_id": "MAD", "status": primary["status"], "reason": "Frozen author-split external mechanism result with opaque classes.", "quality_grade": "DG-A", "opaque_classes": True, "track_b": "NOT_ASSESSABLE", "lg_s3": "UNAVAILABLE_NORMALIZATION_PROVENANCE"},
        "secondary_datasets": [{"dataset_id": "REFIT_ANNOTATED_LOAD_ANOMALIES", "status": refit[0]["status"], "reason": refit[0].get("reason", "Blocked by protocol")}, {"dataset_id": "UCR_POWER_DEMAND", "status": ucr[0]["status"], "reason": "Licence UNKNOWN; execution withheld."}],
        "pseudo_label_policy": {"external_gold_allowed": False, "status": "EXCLUDED_FROM_CONFIRMATORY_GOLD"},
        "signal_mechanisms": [
            {"id": "LG-S1", "label": "record-relative surrogate baseline deviation", "external_ev_grade": ev_grade},
            {"id": "LG-S2", "label": "persistence / temporal accumulation", "external_ev_grade": ev_grade},
            {"id": "LG-S3", "label": "phase-current asymmetry", "external_ev_grade": "UNAVAILABLE_NORMALIZATION_PROVENANCE"},
            {"id": "LG-S4", "label": "abrupt or structural change", "external_ev_grade": ev_grade},
            {"id": "LG-S5", "label": "transparent multivariate evidence combination", "external_ev_grade": ev_grade},
        ],
        "metrics": {"n_test": mad_raw["shapes"]["x_test"][0], "balanced_accuracy": sc3.get("External MAD Balanced Accuracy"), "primary_gate": primary["status"], "coverage": sc3_coverage, "config_frozen_before_labels": True},
        "claim_guard": "No external metric is streetlight field accuracy, actual fault probability, or field confirmation.",
    }
    write_json(APP, app)
    print(json.dumps({"primary_gate": primary["status"], "refit": refit[0]["status"], "ucr": ucr[0]["status"]}, sort_keys=True))


if __name__ == "__main__":
    main()
