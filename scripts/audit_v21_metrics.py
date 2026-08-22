#!/usr/bin/env python3
import csv
import json
from pathlib import Path

from v21_submission_lib import DATA, ROOT, sha


def main():
    registry = json.loads((DATA / "v21_metric_registry.json").read_text(encoding="utf-8"))
    for metric in registry:
        path = ROOT / metric["source_file"]
        assert path.is_file() and sha(path) == metric["source_hash"], metric["metric_id"]
        if metric["extraction_method"] == "csv_rows":
            with path.open(encoding="utf-8-sig", newline="") as f:
                actual = sum(1 for _ in csv.DictReader(f))
        else:
            actual = json.loads(path.read_text(encoding="utf-8"))
            for key in metric["json_path"]:
                actual = actual[key]
        expected = metric["value"]
        if isinstance(expected, float):
            assert abs(float(actual) - expected) < 1e-12, metric["metric_id"]
        else:
            assert actual == expected, (metric["metric_id"], actual, expected)
    print(f"v0.21 metric consistency: PASS ({len(registry)} metrics)")


if __name__ == "__main__":
    main()
