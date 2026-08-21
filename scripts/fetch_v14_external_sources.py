#!/usr/bin/env python3
"""Fetch only preregistered v0.14 resources; never fetch full CoDEx runs."""
from __future__ import annotations

import argparse
import json
import os
import ssl
import urllib.request
from pathlib import Path
from typing import Any

import certifi

from v14_common import CLAIM, DATA, RAW, frozen, manifest_entry, require, write_json

CAP = 16 * 1024 * 1024


def resources(config: dict[str, Any], env_name: str) -> list[dict[str, str]]:
    found: list[dict[str, str]] = []
    for key in ("selected_runs", "resources", "files", "frozen_resources"):
        value = config.get(key, [])
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and item.get("url"):
                    found.append({"id": str(item.get("run_id") or item.get("id") or item.get("name")), "url": item["url"]})
    if os.environ.get(env_name):
        found.extend(json.loads(os.environ[env_name]))
    return found


def fetch(url: str, target: Path, cap: int | None) -> None:
    headers = {"User-Agent": "LightGuard-v0.14-research"}
    if cap:
        headers["Range"] = f"bytes=0-{cap - 1}"
    request = urllib.request.Request(url, headers=headers)
    target.parent.mkdir(parents=True, exist_ok=True)
    context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(request, timeout=90, context=context) as response, target.open("wb") as handle:
        remaining = cap
        while True:
            chunk = response.read(min(1024 * 1024, remaining) if remaining else 1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
            if remaining is not None:
                remaining -= len(chunk)
                if remaining <= 0:
                    break
    require(target.stat().st_size <= cap if cap else True, "download exceeded frozen byte cap")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", action="store_true", help="perform sealed network fetches")
    args = parser.parse_args()
    codex = frozen(DATA / "v14_track_b_config.json")
    sust = frozen(DATA / "v14_track_c_config.json")
    codex_items = resources(codex, "LIGHTGUARD_V14_CODEX_RUNS_JSON")
    sust_items = resources(sust, "LIGHTGUARD_V14_SUSTDATA_FILES_JSON")
    if args.network:
        require(codex_items, "no pre-outcome CoDEx run URLs are sealed")
        require(len(sust_items) == 19, "SustData seal must contain one 1 Hz file and 18 label CSVs")
        for item in codex_items:
            fetch(item["url"], RAW / "codex_vfd" / f"{item['id']}.prefix.csv", CAP)
        for item in sust_items:
            require(Path(item["id"]).name == item["id"] and item["id"].endswith(".csv"), "sealed SustData id must be a safe CSV filename")
            fetch(item["url"], RAW / "sustdataed2" / item["id"], None)
    files = []
    codex_sources = {f"{item['id']}.prefix.csv": item["url"] for item in codex_items}
    sust_sources = {item["id"]: item["url"] for item in sust_items}
    for path in sorted(RAW.glob("codex_vfd/*.prefix.csv")):
        files.append(manifest_entry(path, partial=True, source=codex_sources.get(path.name, "")))
    for path in sorted(RAW.glob("sustdataed2/*")):
        if path.is_file():
            files.append(manifest_entry(path, source=sust_sources.get(path.name, "")))
    write_json(DATA / "v14_raw_external_manifest.json", {
        "schema_version": "lightguard.v14.raw-manifest.1", "phase": "PRE_OUTCOME_FROZEN",
        "claim_boundary": CLAIM, "codex_policy": "selected runs only; 16 MiB HTTP Range prefix; every run is partial",
        "sustdata_policy": "first 1 Hz period plus exactly 18 label CSV files; UTC alignment required",
        "network_performed": args.network, "files": files,
    })
    print(f"v0.14 raw manifest: {len(files)} local files")


if __name__ == "__main__":
    main()
