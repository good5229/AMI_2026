#!/usr/bin/env python3
"""Fetch official KMA ASOS hourly observations for Busan station 159."""

from __future__ import annotations

import json
from datetime import date, datetime

from context_common import CONTEXT_DIR, as_number, curl_get, mirror_to_app, service_key, utc_now, write_json


DATES = ("2026-01-14", "2026-04-15", "2026-07-15", "2026-10-15")
ENDPOINT = "https://apis.data.go.kr/1360000/AsosHourlyInfoService/getWthrDataList"


def main() -> int:
    key = service_key("KMA_SERVICE_KEY")
    retrieved_at = utc_now()
    observations = []
    failures = []
    for target in DATES:
        if date.fromisoformat(target) > date.today():
            failures.append({"date": target, "code": "future_date", "message": "Observation date has not occurred", "retryable": True})
            continue
        if not key:
            failures.append({"date": target, "code": "missing_service_key", "message": "KMA service key is unavailable", "retryable": True})
            continue
        try:
            raw = curl_get(
                ENDPOINT,
                {
                    "ServiceKey": key,
                    "pageNo": 1,
                    "numOfRows": 48,
                    "dataType": "JSON",
                    "dataCd": "ASOS",
                    "dateCd": "HR",
                    "startDt": target.replace("-", ""),
                    "startHh": "00",
                    "endDt": target.replace("-", ""),
                    "endHh": "23",
                    "stnIds": "159",
                },
            )
            payload = json.loads(raw)
            auth = payload.get("OpenAPI_ServiceResponse", {}).get("cmmMsgHeader")
            if auth:
                failures.append({
                    "date": target,
                    "code": auth.get("returnReasonCode") or "authorization_error",
                    "message": auth.get("returnAuthMsg") or auth.get("errMsg") or "KMA authorization error",
                    "retryable": False,
                })
                continue
            response = payload.get("response", {})
            header = response.get("header", {})
            items = response.get("body", {}).get("items", {}).get("item", [])
            if header.get("resultCode") != "00" or not items:
                failures.append({"date": target, "code": header.get("resultCode") or "empty_response", "message": header.get("resultMsg") or "KMA response contained no observations", "retryable": True})
                continue
            if isinstance(items, dict):
                items = [items]
            for item in items:
                timestamp = item.get("tm")
                if timestamp:
                    datetime.fromisoformat(timestamp)
                observations.append({
                    "timestamp": timestamp,
                    "temperature": as_number(item.get("ta")),
                    "precipitation": as_number(item.get("rn")),
                    "humidity": as_number(item.get("hm")),
                    "cloud_amount": as_number(item.get("dc10Tca")),
                    "sunshine": as_number(item.get("ss")),
                    "solar_radiation": as_number(item.get("icsr")),
                    "visibility": as_number(item.get("vs")),
                    "wind_speed": as_number(item.get("ws")),
                    "station_id": str(item.get("stnId") or "159"),
                    "station_name": item.get("stnNm") or "부산",
                    "source": "KMA_ASOS_HOURLY_OFFICIAL",
                })
        except Exception as exc:
            failures.append({"date": target, "code": "request_failed", "message": str(exc), "retryable": True})

    available_dates = sorted({row["timestamp"][:10] for row in observations if row.get("timestamp")})
    status = "official" if len(available_dates) == len(DATES) else ("partial" if observations else "unavailable")
    output = CONTEXT_DIR / "kma_asos_busan_2026.json"
    write_json(output, {
        "schema_version": "lightguard-context-v0.3",
        "context_source": status,
        "provider": "Korea Meteorological Administration (KMA)",
        "station_id": "159",
        "station_name": "부산",
        "requested_dates": list(DATES),
        "available_dates": available_dates,
        "retrieved_at": retrieved_at,
        "observations": observations,
        "errors": failures,
    })
    mirror_to_app(output)
    print(f"KMA context_source={status}; observations={len(observations)}; unavailable={len(failures)}")
    elapsed_dates = {target for target in DATES if date.fromisoformat(target) <= date.today()}
    return 0 if elapsed_dates.issubset(set(available_dates)) else 2


if __name__ == "__main__":
    raise SystemExit(main())
