#!/usr/bin/env python3
"""Run a sealed one-pass External MAD confirmatory evaluation."""
from __future__ import annotations

import hashlib
import math

import numpy as np

from v13_common import (
    CLAIM_BOUNDARY, SEED, V13ContractError, atomic_write_csv, binary_average_precision,
    binary_labels, binary_metrics, binary_auroc, fit_zscore_template, load_json,
    load_mad_test_once, load_mad_train, mad_split_indices, protocol_paths,
    require_preconfirmatory_seal, robust_signal_components, signal_scores, wilson_interval,
    zscore_comparator,
)


def bootstrap_interval(y: np.ndarray, score: np.ndarray, prediction: np.ndarray, metric: str) -> tuple[float | None, float | None]:
    rng = np.random.default_rng(SEED)
    values: list[float] = []
    for _ in range(1000):
        indices = rng.integers(0, y.size, size=y.size)
        sampled_y = y[indices]
        if metric == "f1":
            if np.unique(sampled_y).size == 2:
                values.append(float(binary_metrics(sampled_y, prediction[indices])["f1"]))
        elif len(np.unique(sampled_y)) == 2:
            values.append(binary_average_precision(sampled_y, score[indices]))
    if not values:
        return None, None
    return float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))


def metrics_row(candidate: str, y: np.ndarray, score: np.ndarray, threshold: float) -> dict[str, object]:
    prediction = (score >= threshold).astype(np.int64)
    metric = binary_metrics(y, prediction)
    true_negative = int(metric["true_negative"])
    false_positive = int(metric["false_positive"])
    true_positive = int(metric["true_positive"])
    false_negative = int(metric["false_negative"])
    specificity = float(metric["specificity"])
    fpr = float(metric["fpr"])
    recall_low, recall_high = wilson_interval(true_positive, true_positive + false_negative)
    specificity_low, specificity_high = wilson_interval(true_negative, true_negative + false_positive)
    f1_low, f1_high = bootstrap_interval(y, score, prediction, "f1")
    ap_low, ap_high = bootstrap_interval(y, score, prediction, "ap")
    return {
        "dataset": "External MAD", "candidate": candidate, "status": "EVALUATED", "threshold": threshold,
        "External MAD Accuracy": float(metric["accuracy"]),
        "External MAD Balanced Accuracy": float(metric["balanced_accuracy"]),
        "External MAD Precision": float(metric["precision"]),
        "External MAD Recall": float(metric["recall"]),
        "External MAD F1": float(metric["f1"]),
        "External MAD Specificity": specificity, "External MAD FPR": fpr,
        "External MAD AP": binary_average_precision(y, score), "External MAD AUROC": binary_auroc(y, score),
        "External MAD Recall Wilson 95% Low": recall_low, "External MAD Recall Wilson 95% High": recall_high,
        "External MAD Specificity Wilson 95% Low": specificity_low, "External MAD Specificity Wilson 95% High": specificity_high,
        "External MAD F1 Bootstrap 95% Low": f1_low, "External MAD F1 Bootstrap 95% High": f1_high,
        "External MAD AP Bootstrap 95% Low": ap_low, "External MAD AP Bootstrap 95% High": ap_high,
        "true_negative": true_negative, "false_positive": false_positive, "true_positive": true_positive, "false_negative": false_negative,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def main() -> None:
    feature_seal = require_preconfirmatory_seal()
    paths = protocol_paths()
    threshold_seal = load_json(paths["threshold_seal"])
    if threshold_seal.get("phase") != "PRE_CONFIRMATORY":
        raise V13ContractError("Threshold seal is not PRE_CONFIRMATORY")
    if threshold_seal.get("feature_seal_sha256") != hashlib.sha256(paths["feature_seal"].read_bytes()).hexdigest():
        raise V13ContractError("Threshold seal does not bind the current feature/config seal")
    if threshold_seal.get("raw_mad_npz_sha256") != feature_seal["input_sha256"]["raw_mad_npz"]:
        raise V13ContractError("Threshold seal raw hash mismatch")

    # Rebuild all label-free fit/calibration state from sealed source/train order.
    x_train, _ = load_mad_train()
    fit_idx, calibration_idx, split_method = mad_split_indices(x_train.shape[0])
    if threshold_seal.get("split", {}).get("method") != split_method:
        raise V13ContractError("Train split method differs from threshold seal")
    x_fit, x_calibration = x_train[fit_idx], x_train[calibration_idx]
    population_daily_profile = np.median(x_fit, axis=0)
    population_daily_mad = np.median(np.abs(x_fit - population_daily_profile), axis=0)
    if hashlib.sha256(population_daily_profile.tobytes()).hexdigest() != threshold_seal.get("population_daily_profile_sha256"):
        raise V13ContractError("Sealed label-free population daily profile differs")
    if hashlib.sha256(population_daily_mad.tobytes()).hexdigest() != threshold_seal.get("population_daily_mad_sha256"):
        raise V13ContractError("Sealed label-free population daily MAD differs")
    positive_mads = np.median(np.abs(x_calibration - np.median(x_calibration, axis=2, keepdims=True)), axis=2)
    positive_mads = positive_mads[positive_mads > 0]
    epsilon = float(np.quantile(positive_mads, 0.05))
    if not math.isclose(epsilon, float(threshold_seal["epsilon"]), rel_tol=0.0, abs_tol=0.0):
        raise V13ContractError("Calibration scale floor differs from sealed value")
    calibration_components = robust_signal_components(x_calibration, epsilon, phase_available=False)
    mean, std = fit_zscore_template(x_fit)

    # This is the sole immutable test-array/test-label access in this script.
    x_test, y_test_opaque = load_mad_test_once()
    y_test = binary_labels(y_test_opaque)
    components = robust_signal_components(x_test, epsilon, phase_available=False)
    scores = signal_scores(components, calibration_components)
    scores["z-score comparator"] = zscore_comparator(x_test, mean, std)

    total_count = int(y_test.size)
    rows: list[dict[str, object]] = [{
        "dataset": "External MAD", "candidate": "implementation recovery audit",
        "status": "ATTEMPT_2_IMPLEMENTATION_ONLY_RECOVERY",
        "audit_note": (
            "Attempt 1 failed before any metric was computed because it required all candidate scores "
            "to be finite. Attempt 2 reports finite-score eligible coverage only; formulas, scores, "
            "thresholds, configuration, and seals are unchanged."
        ),
        "claim_boundary": CLAIM_BOUNDARY,
    }]
    for candidate in ("SC1", "SC2", "SC3", "z-score comparator"):
        if candidate == "SC2":
            rows.append({
                "dataset": "External MAD", "candidate": candidate, "status": "NOT_EVALUABLE_LG_S3_UNAVAILABLE",
                "threshold": None, "eligible_count": 0, "total_count": total_count, "eligibility_fraction": 0.0,
                "claim_boundary": CLAIM_BOUNDARY,
            })
            continue
        threshold = threshold_seal.get("candidates", {}).get(candidate, {}).get("threshold")
        if threshold is None:
            raise V13ContractError(f"Sealed threshold is missing: {candidate}")
        eligible = np.isfinite(scores[candidate])
        eligible_count = int(eligible.sum())
        coverage = eligible_count / total_count
        if eligible_count == 0:
            rows.append({
                "dataset": "External MAD", "candidate": candidate, "status": "NOT_EVALUABLE_NO_ELIGIBLE_ROWS",
                "threshold": float(threshold), "eligible_count": eligible_count, "total_count": total_count,
                "eligibility_fraction": coverage, "claim_boundary": CLAIM_BOUNDARY,
            })
            continue
        eligible_y = y_test[eligible]
        if np.unique(eligible_y).size != 2:
            rows.append({
                "dataset": "External MAD", "candidate": candidate, "status": "NOT_EVALUABLE_ONE_CLASS_ELIGIBLE",
                "threshold": float(threshold), "eligible_count": eligible_count, "total_count": total_count,
                "eligibility_fraction": coverage, "claim_boundary": CLAIM_BOUNDARY,
            })
            continue
        row = metrics_row(candidate, eligible_y, scores[candidate][eligible], float(threshold))
        row.update({
            "status": "EVALUATED" if coverage == 1.0 else "EVALUATED_PARTIAL",
            "eligible_count": eligible_count, "total_count": total_count, "eligibility_fraction": coverage,
        })
        rows.append(row)

    by_candidate = {row["candidate"]: row for row in rows if row["candidate"] in ("SC1", "SC3", "z-score comparator")}
    sc3 = by_candidate["SC3"]
    comparator = by_candidate["z-score comparator"]
    if float(sc3["eligibility_fraction"]) != 1.0:
        primary_status = "NOT_EVALUABLE_INCOMPLETE_COVERAGE"
    elif sc3["status"] not in ("EVALUATED",) or comparator["status"] not in ("EVALUATED", "EVALUATED_PARTIAL"):
        primary_status = "NOT_EVALUABLE_SEALED_CANDIDATE_UNAVAILABLE"
    else:
        primary_pass = (
            float(sc3["External MAD Balanced Accuracy"]) >= 0.70
            and float(sc3["External MAD Balanced Accuracy"]) - float(comparator["External MAD Balanced Accuracy"]) >= 0.05
        )
        primary_status = "PASS" if primary_pass else "FAIL"
    rows.append({
        "dataset": "External MAD", "candidate": "SC3 primary gate", "status": primary_status,
        "threshold": threshold_seal["candidates"]["SC3"]["threshold"],
        "External MAD Balanced Accuracy": sc3.get("External MAD Balanced Accuracy"),
        "eligible_count": sc3["eligible_count"], "total_count": total_count,
        "eligibility_fraction": sc3["eligibility_fraction"],
        "claim_boundary": CLAIM_BOUNDARY,
    })
    metric_fields = list(dict.fromkeys(key for row in rows for key in row))
    atomic_write_csv(paths["threshold_seal"].parents[3] / "reports" / "v13" / "v13_mad_confirmatory_results.csv", metric_fields, rows)

    classwise = []
    sc3_eligible = np.isfinite(scores["SC3"])
    prediction = (scores["SC3"] >= float(threshold_seal["candidates"]["SC3"]["threshold"])).astype(np.int64)
    for label in range(7):
        full_mask = y_test_opaque == label
        mask = full_mask & sc3_eligible
        target = 0 if label == 0 else 1
        eligible_count = int(mask.sum())
        classwise.append({
            "dataset": "External MAD", "candidate": "SC3", "opaque_label": f"{label}" if label == 0 else f"Abnormal-{label}",
            "sample_count": int(full_mask.sum()), "eligible_count": eligible_count,
            "eligibility_fraction": eligible_count / int(full_mask.sum()) if full_mask.any() else 0.0,
            "classwise_recall": float((prediction[mask] == target).mean()) if eligible_count else None,
            "interpretation": "Opaque repository label only; no class mechanism inferred.", "claim_boundary": CLAIM_BOUNDARY,
        })
    atomic_write_csv(
        paths["threshold_seal"].parents[3] / "reports" / "v13" / "v13_mad_classwise_results.csv",
        ["dataset", "candidate", "opaque_label", "sample_count", "eligible_count", "eligibility_fraction", "classwise_recall", "interpretation", "claim_boundary"], classwise,
    )
    print("External MAD confirmatory results written; no configuration or threshold was changed.")


if __name__ == "__main__":
    main()
