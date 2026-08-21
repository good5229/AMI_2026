#!/usr/bin/env python3
"""Train/calibrate frozen transparent MAD candidates without touching x_test/y_test."""
from __future__ import annotations

import hashlib

import numpy as np

from v13_common import (
    CLAIM_BOUNDARY, V13ContractError, atomic_write_csv, atomic_write_json, binary_labels,
    choose_threshold, fit_zscore_template, load_mad_train, mad_split_indices, protocol_paths,
    require_preconfirmatory_seal, robust_signal_components, signal_scores, zscore_comparator,
)


def main() -> None:
    feature_seal = require_preconfirmatory_seal()
    paths = protocol_paths()
    x_train, y_train = load_mad_train()  # Explicitly the only label-bearing source used here.
    fit_idx, calibration_idx, split_method = mad_split_indices(x_train.shape[0])
    x_fit, x_calibration = x_train[fit_idx], x_train[calibration_idx]
    y_calibration = binary_labels(y_train[calibration_idx])

    # These templates are fitted label-free on the fit partition.  They are
    # reconstructed at confirmation time rather than emitted as adapted rows.
    population_daily_profile = np.median(x_fit, axis=0)
    population_daily_mad = np.median(np.abs(x_fit - population_daily_profile), axis=0)
    positive_mads = np.median(np.abs(x_calibration - np.median(x_calibration, axis=2, keepdims=True)), axis=2)
    positive_mads = positive_mads[positive_mads > 0]
    if positive_mads.size == 0:
        raise V13ContractError("No positive calibration channel MAD; fail closed")
    epsilon = float(np.quantile(positive_mads, 0.05))
    calibration_components = robust_signal_components(x_calibration, epsilon, phase_available=False)
    calibration_scores = signal_scores(calibration_components, calibration_components)
    mean, std = fit_zscore_template(x_fit)
    calibration_scores["z-score comparator"] = zscore_comparator(x_calibration, mean, std)

    grid = feature_seal["threshold_grid"]
    candidate_rows = []
    selected: dict[str, dict[str, object]] = {}
    for candidate in ("SC1", "SC2", "SC3", "z-score comparator"):
        score = calibration_scores[candidate]
        if candidate == "SC2":
            candidate_rows.append({
                "dataset": "External MAD", "candidate": candidate, "status": "INELIGIBLE_LG_S3_UNAVAILABLE",
                "calibration_balanced_accuracy": None, "threshold": None, "selected_signal_core_candidate": False,
                "claim_boundary": CLAIM_BOUNDARY,
            })
            continue
        result = choose_threshold(score, y_calibration, grid)
        selected[candidate] = result
        candidate_rows.append({
            "dataset": "External MAD", "candidate": candidate, "status": "ELIGIBLE",
            "calibration_balanced_accuracy": result["calibration_balanced_accuracy"], "threshold": result["threshold"],
            "selected_signal_core_candidate": False, "claim_boundary": CLAIM_BOUNDARY,
        })
    signal_candidates = [name for name in ("SC1", "SC3") if name in selected]
    best_accuracy = max(float(selected[name]["calibration_balanced_accuracy"]) for name in signal_candidates)
    tie_order = ("SC3", "SC2", "SC1")
    selected_signal = next(name for name in tie_order if name in selected and float(selected[name]["calibration_balanced_accuracy"]) == best_accuracy)
    for row in candidate_rows:
        row["selected_signal_core_candidate"] = row["candidate"] == selected_signal

    threshold_seal = {
        "schema_version": "v13-mad-threshold-seal-1",
        "phase": "PRE_CONFIRMATORY",
        "feature_seal_sha256": __import__("hashlib").sha256(paths["feature_seal"].read_bytes()).hexdigest(),
        "raw_mad_npz_sha256": feature_seal["input_sha256"]["raw_mad_npz"],
        "split": {"method": split_method, "fit_count": int(fit_idx.size), "calibration_count": int(calibration_idx.size)},
        "epsilon": epsilon,
        "population_daily_profile_shape": list(population_daily_profile.shape),
        "population_daily_mad_shape": list(population_daily_mad.shape),
        "population_daily_profile_sha256": hashlib.sha256(population_daily_profile.tobytes()).hexdigest(),
        "population_daily_mad_sha256": hashlib.sha256(population_daily_mad.tobytes()).hexdigest(),
        "lg_s1_status": "WITHIN_RECORD_DEVIATION_ONLY_METER_RELATIVE_NOT_ASSESSABLE",
        "lg_s3_status": "UNAVAILABLE_NORMALIZATION_PROVENANCE",
        "candidates": selected,
        "selected_signal_core_candidate": selected_signal,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    atomic_write_json(paths["threshold_seal"], threshold_seal, immutable=True)
    atomic_write_csv(
        paths["threshold_seal"].parents[3] / "reports" / "v13" / "v13_mad_train_results.csv",
        ["dataset", "candidate", "status", "calibration_balanced_accuracy", "threshold", "selected_signal_core_candidate", "claim_boundary"],
        candidate_rows,
    )
    print("External MAD train/calibration complete; immutable test labels were not accessed.")


if __name__ == "__main__":
    main()
