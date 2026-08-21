#!/usr/bin/env python3
"""Fetch official 2025 KMA/KASI context for regional-seasonal validation.

The service key is read by the existing fetch modules from .env and is never
written to the output artifact.
"""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import fetch_kasi_context as kasi  # noqa: E402
import fetch_kma_weather_regimes as kma  # noqa: E402


OUTPUT = ROOT / "lightguard_v0_1/data/validation/v07/regional_seasonal_context_2025.json"
KASI_ENDPOINT = (
    "https://apis.data.go.kr/B090041/openapi/service/"
    "RiseSetInfoService/getAreaRiseSetInfo"
)
REGIONS = {
    "suyeong": {"name_ko": "수영구", "area": "부산", "station_id": "159"},
    "gangneung": {"name_ko": "강릉", "area": "강릉", "station_id": "105"},
    "chungju": {"name_ko": "충주", "area": "충주", "station_id": "127"},
}
SEASONS = {
    "winter": date(2025, 1, 15),
    "spring": date(2025, 4, 15),
    "summer": date(2025, 7, 15),
    "autumn": date(2025, 10, 15),
}


def _text(item: ET.Element, name: str) -> str:
    node = item.find(name)
    return (node.text or "").strip() if node is not None else ""


def fetch_solar(area: str, target: date) -> dict[str, str]:
    payload = kasi.curl_get(
        KASI_ENDPOINT,
        {
            "serviceKey": kasi.service_key("KASI_SERVICE_KEY"),
            "locdate": target.strftime("%Y%m%d"),
            "location": area,
        },
    )
    root = ET.fromstring(payload)
    item = root.find(".//item")
    if item is None:
        raise RuntimeError(f"KASI returned no item for {area} {target}")
    return {
        "sunrise": kasi.hhmm(_text(item, "sunrise")),
        "sunset": kasi.hhmm(_text(item, "sunset")),
        "civil_morning": kasi.hhmm(_text(item, "civilm")),
        "civil_evening": kasi.hhmm(_text(item, "civile")),
    }


def main() -> None:
    cells: list[dict[str, object]] = []
    key = kma.service_key("KMA_SERVICE_KEY")
    for region_id, region in REGIONS.items():
        for season, anchor in SEASONS.items():
            start = anchor - timedelta(days=3)
            end = anchor + timedelta(days=3)
            kma.STATION_ID = region["station_id"]
            observations = kma.fetch_chunk(key, start, end)
            if len(observations) != 168:
                raise RuntimeError(
                    f"Expected 168 KMA observations for {region_id}/{season}, "
                    f"received {len(observations)}"
                )
            cells.append(
                {
                    "cell_id": f"{region_id}_{season}",
                    "region_id": region_id,
                    "region_name_ko": region["name_ko"],
                    "season": season,
                    "anchor_date": anchor.isoformat(),
                    "station_id": region["station_id"],
                    "kma_window": {"start": start.isoformat(), "end": end.isoformat()},
                    "solar": fetch_solar(str(region["area"]), anchor),
                    "kma_observations": observations,
                }
            )

    artifact = {
        "schema_version": "lightguard.regional-seasonal-context.v1",
        "context_year": 2025,
        "regions": REGIONS,
        "seasons": {name: day.isoformat() for name, day in SEASONS.items()},
        "sources": {
            "weather": {
                "provider": "KMA",
                "dataset": "ASOS hourly observations",
                "url": "https://www.data.go.kr/data/15057210/openapi.do",
            },
            "solar": {
                "provider": "KASI",
                "dataset": "Area sunrise/sunset information",
                "url": "https://www.data.go.kr/data/15012688/openapi.do",
            },
        },
        "cells": cells,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUTPUT.relative_to(ROOT)}: {len(cells)} cells")


if __name__ == "__main__":
    main()
