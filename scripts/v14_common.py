#!/usr/bin/env python3
"""Shared fail-closed utilities for the v0.14 physical replication."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v14"
REPORTS = ROOT / "lightguard_v0_1/reports/v14"
RAW = ROOT / "official_docs/external_benchmarks_v14"
V13_DATA = ROOT / "lightguard_v0_1/data/validation/v13"
V13_REPORTS = ROOT / "lightguard_v0_1/reports/v13"
CLAIM = ("External physical-mechanism replication only; not streetlight field "
         "accuracy, municipal performance, fault recall, false-positive rate, "
         "asset condition, or actual fault probability.")
FROZEN_PREFIX = "PRE_OUTCOME_FROZEN"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON object required: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.is_file(), f"missing CSV: {path}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def frozen(path: Path) -> dict[str, Any]:
    value = load_json(path)
    require(str(value.get("status", "")).startswith(FROZEN_PREFIX), f"config is not {FROZEN_PREFIX}: {path.name}")
    return value


def median(values: list[float]) -> float:
    require(bool(values), "median requires observations")
    data = sorted(values)
    n = len(data)
    return data[n // 2] if n % 2 else (data[n // 2 - 1] + data[n // 2]) / 2.0


def robust_scale(values: list[float]) -> tuple[float, float]:
    center = median(values)
    mad = median([abs(value - center) for value in values])
    return center, max(1.4826 * mad, 1e-12)


def balanced_accuracy(actual: list[int], predicted: list[int]) -> float | None:
    require(len(actual) == len(predicted), "metric arrays differ")
    rates = []
    for label in (0, 1):
        indices = [i for i, value in enumerate(actual) if value == label]
        if indices:
            rates.append(sum(predicted[i] == label for i in indices) / len(indices))
    return sum(rates) / len(rates) if len(rates) == 2 else None


def finite(value: str) -> float | None:
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def manifest_entry(path: Path, *, partial: bool = False, source: str = "") -> dict[str, Any]:
    return {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size,
            "sha256": sha256(path), "partial_run": partial, "source": source}


def result_fields() -> list[str]:
    return ["dataset_id", "unit_id", "status", "role", "partial_run", "actual_label",
            "pmc_prediction", "comparator_prediction", "pmc_score", "comparator_score",
            "independent_unit", "interpretation", "claim_boundary"]

