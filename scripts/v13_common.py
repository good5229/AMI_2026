#!/usr/bin/env python3
"""Shared fail-closed helpers for the v0.13 external benchmark workflow.

This module deliberately has no network behaviour and never writes raw or
row-level external data.  All result artefacts are aggregate-only.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
V13_DATA = ROOT / "lightguard_v0_1" / "data" / "validation" / "v13"
V13_REPORTS = ROOT / "lightguard_v0_1" / "reports" / "v13"
RAW_ROOT = ROOT / "official_docs" / "external_benchmarks"
CLAIM_BOUNDARY = (
    "External electrical anomaly mechanism evaluation only; not LightGuard "
    "streetlight field accuracy, field recall, asset condition, or fault probability."
)
SEED = 20260821


class V13ContractError(RuntimeError):
    """Raised when a frozen v0.13 contract cannot be proven intact."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise V13ContractError(f"Required file is missing: {path}")
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise V13ContractError(f"Expected JSON object: {path}")
    return value


def atomic_write_json(path: Path, value: Any, *, immutable: bool = False) -> None:
    payload = canonical_json(value) + "\n"
    if immutable and path.exists():
        if path.read_text(encoding="utf-8") != payload:
            raise V13ContractError(f"Immutable seal already exists with different content: {path}")
        return
    _atomic_write_text(path, payload)


def atomic_write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: "" if value is None else value for key, value in row.items()})
        temp_name = handle.name
    os.replace(temp_name, path)


def _atomic_write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(payload)
        temp_name = handle.name
    os.replace(temp_name, path)


def protocol_paths() -> dict[str, Path]:
    return {
        "mapping": V13_DATA / "v13_feature_mapping.json",
        "config": V13_DATA / "v13_signal_core_config.json",
        "protocol": V13_REPORTS / "v13_feature_transfer_protocol.md",
        "raw_manifest": V13_DATA / "v13_raw_external_manifest.json",
        "feature_seal": V13_DATA / "v13_preconfirmatory_config_seal.json",
        "threshold_seal": V13_DATA / "v13_mad_threshold_seal.json",
    }


def require_preconfirmatory_seal() -> dict[str, Any]:
    paths = protocol_paths()
    seal = load_json(paths["feature_seal"])
    if seal.get("phase") != "PRE_CONFIRMATORY":
        raise V13ContractError("Feature/config seal is not PRE_CONFIRMATORY")
    expected = seal.get("input_sha256", {})
    for key in ("mapping", "config", "protocol", "raw_mad_npz"):
        if key not in expected:
            raise V13ContractError(f"Feature/config seal lacks {key} hash")
    actual = {
        "mapping": sha256_file(paths["mapping"]),
        "config": sha256_file(paths["config"]),
        "protocol": sha256_file(paths["protocol"]),
        "raw_mad_npz": sha256_file(RAW_ROOT / "MAD" / "MAD.npz"),
    }
    if actual != expected:
        raise V13ContractError("Feature/config seal hash mismatch; refuse execution")
    raw_manifest = load_json(paths["raw_manifest"])
    if raw_manifest.get("phase") != "PRE_CONFIRMATORY":
        raise V13ContractError("Raw manifest was not created in PRE_CONFIRMATORY phase")
    mad = raw_manifest.get("datasets", {}).get("MAD", {})
    if mad.get("mad_npz_sha256") != actual["raw_mad_npz"]:
        raise V13ContractError("Raw MAD hash differs from sealed raw manifest")
    return seal


def mad_paths() -> tuple[Path, Path]:
    return RAW_ROOT / "MAD" / "MAD.npz", RAW_ROOT / "MAD" / "README.md"


def load_mad_train() -> tuple[np.ndarray, np.ndarray]:
    npz_path, _ = mad_paths()
    if not npz_path.is_file():
        raise V13ContractError(f"MAD source is unavailable: {npz_path}")
    with np.load(npz_path, allow_pickle=False) as archive:
        required = {"x_train", "y_train"}
        if not required.issubset(archive.files):
            raise V13ContractError("MAD archive lacks x_train/y_train")
        x_train = np.asarray(archive["x_train"], dtype=np.float64)
        y_train = np.asarray(archive["y_train"], dtype=np.int64)
    validate_mad_arrays(x_train, y_train, "train")
    return x_train, y_train


def load_mad_test_once() -> tuple[np.ndarray, np.ndarray]:
    """The only helper permitted to access immutable MAD test labels."""
    npz_path, _ = mad_paths()
    with np.load(npz_path, allow_pickle=False) as archive:
        required = {"x_test", "y_test"}
        if not required.issubset(archive.files):
            raise V13ContractError("MAD archive lacks x_test/y_test")
        x_test = np.asarray(archive["x_test"], dtype=np.float64)
        y_test = np.asarray(archive["y_test"], dtype=np.int64)
    validate_mad_arrays(x_test, y_test, "test")
    return x_test, y_test


def validate_mad_arrays(x: np.ndarray, y: np.ndarray, partition: str) -> None:
    if x.ndim != 3 or x.shape[1:] != (14, 48):
        raise V13ContractError(f"MAD {partition} shape must be [sample,14,48], got {x.shape}")
    if y.shape != (x.shape[0],):
        raise V13ContractError(f"MAD {partition} labels do not match samples")
    if not np.isfinite(x).all():
        raise V13ContractError(f"MAD {partition} contains non-finite values; no imputation is allowed")
    if not np.isin(y, np.arange(7)).all():
        raise V13ContractError(f"MAD {partition} label schema must be opaque classes 0..6")


def mad_split_indices(sample_count: int) -> tuple[np.ndarray, np.ndarray, str]:
    """Hash the immutable author-train array index before any label access."""
    calibration = np.array(
        [index for index in range(sample_count) if int(hashlib.sha256(f"{index}:v13-calibration".encode("ascii")).hexdigest(), 16) % 5 == 0],
        dtype=np.int64,
    )
    fit = np.setdiff1d(np.arange(sample_count, dtype=np.int64), calibration, assume_unique=True)
    if calibration.size == 0 or fit.size == 0:
        raise V13ContractError("Deterministic author-train index split is empty")
    return fit, calibration, "sha256_author_train_sample_index_v13_calibration_mod_5"


def binary_labels(y: np.ndarray) -> np.ndarray:
    return (np.asarray(y, dtype=np.int64) != 0).astype(np.int64)


def robust_signal_components(
    x: np.ndarray, epsilon: float, *, phase_available: bool = False
) -> dict[str, np.ndarray]:
    """Compute only frozen LG signals; MAD always calls this with phase unavailable."""
    if epsilon <= 0 or not np.isfinite(epsilon):
        raise V13ContractError("Calibration robust-scale floor is invalid")
    medians = np.median(x, axis=2, keepdims=True)
    raw_mad = np.median(np.abs(x - medians), axis=2)
    eligible = raw_mad > 0
    scales = np.maximum(1.4826 * raw_mad, epsilon)[..., np.newaxis]
    residual = np.clip((x - medians) / scales, -8.0, 8.0)
    residual = np.where(eligible[..., np.newaxis], residual, np.nan)

    s1_channels = np.nanquantile(np.abs(residual), 0.95, axis=2)
    s1 = np.nanmedian(s1_channels, axis=1)

    persistent = np.full(s1_channels.shape, np.nan)
    for sample in range(x.shape[0]):
        for channel in range(x.shape[1]):
            valid = np.isfinite(residual[sample, channel])
            if valid.sum() < 12:
                continue
            active = np.abs(residual[sample, channel, valid]) >= 2.0
            longest = current = 0
            for value in active:
                current = current + 1 if value else 0
                longest = max(longest, current)
            persistent[sample, channel] = longest / int(valid.sum())
    s2 = np.nanmedian(persistent, axis=1)

    median_residual = np.nanmedian(residual, axis=1)
    s4 = np.full(x.shape[0], np.nan)
    for sample, series in enumerate(median_residual):
        if np.isfinite(series).sum() < 12:
            continue
        positive = negative = 0.0
        maximum = 0.0
        for value in series[np.isfinite(series)]:
            positive = max(0.0, positive + value - 0.5)
            negative = min(0.0, negative + value + 0.5)
            maximum = max(maximum, abs(positive), abs(negative))
        s4[sample] = maximum

    # Physical provenance has not passed for MAD normalized tensors.  Do not
    # compute or approximate phase-current asymmetry from channel positions.
    s3 = np.full(x.shape[0], np.nan) if not phase_available else np.full(x.shape[0], np.nan)
    return {"LG-S1": s1, "LG-S2": s2, "LG-S3": s3, "LG-S4": s4}


def empirical_midrank(values: np.ndarray, reference: np.ndarray) -> np.ndarray:
    reference = np.sort(reference[np.isfinite(reference)])
    output = np.full(values.shape, np.nan, dtype=np.float64)
    if reference.size == 0:
        return output
    finite = np.isfinite(values)
    lower = np.searchsorted(reference, values[finite], side="left")
    upper = np.searchsorted(reference, values[finite], side="right")
    output[finite] = (lower + upper) / (2.0 * reference.size)
    return output


def signal_scores(
    components: dict[str, np.ndarray], calibration_components: dict[str, np.ndarray]
) -> dict[str, np.ndarray]:
    s1, s2, s3, s4 = (components[key] for key in ("LG-S1", "LG-S2", "LG-S3", "LG-S4"))
    rank_s1 = empirical_midrank(s1, calibration_components["LG-S1"])
    rank_s2 = empirical_midrank(s2, calibration_components["LG-S2"])
    rank_s4 = empirical_midrank(s4, calibration_components["LG-S4"])
    s3_reference = calibration_components["LG-S3"]
    # MAD lacks proven common phase-current scale.  Avoid a rank transform of
    # an all-NaN component and preserve its explicit unavailable state.
    if np.isfinite(s3_reference).any():
        rank_s3 = empirical_midrank(s3, s3_reference)
        ranked_components = [rank_s1, rank_s2, rank_s3, rank_s4]
    else:
        rank_s3 = np.full(s3.shape, np.nan, dtype=np.float64)
        ranked_components = [rank_s1, rank_s2, rank_s4]
    available = np.stack(ranked_components, axis=1)
    count = np.isfinite(available).sum(axis=1)
    finite_sum = np.where(np.isfinite(available), available, 0.0).sum(axis=1)
    s5 = np.full(s1.shape, np.nan, dtype=np.float64)
    np.divide(finite_sum, count, out=s5, where=count >= 2)
    return {"SC1": s1, "SC2": np.where(np.isfinite(rank_s2) & np.isfinite(rank_s3), (rank_s2 + rank_s3) / 2.0, np.nan), "SC3": s5}


def fit_zscore_template(x_fit: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return np.mean(x_fit, axis=0), np.std(x_fit, axis=0, ddof=0)


def zscore_comparator(x: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    safe_std = np.where(std > 0, std, np.nan)
    z = np.abs((x - mean) / safe_std)
    return np.nanquantile(np.nanmax(z, axis=1), 0.95, axis=1)


def choose_threshold(score: np.ndarray, y_binary: np.ndarray, grid: list[float]) -> dict[str, float]:
    valid = np.isfinite(score)
    if valid.sum() == 0 or not has_two_binary_classes(y_binary[valid]):
        raise V13ContractError("Calibration score is ineligible or has one binary class")
    candidates: list[tuple[float, float]] = []
    for percentile in grid:
        threshold = float(np.quantile(score[valid], percentile))
        prediction = (score[valid] >= threshold).astype(np.int64)
        candidates.append((binary_metrics(y_binary[valid], prediction)["balanced_accuracy"], threshold))
    best_score = max(item[0] for item in candidates)
    best_threshold = max(threshold for score_value, threshold in candidates if score_value == best_score)
    return {"calibration_balanced_accuracy": best_score, "threshold": best_threshold}


def has_two_binary_classes(y: np.ndarray) -> bool:
    values = np.unique(np.asarray(y, dtype=np.int64))
    return values.shape == (2,) and np.array_equal(values, np.array([0, 1], dtype=np.int64))


def binary_confusion(y: np.ndarray, prediction: np.ndarray) -> dict[str, int]:
    y = np.asarray(y, dtype=np.int64)
    prediction = np.asarray(prediction, dtype=np.int64)
    if y.shape != prediction.shape or not has_two_binary_classes(y):
        raise V13ContractError("Binary metric requires aligned labels containing both 0 and 1")
    if not np.isin(prediction, (0, 1)).all():
        raise V13ContractError("Binary prediction must contain only 0 and 1")
    return {
        "true_negative": int(((y == 0) & (prediction == 0)).sum()),
        "false_positive": int(((y == 0) & (prediction == 1)).sum()),
        "true_positive": int(((y == 1) & (prediction == 1)).sum()),
        "false_negative": int(((y == 1) & (prediction == 0)).sum()),
    }


def binary_metrics(y: np.ndarray, prediction: np.ndarray) -> dict[str, float | int]:
    counts = binary_confusion(y, prediction)
    tn, fp = counts["true_negative"], counts["false_positive"]
    tp, fn = counts["true_positive"], counts["false_negative"]
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    specificity = tn / (tn + fp) if tn + fp else 0.0
    f1 = 2.0 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        **counts,
        "accuracy": (tp + tn) / (tp + tn + fp + fn),
        "balanced_accuracy": (recall + specificity) / 2.0,
        "precision": precision,
        "recall": recall,
        "specificity": specificity,
        "fpr": fp / (fp + tn) if fp + tn else 0.0,
        "f1": f1,
    }


def binary_average_precision(y: np.ndarray, score: np.ndarray) -> float:
    """Descending-score precision-recall step sum, grouping tied scores."""
    y = np.asarray(y, dtype=np.int64)
    score = np.asarray(score, dtype=np.float64)
    if y.shape != score.shape or not np.isfinite(score).all() or not has_two_binary_classes(y):
        raise V13ContractError("Average precision requires finite scores and both binary classes")
    order = np.argsort(-score, kind="mergesort")
    sorted_score, sorted_y = score[order], y[order]
    positives = int(sorted_y.sum())
    true_positive = false_positive = 0
    previous_recall = 0.0
    ap = 0.0
    index = 0
    while index < sorted_y.size:
        end = index + 1
        while end < sorted_y.size and sorted_score[end] == sorted_score[index]:
            end += 1
        group = sorted_y[index:end]
        true_positive += int(group.sum())
        false_positive += int(group.size - group.sum())
        recall = true_positive / positives
        precision = true_positive / (true_positive + false_positive)
        ap += (recall - previous_recall) * precision
        previous_recall = recall
        index = end
    return float(ap)


def binary_auroc(y: np.ndarray, score: np.ndarray) -> float:
    """Tie-aware Mann-Whitney AUROC using ascending-score midranks."""
    y = np.asarray(y, dtype=np.int64)
    score = np.asarray(score, dtype=np.float64)
    if y.shape != score.shape or not np.isfinite(score).all() or not has_two_binary_classes(y):
        raise V13ContractError("AUROC requires finite scores and both binary classes")
    order = np.argsort(score, kind="mergesort")
    sorted_score = score[order]
    ranks = np.empty(score.size, dtype=np.float64)
    index = 0
    while index < score.size:
        end = index + 1
        while end < score.size and sorted_score[end] == sorted_score[index]:
            end += 1
        ranks[order[index:end]] = (index + 1 + end) / 2.0
        index = end
    positive_count = int(y.sum())
    negative_count = int(y.size - positive_count)
    return float((ranks[y == 1].sum() - positive_count * (positive_count + 1) / 2.0) / (positive_count * negative_count))


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float | None, float | None]:
    if total <= 0:
        return None, None
    proportion = successes / total
    denominator = 1.0 + z * z / total
    centre = (proportion + z * z / (2.0 * total)) / denominator
    half = z * np.sqrt((proportion * (1.0 - proportion) + z * z / (4.0 * total)) / total) / denominator
    return float(centre - half), float(centre + half)
