#!/usr/bin/env python3
"""Collect official 2026 Busan ASOS observations and select weather regimes."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta

from context_common import CONTEXT_DIR, as_number, curl_get, service_key, utc_now, write_json


ENDPOINT = "https://apis.data.go.kr/1360000/AsosHourlyInfoService/getWthrDataList"
STATION_ID = "159"
FIELDS = (
    "temperature", "precipitation", "humidity", "cloud_amount", "sunshine",
    "solar_radiation", "visibility", "wind_speed",
)


def quantile(values: list[float], fraction: float) -> float | None:
    ordered = sorted(values)
    if not ordered:
        return None
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def fetch_chunk(key: str, start: date, end: date) -> list[dict]:
    raw = curl_get(ENDPOINT, {
        "ServiceKey": key,
        "pageNo": 1,
        "numOfRows": 999,
        "dataType": "JSON",
        "dataCd": "ASOS",
        "dateCd": "HR",
        "startDt": start.strftime("%Y%m%d"),
        "startHh": "00",
        "endDt": end.strftime("%Y%m%d"),
        "endHh": "23",
        "stnIds": STATION_ID,
    }, retries=2)
    payload = json.loads(raw)
    auth = payload.get("OpenAPI_ServiceResponse", {}).get("cmmMsgHeader")
    if auth:
        raise RuntimeError(auth.get("returnAuthMsg") or auth.get("errMsg") or "KMA authorization error")
    response = payload.get("response", {})
    header = response.get("header", {})
    if header.get("resultCode") != "00":
        raise RuntimeError(header.get("resultMsg") or "KMA response error")
    items = response.get("body", {}).get("items", {}).get("item", [])
    if isinstance(items, dict):
        items = [items]
    rows = []
    for item in items:
        timestamp = item.get("tm")
        if not timestamp:
            continue
        datetime.fromisoformat(timestamp)
        rows.append({
            "timestamp": timestamp,
            "temperature": as_number(item.get("ta")),
            "precipitation": as_number(item.get("rn")),
            "humidity": as_number(item.get("hm")),
            "cloud_amount": as_number(item.get("dc10Tca")),
            "sunshine": as_number(item.get("ss")),
            "solar_radiation": as_number(item.get("icsr")),
            "visibility": as_number(item.get("vs")),
            "wind_speed": as_number(item.get("ws")),
            "station_id": str(item.get("stnId") or STATION_ID),
            "station_name": item.get("stnNm") or "부산",
            "source": "KMA_ASOS_HOURLY_OFFICIAL",
        })
    return rows


def compact(row: dict) -> dict:
    return {"timestamp": row["timestamp"], **{field: row.get(field) for field in FIELDS},
            "source": row["source"]}


def main() -> int:
    key = service_key("KMA_SERVICE_KEY")
    end = min(date.today() - timedelta(days=1), date(2026, 12, 31))
    start = date(2026, 1, 1)
    output = CONTEXT_DIR / "kma_weather_regimes_2026.json"
    if not key:
        write_json(output, {
            "schema_version": "lightguard-weather-regimes-v0.4",
            "context_source": "unavailable",
            "station_id": STATION_ID,
            "requested_start": start.isoformat(),
            "requested_end": end.isoformat(),
            "errors": [{"code": "missing_service_key", "message": "KMA service key is unavailable"}],
            "regimes": [],
        })
        return 2

    observations: dict[str, dict] = {}
    errors = []
    cursor = start
    while cursor <= end:
        chunk_end = min(cursor + timedelta(days=30), end)
        try:
            for row in fetch_chunk(key, cursor, chunk_end):
                observations[row["timestamp"]] = row
        except Exception as exc:
            errors.append({"start": cursor.isoformat(), "end": chunk_end.isoformat(), "message": str(exc)})
        cursor = chunk_end + timedelta(days=1)

    rows = [observations[key] for key in sorted(observations)]
    if not rows:
        write_json(output, {
            "schema_version": "lightguard-weather-regimes-v0.4",
            "context_source": "unavailable",
            "station_id": STATION_ID,
            "requested_start": start.isoformat(),
            "requested_end": end.isoformat(),
            "errors": errors or [{"code": "empty_response", "message": "No official observations returned"}],
            "regimes": [],
        })
        return 2

    daylight = [row for row in rows if 8 <= datetime.fromisoformat(row["timestamp"]).hour <= 18]
    q = {
        "cloud_q25": quantile([row["cloud_amount"] for row in daylight if row["cloud_amount"] is not None], .25),
        "cloud_q75": quantile([row["cloud_amount"] for row in daylight if row["cloud_amount"] is not None], .75),
        "radiation_q25": quantile([row["solar_radiation"] for row in daylight if row["solar_radiation"] is not None], .25),
        "radiation_q75": quantile([row["solar_radiation"] for row in daylight if row["solar_radiation"] is not None], .75),
        "humidity_q90": quantile([row["humidity"] for row in rows if row["humidity"] is not None], .90),
        "visibility_q10": quantile([row["visibility"] for row in rows if row["visibility"] is not None], .10),
    }

    def dry(row: dict) -> bool:
        return (row.get("precipitation") or 0) <= 0

    candidates = {
        "CLEAR": [row for row in daylight if dry(row) and row.get("cloud_amount") is not None
                  and row.get("solar_radiation") is not None and row["cloud_amount"] <= q["cloud_q25"]
                  and row["solar_radiation"] >= q["radiation_q75"]],
        "OVERCAST": [row for row in daylight if dry(row) and row.get("cloud_amount") is not None
                     and row["cloud_amount"] >= q["cloud_q75"]],
        "RAIN": [row for row in rows if (row.get("precipitation") or 0) > 0],
        "LOW_SOLAR": [row for row in daylight if row.get("solar_radiation") is not None
                      and row["solar_radiation"] <= q["radiation_q25"]],
        "HIGH_HUMIDITY_OR_LOW_VISIBILITY": [row for row in rows if
            (row.get("humidity") is not None and row["humidity"] >= q["humidity_q90"])
            or (row.get("visibility") is not None and row["visibility"] <= q["visibility_q10"])],
    }
    sorters = {
        "CLEAR": lambda row: (-(row.get("solar_radiation") or 0), row.get("cloud_amount") or 0, row["timestamp"]),
        "OVERCAST": lambda row: (-(row.get("cloud_amount") or 0), row.get("solar_radiation") or 0, row["timestamp"]),
        "RAIN": lambda row: (-(row.get("precipitation") or 0), row["timestamp"]),
        "LOW_SOLAR": lambda row: (row.get("solar_radiation") or 0, -(row.get("cloud_amount") or 0), row["timestamp"]),
        "HIGH_HUMIDITY_OR_LOW_VISIBILITY": lambda row: (-(row.get("humidity") or 0), row.get("visibility") or 999999, row["timestamp"]),
    }
    rules = {
        "CLEAR": "daylight; no rain; cloud <= q25; solar radiation >= q75",
        "OVERCAST": "daylight; no rain; cloud >= q75",
        "RAIN": "precipitation > 0",
        "LOW_SOLAR": "daylight; solar radiation <= q25",
        "HIGH_HUMIDITY_OR_LOW_VISIBILITY": "humidity >= q90 OR visibility <= q10",
    }
    regimes = []
    for name in candidates:
        selected = sorted(candidates[name], key=sorters[name])[:6]
        regimes.append({
            "regime": name,
            "date": selected[0]["timestamp"][:10] if selected else None,
            "representative_hours": [compact(row) for row in selected],
            "selection_rule": rules[name],
            "source": "KMA_ASOS_HOURLY_OFFICIAL" if selected else "unavailable",
        })
    write_json(output, {
        "schema_version": "lightguard-weather-regimes-v0.4",
        "context_source": "official" if all(row["representative_hours"] for row in regimes) else "partial",
        "provider": "Korea Meteorological Administration (KMA)",
        "station_id": STATION_ID,
        "station_name": "부산",
        "requested_start": start.isoformat(),
        "requested_end": end.isoformat(),
        "future_dates_excluded": True,
        "retrieved_at": utc_now(),
        "observation_count": len(rows),
        "quantiles": q,
        "regimes": regimes,
        "errors": errors,
    })
    print(f"KMA regimes: observations={len(rows)} regimes={sum(bool(r['representative_hours']) for r in regimes)}/5 errors={len(errors)}")
    return 0 if all(row["representative_hours"] for row in regimes) and not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
