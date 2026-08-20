#!/usr/bin/env python3
"""Fetch official KASI solar context and compare it with the internal formula."""

from __future__ import annotations

import csv
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from context_common import (
    APP_CONTEXT_DIR,
    CONTEXT_DIR,
    REPORT_DIR,
    ROOT,
    curl_get,
    mirror_to_app,
    service_key,
    suyeong_centroid,
    utc_now,
    write_json,
)

sys.path.insert(0, str(ROOT / "lightguard_v0_1" / "src"))
from build_lightguard_v02 import calc_sun_schedule  # noqa: E402


DATES = ("2026-01-14", "2026-04-15", "2026-07-15", "2026-10-15")
ENDPOINT = "https://apis.data.go.kr/B090041/openapi/service/RiseSetInfoService/getLCRiseSetInfo"


def hhmm(value: str | None) -> str | None:
    if not value:
        return None
    digits = "".join(ch for ch in value if ch.isdigit()).zfill(4)[-4:]
    return f"{digits[:2]}:{digits[2:]}"


def minutes(value: str) -> int:
    hour, minute = value.split(":")
    return int(hour) * 60 + int(minute)


def main() -> int:
    retrieved_at = utc_now()
    location = suyeong_centroid()
    key = service_key("KASI_SERVICE_KEY")
    rows = []
    failures = []
    for date in DATES:
        item = None
        error = None
        if not key:
            error = {"code": "missing_service_key", "message": "KASI service key is unavailable", "retryable": True}
        else:
            try:
                raw = curl_get(
                    ENDPOINT,
                    {
                        "ServiceKey": key,
                        "locdate": date.replace("-", ""),
                        "longitude": location["longitude"],
                        "latitude": location["latitude"],
                        "dnYn": "Y",
                    },
                )
                root = ET.fromstring(raw)
                node = root.find(".//item")
                if node is None:
                    header = root.find(".//cmmMsgHeader")
                    error = {
                        "code": (header.findtext("returnReasonCode") if header is not None else None) or root.findtext(".//resultCode") or "empty_response",
                        "message": (header.findtext("returnAuthMsg") if header is not None else None) or root.findtext(".//resultMsg") or "KASI response contained no item",
                        "retryable": False,
                    }
                else:
                    item = {
                        "date": date,
                        "sunrise": hhmm(node.findtext("sunrise")),
                        "sunset": hhmm(node.findtext("sunset")),
                        "civil_twilight_start": hhmm(node.findtext("civilm")),
                        "civil_twilight_end": hhmm(node.findtext("civile")),
                        "source": "KASI_RISE_SET_OFFICIAL",
                        "retrieved_at": retrieved_at,
                    }
            except Exception as exc:  # API failures are serialized, never replaced.
                error = {"code": "request_failed", "message": str(exc), "retryable": True}
        if item is None:
            failures.append({"date": date, **(error or {})})
            item = {
                "date": date,
                "sunrise": None,
                "sunset": None,
                "civil_twilight_start": None,
                "civil_twilight_end": None,
                "source": "unavailable",
                "retrieved_at": retrieved_at,
                "error": error,
            }
        rows.append(item)

    context_source = "official" if not failures else ("partial" if len(failures) < len(DATES) else "unavailable")
    output = CONTEXT_DIR / "kasi_solar_context_2026.json"
    write_json(
        output,
        {
            "schema_version": "lightguard-context-v0.3",
            "context_source": context_source,
            "provider": "Korea Astronomy and Space Science Institute (KASI)",
            "endpoint_purpose": "location-based sunrise, sunset and civil twilight",
            "location": location,
            "retrieved_at": retrieved_at,
            "dates": rows,
            "errors": failures,
        },
    )
    mirror_to_app(output)

    report = REPORT_DIR / "kasi_validation.csv"
    report.parent.mkdir(parents=True, exist_ok=True)
    headers = [
        "date", "status", "internal_sunrise", "official_sunrise", "sunrise_delta_min",
        "internal_sunset", "official_sunset", "sunset_delta_min",
        "internal_civil_start", "official_civil_start", "civil_start_delta_min",
        "internal_civil_end", "official_civil_end", "civil_end_delta_min",
    ]
    with report.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            internal = calc_sun_schedule(
                datetime.fromisoformat(row["date"]).date(),
                float(location["latitude"]),
                float(location["longitude"]),
            )
            available = row["source"] == "KASI_RISE_SET_OFFICIAL"
            values = {
                "date": row["date"],
                "status": "available" if available else "unavailable",
                "internal_sunrise": internal["sunrise"],
                "official_sunrise": row["sunrise"] or "",
                "internal_sunset": internal["sunset"],
                "official_sunset": row["sunset"] or "",
                "internal_civil_start": internal["civil_twilight_start"],
                "official_civil_start": row["civil_twilight_start"] or "",
                "internal_civil_end": internal["civil_twilight_end"],
                "official_civil_end": row["civil_twilight_end"] or "",
            }
            for internal_key, official_key, delta_key in (
                ("internal_sunrise", "official_sunrise", "sunrise_delta_min"),
                ("internal_sunset", "official_sunset", "sunset_delta_min"),
                ("internal_civil_start", "official_civil_start", "civil_start_delta_min"),
                ("internal_civil_end", "official_civil_end", "civil_end_delta_min"),
            ):
                values[delta_key] = minutes(values[internal_key]) - minutes(values[official_key]) if available else ""
            writer.writerow(values)
    (APP_CONTEXT_DIR / report.name).write_bytes(report.read_bytes())
    print(f"KASI context_source={context_source}; dates={len(rows)}; unavailable={len(failures)}")
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
