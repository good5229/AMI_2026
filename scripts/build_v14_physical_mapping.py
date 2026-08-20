#!/usr/bin/env python3
"""Validate the preregistered physical mapping without outcome access."""
from __future__ import annotations

from v14_common import DATA, frozen, require


def main() -> None:
    mapping = frozen(DATA / "v14_physical_feature_mapping.json")
    require(set(mapping.get("core", {})) == {f"PMC-{i}" for i in range(1, 6)}, "PMC-1..PMC-5 required")
    rules = mapping.get("global_fail_closed_rules", {})
    require(rules.get("no_row_level_pseudoreplication") is True, "row-level inference prohibition missing")
    require(rules.get("no_raw_external_data_in_git") is True, "raw-data exclusion missing")
    require(rules.get("external_results_are_streetlight_accuracy") is False, "claim boundary weakened")
    for name in ("v14_track_a_config.json", "v14_track_b_config.json", "v14_track_c_config.json"):
        frozen(DATA / name)
    print("v0.14 physical mapping seal PASS")


if __name__ == "__main__":
    main()

