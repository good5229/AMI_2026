#!/usr/bin/env python3
"""Shared helpers for auditable LightGuard v0.3 context ingestion."""

from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
CONTEXT_DIR = ROOT / "lightguard_v0_1" / "data" / "context"
REPORT_DIR = ROOT / "lightguard_v0_1" / "reports"
APP_CONTEXT_DIR = ROOT / "lightguard_app" / "assets" / "data" / "context"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_env() -> dict[str, str]:
    values = dict(os.environ)
    for candidate in (ROOT / ".env", ROOT / ".env.local"):
        if not candidate.exists():
            continue
        for raw in candidate.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    return values


def service_key(dedicated_name: str) -> str | None:
    env = load_env()
    value = (
        env.get(dedicated_name)
        or env.get("DATA_GO_KR_DECODING")
        or env.get("DATA_GO_KR_ENCODING")
    )
    return unquote(value) if value else None


def curl_get(endpoint: str, params: dict[str, object], retries: int = 1) -> bytes:
    args = ["curl", "-sS", "--fail-with-body", "--get", endpoint]
    for key, value in params.items():
        args.extend(("--data-urlencode", f"{key}={value}"))
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            completed = subprocess.run(
                args,
                check=True,
                capture_output=True,
                timeout=30,
            )
            return completed.stdout
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(1.0)
    raise RuntimeError(
        f"official API request failed after {retries + 1} bounded attempt(s)"
    ) from None


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def mirror_to_app(source: Path) -> None:
    APP_CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
    (APP_CONTEXT_DIR / source.name).write_bytes(source.read_bytes())


def suyeong_centroid() -> dict[str, object]:
    objects = json.loads(
        (ROOT / "lightguard_v0_1" / "data" / "suyeong_v02_objects.json").read_text(
            encoding="utf-8"
        )
    )
    points = []
    for cabinet in objects:
        spatial = cabinet.get("asset_info", {}).get("spatial", {})
        lat, lon = spatial.get("latitude"), spatial.get("longitude")
        if lat is not None and lon is not None:
            points.append((float(lat), float(lon)))
    if not points:
        raise RuntimeError("No Suyeong coordinates available for centroid calculation")
    return {
        "method": "arithmetic_mean_of_cabinet_coordinates",
        "asset_count": len(points),
        "latitude": sum(p[0] for p in points) / len(points),
        "longitude": sum(p[1] for p in points) / len(points),
    }


def as_number(value: object) -> float | None:
    if value in (None, "", "-", "null"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
