#!/usr/bin/env python3
"""UTC-align SustDataED2 transitions as positive controls, never faults."""
from __future__ import annotations

import csv
from bisect import bisect_left
from datetime import datetime, timezone
from pathlib import Path

from v14_common import CLAIM, DATA, RAW, REPORTS, finite, frozen, median, require, result_fields, robust_scale, write_csv


def utc(value: str) -> float:
    number = finite(value)
    if number is not None and number > 1e8:
        return number / 1000.0 if number > 1e11 else number
    parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).timestamp()


def table(path: Path) -> tuple[list[float], list[float]]:
    with path.open(encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle)
        require(reader.fieldnames is not None, "1 Hz CSV header missing")
        time_name = next((x for x in reader.fieldnames if any(k in x.lower() for k in ("time", "date"))), reader.fieldnames[0])
        value_name = next((x for x in reader.fieldnames if x.strip().upper() == "P"), None)
        require(value_name is not None, "1 Hz physical value column missing")
        pairs = []
        for row in reader:
            value = finite(row.get(value_name, ""))
            if value is not None:
                pairs.append((utc(row[time_name]), value))
    require(len(pairs) >= 32, "insufficient 1 Hz observations")
    pairs.sort()
    return [x[0] for x in pairs], [x[1] for x in pairs]


def label_times(path: Path) -> list[float]:
    with path.open(encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle)
        require(reader.fieldnames is not None, f"label header missing: {path.name}")
        name = next((x for x in reader.fieldnames if any(k in x.lower() for k in ("time", "date"))), reader.fieldnames[0])
        return [utc(row[name]) for row in reader if row.get(name)]


def main() -> None:
    frozen(DATA / "v14_track_c_config.json")
    base = RAW / "sustdataed2"
    csvs = sorted(base.glob("*.csv"))
    hz = [x for x in csvs if x.stem.isdigit() and len(x.stem) == 13]
    labels = [x for x in csvs if x not in hz]
    if len(hz) != 1 or len(labels) != 18:
        rows = [{"dataset_id": "SUSTDATAED2", "unit_id": "DATASET_GATE", "status": "BLOCKED_REQUIRED_FILES",
                 "role": "TRANSITION_POSITIVE_CONTROL_ONLY", "partial_run": False, "independent_unit": "day_appliance_cluster",
                 "interpretation": f"Required exactly one 1 Hz file and 18 label CSVs; found {len(hz)} and {len(labels)}. No metric computed.", "claim_boundary": CLAIM}]
    else:
        times, values = table(hz[0])
        center, scale = robust_scale(values[:max(16, len(values) // 5)])
        rows = []
        for path in labels:
            events = label_times(path)
            scores = []
            for event in events:
                position = bisect_left(times, event)
                candidates = [index for index in (position - 1, position) if 0 <= index < len(times)]
                nearest = min(candidates, key=lambda i: abs(times[i] - event))
                if 5 <= nearest < len(values) - 5:
                    scores.append(abs(median(values[nearest:nearest + 5]) - median(values[nearest - 5:nearest])) / scale)
            score = median(scores) if scores else 0.0
            rows.append({"dataset_id": "SUSTDATAED2", "unit_id": path.stem, "status": "EVALUATED_POSITIVE_CONTROL",
                         "role": "TRANSITION_POSITIVE_CONTROL_ONLY", "partial_run": False, "actual_label": 1,
                         "pmc_prediction": int(score >= 3.5), "comparator_prediction": "", "pmc_score": f"{score:.8g}",
                         "comparator_score": "", "independent_unit": "day_appliance_cluster",
                         "interpretation": "Human-corrected appliance transition; not an electrical fault.", "claim_boundary": CLAIM})
    write_csv(REPORTS / "v14_sustdata_results.csv", result_fields(), rows)
    print(f"SustData aggregate units: {len(rows)}")


if __name__ == "__main__":
    main()
