#!/usr/bin/env python3
"""Aggregate-only CoDEx-VFD replication on sealed 16 MiB run prefixes."""
from __future__ import annotations

import csv
from pathlib import Path

from v14_common import CLAIM, DATA, RAW, REPORTS, finite, frozen, median, require, result_fields, robust_scale, write_csv


def summarize(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8-sig", errors="replace", newline="") as handle:
        names = None
        for preamble_line in handle:
            candidate = next(csv.reader([preamble_line]))
            if len(candidate) >= 4 and candidate[0].strip().upper() == "TIME":
                names = [value.strip() for value in candidate]
                break
        require(names is not None, f"Tektronix TIME/channel header missing: {path.name}")
        reader = csv.DictReader(handle, fieldnames=names)
        label_name = next((x for x in names if any(k in x.lower() for k in ("label", "disturb", "inject"))), None)
        current_names = [name for name in names if name != label_name and any(key in name.lower() for key in ("phase", "current"))]
        require(len(current_names) == 2, f"exactly two documented current channels required: {path.name}")
        numeric: dict[str, list[float]] = {name: [] for name in current_names}
        labels: list[int] = []
        for index, row in enumerate(reader):
            if index >= 250000:
                break
            for name in numeric:
                value = finite(row.get(name, ""))
                if value is not None:
                    numeric[name].append(value)
            if label_name:
                value = finite(row.get(label_name, ""))
                if value is not None:
                    labels.append(int(value != 0))
    channels = sorted(numeric, key=lambda name: len(numeric[name]), reverse=True)[:2]
    require(len(channels) == 2 and min(len(numeric[x]) for x in channels) >= 32, f"two numeric current channels required: {path.name}")
    n = min(len(numeric[x]) for x in channels)
    contrasts = [abs(numeric[channels[0]][i] - numeric[channels[1]][i]) for i in range(n)]
    split = max(16, n // 4)
    center, scale = robust_scale(contrasts[:split])
    pmc_score = median([abs(value - center) / scale for value in contrasts[-split:]])
    first = numeric[channels[0]][:split]
    mean = sum(first) / len(first)
    sd = max((sum((x - mean) ** 2 for x in first) / len(first)) ** 0.5, 1e-12)
    comparator = abs(sum(numeric[channels[0]][-split:]) / split - mean) / sd
    actual = int(any(labels)) if labels else ""
    return {"dataset_id": "CODEX_VFD", "unit_id": path.stem, "status": "EVALUATED_PARTIAL_RUN_PREFIX",
            "role": "CONTROLLED_INJECTED_DISTURBANCE", "partial_run": True, "actual_label": actual,
            "pmc_prediction": int(pmc_score >= 3.5), "comparator_prediction": int(comparator >= 3.5),
            "pmc_score": f"{pmc_score:.8g}", "comparator_score": f"{comparator:.8g}",
            "independent_unit": "measurement_run", "interpretation": "Controlled current-disturbance mechanism on a partial prefix; not a field fault.",
            "claim_boundary": CLAIM}


def main() -> None:
    frozen(DATA / "v14_track_b_config.json")
    manifest = __import__("v14_common").load_json(DATA / "v14_raw_external_manifest.json")
    files = sorted(RAW.glob("codex_vfd/*.prefix.csv"))
    declared = {Path(x["path"]).resolve(): x for x in manifest.get("files", []) if x.get("partial_run")}
    rows = []
    for path in files:
        require(path.resolve() in declared, f"undeclared CoDEx prefix: {path.name}")
        require(path.stat().st_size <= 16 * 1024 * 1024, f"CoDEx prefix exceeds 16 MiB: {path.name}")
        rows.append(summarize(path))
    if not rows:
        rows = [{"dataset_id": "CODEX_VFD", "unit_id": "DATASET_GATE", "status": "BLOCKED_NO_SEALED_PREFIXES",
                 "role": "CONTROLLED_INJECTED_DISTURBANCE", "partial_run": True, "independent_unit": "measurement_run",
                 "interpretation": "No sealed 16 MiB run prefixes are locally available; no metric computed.", "claim_boundary": CLAIM}]
    write_csv(REPORTS / "v14_codex_vfd_results.csv", result_fields(), rows)
    print(f"CoDEx-VFD aggregate units: {len(rows)}")


if __name__ == "__main__":
    main()
