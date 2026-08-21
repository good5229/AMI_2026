#!/usr/bin/env python3
"""Separate municipal asset provenance from AMI signal provenance."""

from __future__ import annotations

import json
from pathlib import Path

from context_common import ROOT, write_json


SEEDS = {
    "suyeong": "suyeong_v02_seed.json",
    "gangneung": "gangneung_v02_seed.json",
    "chungju": "chungju_v02_seed.json",
}


def normalize_objects(objects: list[dict], scenario_ids: set[str]) -> None:
    for cabinet in objects:
        cabinet.setdefault("asset_info", {})["asset_source"] = "municipal_public_data"
        ami = cabinet.setdefault("ami", {})
        is_scenario = cabinet.get("cabinet_uid") in scenario_ids
        ami["signal_source"] = "scenario_injection" if is_scenario else "none"
        ami["virtual_link_mode"] = "scenario_injection" if is_scenario else "none"
        ami["has_real_ami"] = False
        ami["ami_meter_id"] = None
        weather = cabinet.setdefault("weather_context", {})
        if weather.get("forecast_hourly"):
            weather["source"] = "synthetic_weather"
            weather["context_policy"] = "validation_only"


def main() -> None:
    seed_dir = ROOT / "lightguard_v0_1" / "app_seed"
    app_dir = ROOT / "lightguard_app" / "assets" / "data"
    scenario_rows = json.loads(
        (ROOT / "lightguard_v0_1" / "data" / "simulation_scenarios_v02.json").read_text(
            encoding="utf-8"
        )
    )
    scenario_ids = {row["cabinet_uid"] for row in scenario_rows}

    for region, filename in SEEDS.items():
        if region != "suyeong":
            continue
        canonical = seed_dir / filename
        source = canonical if canonical.exists() else app_dir / filename
        seed = json.loads(source.read_text(encoding="utf-8"))
        normalize_objects(seed.get("objects", []), scenario_ids if region == "suyeong" else set())
        seed["schema_version"] = "lightguard-v0.3"
        seed["source_semantics"] = {
            "asset_source": "municipal_public_data",
            "signal_source": "scenario_injection_or_none" if region == "suyeong" else "none",
            "real_municipal_ami_mappings": 0,
        }
        if canonical.exists():
            write_json(canonical, seed)
        write_json(app_dir / filename, seed)

    objects_path = ROOT / "lightguard_v0_1" / "data" / "suyeong_v02_objects.json"
    objects = json.loads(objects_path.read_text(encoding="utf-8"))
    normalize_objects(objects, scenario_ids)
    write_json(objects_path, objects)
    write_json(app_dir / "suyeong_v02_objects.json", objects)

    scenario_count = sum(
        1 for row in objects if row.get("ami", {}).get("signal_source") == "scenario_injection"
    )
    none_count = sum(1 for row in objects if row.get("ami", {}).get("signal_source") == "none")
    if (len(objects), scenario_count, none_count) != (204, 46, 158):
        raise RuntimeError(
            f"Source semantics mismatch: total={len(objects)} scenario={scenario_count} none={none_count}"
        )
    print("source semantics: assets=204 scenario=46 none=158 real_municipal_ami=0")


if __name__ == "__main__":
    main()
