#!/usr/bin/env python3
"""Build the deterministic, pre-outcome v0.9 episode manifest.

This tool never reads outcome data, detector output, candidate configuration, or
``.env``. It reuses frozen v0.7 official KMA observations and joins only
verified KASI records from the v0.9 context cache.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V07_CONTEXT = ROOT / "lightguard_v0_1/data/validation/v07/regional_seasonal_context_2025.json"
V09_CONTEXT = ROOT / "lightguard_v0_1/data/validation/v09/v09_official_context_2025.json"
OUTPUT = ROOT / "lightguard_v0_1/data/validation/v09/v09_episode_manifest.json"
SPLIT_SEED = "20260901"
SOURCE_URLS = {
    "kma": "https://www.data.go.kr/data/15057210/openapi.do",
    "kasi": "https://www.data.go.kr/data/15012688/openapi.do",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def stable_order(seed: str, cell_id: str, dates: list[str], purpose: str) -> list[str]:
    return sorted(dates, key=lambda day: sha256_text(f"{seed}|{purpose}|{cell_id}|{day}"))


def global_split(selected_by_cell: dict[str, list[str]]) -> dict[str, str]:
    """Assign each calendar date to one split while retaining 2:2 per cell."""
    cells = sorted(selected_by_cell, key=lambda cell: (-sum(day in dates for other, dates in selected_by_cell.items() if other != cell for day in selected_by_cell[cell]), cell))
    assigned: dict[str, str] = {}

    def search(index: int) -> bool:
        if index == len(cells):
            return True
        cell = cells[index]
        dates = selected_by_cell[cell]
        choices = sorted(combinations(dates, 2), key=lambda pair: sha256_text(f"{SPLIT_SEED}|global-split|{cell}|{'|'.join(pair)}"))
        for calibration in choices:
            proposed = {day: ("calibration" if day in calibration else "confirmatory") for day in dates}
            if any(day in assigned and assigned[day] != split for day, split in proposed.items()):
                continue
            added = [day for day in proposed if day not in assigned]
            assigned.update(proposed)
            if search(index + 1):
                return True
            for day in added:
                assigned.pop(day)
        return False

    if not search(0):
        raise RuntimeError("cannot produce globally date-disjoint 2:2 episode split")
    return assigned


def checked_kasi_records() -> dict[tuple[str, str], dict]:
    if not V09_CONTEXT.exists():
        return {}
    payload = load(V09_CONTEXT)
    if payload.get("schema_version") != "lightguard.v09.official-context.v1":
        raise RuntimeError(f"unexpected v0.9 official context schema: {V09_CONTEXT}")
    records = {}
    for row in payload.get("episodes", []):
        values = row.get("kasi", {}).get("values") or {}
        if row.get("kasi", {}).get("status") in {"official", "official_kasi_web_calculator"} and all(
            values.get(key) for key in ("sunrise", "sunset", "civil_morning", "civil_evening")
        ):
            records[(str(row["cell_id"]), str(row["date"]))] = row
    return records


def kma_by_date(cell: dict) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for row in cell["kma_observations"]:
        grouped.setdefault(str(row["timestamp"])[:10], []).append(row)
    for day, rows in grouped.items():
        timestamps = [str(row["timestamp"]) for row in rows]
        if len(rows) != 24 or len(set(timestamps)) != 24:
            raise RuntimeError(f"{cell['cell_id']} {day} must contain 24 unique KMA hours")
        if {str(row.get('source')) for row in rows} != {"KMA_ASOS_HOURLY_OFFICIAL"}:
            raise RuntimeError(f"{cell['cell_id']} {day} has non-official KMA observations")
    return grouped


def main() -> None:
    v07 = load(V07_CONTEXT)
    fetched_kasi = checked_kasi_records()
    selected_by_cell = {}
    grouped_by_cell = {}
    for cell in sorted(v07["cells"], key=lambda item: str(item["cell_id"])):
        grouped = kma_by_date(cell)
        all_dates = sorted(grouped)
        anchor = str(cell["anchor_date"])
        if anchor not in grouped or len(all_dates) < 4:
            raise RuntimeError(f"{cell['cell_id']} cannot provide four official KMA dates")
        selected_by_cell[str(cell["cell_id"])] = [
            anchor,
            *stable_order(SPLIT_SEED, str(cell["cell_id"]), [day for day in all_dates if day != anchor], "episode-date")[:3],
        ]
        grouped_by_cell[str(cell["cell_id"])] = grouped
    split_by_date = global_split(selected_by_cell)
    episodes: list[dict] = []
    for cell in sorted(v07["cells"], key=lambda item: str(item["cell_id"])):
        grouped = grouped_by_cell[str(cell["cell_id"])]
        anchor = str(cell["anchor_date"])
        selected_dates = selected_by_cell[str(cell["cell_id"])]
        for day in sorted(selected_dates):
            kma_rows = sorted(grouped[day], key=lambda row: str(row["timestamp"]))
            fetched = fetched_kasi.get((str(cell["cell_id"]), day))
            if fetched:
                kasi = {
                    "status": fetched["kasi"]["status"],
                    "source_file": V09_CONTEXT.relative_to(ROOT).as_posix(),
                    "values": fetched["kasi"]["values"],
                    "response_sha256": fetched["kasi"]["response_sha256"],
                }
            elif day == anchor:
                kasi = {
                    "status": "official_normalized_v07_anchor",
                    "source_file": V07_CONTEXT.relative_to(ROOT).as_posix(),
                    "values": cell["solar"],
                    "response_sha256": None,
                    "note": "v0.7 stores normalized official KASI values, not a raw-response hash",
                }
            else:
                kasi = {
                    "status": "blocked_pending_official_fetch",
                    "source_file": None,
                    "values": None,
                    "response_sha256": None,
                    "acquisition_command": "KASI_SERVICE_KEY=... python3 scripts/fetch_v09_context_episodes.py --fetch",
                }
            ready = kasi["status"] in {"official", "official_kasi_web_calculator", "official_normalized_v07_anchor"}
            timestamps = [str(row["timestamp"]) for row in kma_rows]
            episodes.append(
                {
                    "episode_id": f"v09-{cell['region_id']}-{cell['season']}-{day}",
                    "cell_id": cell["cell_id"],
                    "region_id": cell["region_id"],
                    "region_name_ko": cell["region_name_ko"],
                    "season": cell["season"],
                    "date": day,
                    "split": split_by_date[day],
                    "episode_status": "ready_for_scenario_generation" if ready else "blocked_pending_official_kasi",
                    "v08_eligibility": "forbidden_regression_and_failure_analysis_only",
                    "kma": {
                        "status": "official_v07_cache",
                        "station_id": cell["station_id"],
                        "source_file": V07_CONTEXT.relative_to(ROOT).as_posix(),
                        "observation_count": len(kma_rows),
                        "timestamps_sha256": sha256_text("\n".join(timestamps)),
                    },
                    "kasi": kasi,
                }
            )
    if len(episodes) != 48:
        raise RuntimeError(f"expected 48 episodes, got {len(episodes)}")
    counts = Counter((row["cell_id"], row["split"]) for row in episodes)
    if set(counts.values()) != {2}:
        raise RuntimeError(f"each cell/split needs two episodes: {counts}")
    station_dates = [(row["kma"]["station_id"], row["date"]) for row in episodes]
    if len(station_dates) != len(set(station_dates)):
        raise RuntimeError("a KMA station/date observation set would overlap between episodes")
    calibration_dates = {row["date"] for row in episodes if row["split"] == "calibration"}
    confirmatory_dates = {row["date"] for row in episodes if row["split"] == "confirmatory"}
    if calibration_dates & confirmatory_dates:
        raise RuntimeError("calendar dates overlap between calibration and confirmatory")
    if any(not str(row["date"]).startswith("2025-") for row in episodes):
        raise RuntimeError("v0.9 episodes must use only 2025 dates")
    ready_count = sum(row["episode_status"] == "ready_for_scenario_generation" for row in episodes)
    payload = {
        "schema_version": "lightguard.v09.episode-manifest.v1",
        "purpose": "Pre-outcome, episode-separated calibration and confirmatory allocation",
        "split_seed": int(SPLIT_SEED),
        "source_context_year": 2025,
        "source_urls": SOURCE_URLS,
        "v08_policy": "v0.8 is frozen regression and failure-analysis evidence only; it cannot tune v0.9 candidates.",
        "scenario_generation_gate": {
            "status": "open" if ready_count == 48 else "blocked",
            "required_ready_episodes": 48,
            "ready_episodes": ready_count,
            "reason": "All 48 episodes require verified official KMA and KASI context before scenario generation.",
        },
        "invariants": {
            "region_count": 3,
            "season_count": 4,
            "episodes_per_region_season_cell": 4,
            "calibration_episodes_per_cell": 2,
            "confirmatory_episodes_per_cell": 2,
            "episode_date_overlap": 0,
            "calendar_date_overlap": 0,
            "kma_station_date_overlap": 0,
            "future_2026_dates": 0,
        },
        "episodes": episodes,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}: episodes=48 ready={ready_count} blocked={48 - ready_count}")


if __name__ == "__main__":
    main()
