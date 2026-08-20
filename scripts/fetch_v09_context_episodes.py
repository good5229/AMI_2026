#!/usr/bin/env python3
"""Acquire missing v0.9 episode solar context from the official KASI API.

The script deliberately reads only process environment variables, never .env.
It preserves the frozen v0.7 KMA ASOS cache and fetches only KASI rows needed
to turn a blocked episode into a complete official-context record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from context_common import curl_get


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "lightguard_v0_1/data/validation/v09/v09_episode_manifest.json"
OUTPUT = ROOT / "lightguard_v0_1/data/validation/v09/v09_official_context_2025.json"
KASI_ENDPOINT = "https://apis.data.go.kr/B090041/openapi/service/RiseSetInfoService/getAreaRiseSetInfo"
KASI_CALCULATOR = "https://astro.kasi.re.kr/life/pageView/9"
WEB_CALCULATOR = ROOT / "scripts/kasi_official_web_calculator.cjs"
REGION_COORDS = {
    "suyeong": {"latitude": 35.160659, "longitude": 129.115398},
    "gangneung": {"latitude": 37.772115, "longitude": 128.894640},
    "chungju": {"latitude": 36.992573, "longitude": 127.889855},
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def hhmm(value: str | None) -> str | None:
    if not value:
        return None
    digits = "".join(character for character in value if character.isdigit())
    if len(digits) < 4:
        return None
    digits = digits.zfill(4)[-4:]
    return f"{digits[:2]}:{digits[2:]}"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fetch_kasi(service_key: str, area: str, day: str) -> tuple[dict | None, str | None, dict | None]:
    try:
        raw = curl_get(
            KASI_ENDPOINT,
            {
                "serviceKey": service_key,
                "locdate": day.replace("-", ""),
                "location": area,
            },
            retries=1,
        )
        root = ET.fromstring(raw)
        item = root.find(".//item")
        if item is None:
            return None, None, {"code": root.findtext(".//resultCode") or "empty_response", "message": root.findtext(".//resultMsg") or "KASI returned no item"}
        values = {"sunrise": hhmm(item.findtext("sunrise")), "sunset": hhmm(item.findtext("sunset")), "civil_morning": hhmm(item.findtext("civilm")), "civil_evening": hhmm(item.findtext("civile"))}
        if not all(values.values()):
            return None, None, {"code": "incomplete_response", "message": "KASI response omitted a required solar/civil-twilight field"}
        return values, hashlib.sha256(raw).hexdigest(), None
    except Exception as exc:
        return None, None, {"code": "request_failed", "message": str(exc)}


def fetch_official_web(episodes: list[dict]) -> tuple[dict[str, dict], dict]:
    request = []
    for episode in episodes:
        coords = REGION_COORDS[episode["region_id"]]
        request.append({"episode_id": episode["episode_id"], "date": episode["date"], **coords})
    completed = subprocess.run(
        ["node", str(WEB_CALCULATOR)],
        input=json.dumps(request, separators=(",", ":")),
        text=True,
        capture_output=True,
        check=True,
        timeout=90,
    )
    payload = json.loads(completed.stdout)
    return {row["episode_id"]: row for row in payload["rows"]}, payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="perform official KASI requests; default reports readiness only")
    parser.add_argument("--official-web", action="store_true", help="use KASI's public official web-calculator JavaScript when the portal key is not registered")
    parser.add_argument("--kasi-service-key-env", default="KASI_SERVICE_KEY", help="process-environment variable containing the KASI service key")
    args = parser.parse_args()
    manifest = load(MANIFEST)
    if manifest.get("schema_version") != "lightguard.v09.episode-manifest.v1":
        raise RuntimeError(f"unexpected manifest schema: {MANIFEST}")
    pending = [row for row in manifest["episodes"] if row["kasi"]["status"] == "blocked_pending_official_fetch"]
    print(f"v0.9 KASI acquisition: pending={len(pending)} verified_anchor={len(manifest['episodes']) - len(pending)}")
    if not args.fetch:
        return 0
    key = os.environ.get(args.kasi_service_key_env)
    if not args.official_web and not key:
        print(f"missing process environment variable: {args.kasi_service_key_env}", file=sys.stderr)
        return 2
    area_by_region = {"suyeong": "부산", "gangneung": "강릉", "chungju": "충주"}
    rows = []
    failures = []
    web_rows = {}
    web_provenance = None
    if args.official_web:
        try:
            web_rows, web_provenance = fetch_official_web(pending)
        except Exception as exc:
            print(f"official KASI web calculator failed: {exc}", file=sys.stderr)
            return 2
    for episode in manifest["episodes"]:
        status = episode["kasi"]["status"]
        if status == "official_normalized_v07_anchor":
            rows.append({"episode_id": episode["episode_id"], "cell_id": episode["cell_id"], "date": episode["date"], "kasi": {"status": "carried_v07_anchor", "values": episode["kasi"]["values"], "response_sha256": None}})
            continue
        if args.official_web:
            web_row = web_rows.get(episode["episode_id"])
            values = web_row["values"] if web_row else None
            response_sha256 = hashlib.sha256(
                json.dumps(web_row, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest() if web_row else None
            error = None if web_row else {"code": "calculator_row_missing", "message": "KASI web calculator omitted the episode"}
        else:
            values, response_sha256, error = fetch_kasi(key, area_by_region[episode["region_id"]], episode["date"])
        if error:
            failures.append({"episode_id": episode["episode_id"], **error})
            rows.append({"episode_id": episode["episode_id"], "cell_id": episode["cell_id"], "date": episode["date"], "kasi": {"status": "unavailable", "values": None, "response_sha256": None, "error": error}})
        else:
            rows.append({"episode_id": episode["episode_id"], "cell_id": episode["cell_id"], "date": episode["date"], "kasi": {"status": "official_kasi_web_calculator" if args.official_web else "official", "values": values, "response_sha256": response_sha256}})
    payload = {
        "schema_version": "lightguard.v09.official-context.v1",
        "provider": "Korea Astronomy and Space Science Institute (KASI)",
        "dataset": "Area sunrise/sunset and civil twilight information",
        "endpoint": KASI_CALCULATOR if args.official_web else KASI_ENDPOINT,
        "acquisition_mode": "official_kasi_web_calculator_javascript" if args.official_web else "public_data_portal_api",
        "web_calculator_provenance": web_provenance and {key: web_provenance[key] for key in ("calculator_url", "source_urls", "source_sha256")},
        "retrieved_at": now_utc(),
        "episodes": rows,
        "failures": failures,
        "secret_policy": "Service keys are read from process environment only and never serialized.",
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}: official={len(rows) - len(failures)} failures={len(failures)}")
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
