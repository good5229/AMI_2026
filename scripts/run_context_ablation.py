#!/usr/bin/env python3
"""Run reproducible controlled-validation ablation on one frozen 204-case set."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timedelta

from context_common import APP_CONTEXT_DIR, CONTEXT_DIR, REPORT_DIR, ROOT, mirror_to_app, utc_now, write_json


MODELS = ("M0", "M1", "M2", "M3")


def at(base: str, minutes: int) -> str:
    parsed = datetime.fromisoformat(f"2026-01-14 {base}") + timedelta(minutes=minutes)
    return parsed.isoformat(sep=" ", timespec="minutes")


def make_cases(seed: dict, scenario_ids: set[str]) -> list[dict]:
    cases = []
    normal_index = 0
    for cabinet in sorted(seed["objects"], key=lambda row: row["cabinet_uid"]):
        uid = cabinet["cabinet_uid"]
        load = cabinet.get("expected_load", {})
        asset = cabinet.get("asset_info", {})
        if uid in scenario_ids:
            signal = (cabinet.get("detected_signals") or [{}])[0]
            cases.append({
                "case_id": f"ANOM-{uid}", "cabinet_uid": uid, "label": "injected_anomaly",
                "hard_negative_type": None, "activation": float(signal.get("max_activation") or 0.2),
                "duration_min": int(signal.get("estimated_duration_min") or 90),
                "timestamp": signal.get("first_sample") or "2026-01-14 09:30",
                "rated_load_kw": float(load.get("expected_rated_load_kW") or 0),
                "lamp_count": int(load.get("lamp_count") or 0),
                "fixture_count": int(asset.get("fixture_count") or 0),
                "near_solar_boundary": False, "normal_partial_policy": False,
                "weather_context_mode": "official_if_available",
            })
            continue

        normal_index += 1
        category = None
        activation, duration, timestamp = 0.02, 0, "2026-01-14 12:00"
        near_boundary = False
        partial_policy = False
        weather_mode = "official_if_available"
        if normal_index <= 5:
            category, activation, duration, timestamp, near_boundary = "A_sunset_boundary", 0.80, 30, at("17:59", -15), True
        elif normal_index <= 10:
            category, activation, duration, timestamp, near_boundary = "B_sunrise_residual", 0.35, 30, at("07:04", 10), True
        elif normal_index <= 15:
            category, activation, duration, timestamp, weather_mode = "C_adverse_weather", 0.55, 120, "2026-07-15 13:00", "official_adverse_candidate"
        elif normal_index <= 20:
            category, activation, duration, timestamp, partial_policy = "D_normal_partial_operation", 0.20, 90, "2026-01-14 10:00", True
        elif normal_index <= 25:
            category, activation, duration, timestamp = "E_transient_spike", 0.95, 5, "2026-01-14 12:00"
        cases.append({
            "case_id": f"CTRL-{uid}", "cabinet_uid": uid, "label": "normal_control",
            "hard_negative_type": category, "activation": activation, "duration_min": duration,
            "timestamp": timestamp, "rated_load_kw": float(load.get("expected_rated_load_kW") or 0),
            "lamp_count": int(load.get("lamp_count") or 0),
            "fixture_count": int(asset.get("fixture_count") or 0),
            "near_solar_boundary": near_boundary, "normal_partial_policy": partial_policy,
            "weather_context_mode": weather_mode,
        })
    return cases


def score(case: dict, model: str, weather_available: bool) -> tuple[float, bool]:
    duration_factor = min(float(case["duration_min"]) / 30.0, 1.0)
    value = float(case["activation"]) * duration_factor
    candidate = value >= 0.18 and case["duration_min"] >= 15
    if model in ("M1", "M2", "M3") and case["near_solar_boundary"]:
        value = max(0.0, value - 0.45)
        candidate = value >= 0.18
    if model in ("M2", "M3"):
        if case["normal_partial_policy"]:
            value = max(0.0, value - 0.25)
        elif 3.0 <= case["rated_load_kw"] <= 3.8 and case["duration_min"] >= 60:
            value = min(1.0, value + 0.25)
        candidate = value >= 0.18
    if model == "M3" and weather_available and case["weather_context_mode"] == "official_adverse_candidate":
        # Ranking-only experimental modifier: the M2 candidate decision is retained.
        m2_value, m2_candidate = score(case, "M2", weather_available)
        observation = case.get("official_weather_context") or {}
        rain = float(observation.get("precipitation") or 0)
        cloud = float(observation.get("cloud_amount") or 0)
        radiation = observation.get("solar_radiation")
        modifier = min(
            0.15,
            (0.05 if rain > 0 else 0.0)
            + min(max(cloud, 0.0), 10.0) / 10.0 * 0.07
            + (0.03 if radiation is not None and float(radiation) < 0.5 else 0.0),
        )
        value = max(0.0, m2_value - modifier)
        candidate = m2_candidate
    return round(value, 6), candidate


def metrics(cases: list[dict], model: str, weather_available: bool) -> dict[str, object]:
    ranked = []
    for case in cases:
        value, candidate = score(case, model, weather_available)
        ranked.append((value, case["case_id"], case["label"] == "injected_anomaly", candidate))
    ranked.sort(key=lambda row: (-row[0], row[1]))
    anomalies = sum(1 for row in ranked if row[2])
    normals = len(ranked) - anomalies
    true_positive = sum(1 for row in ranked if row[2] and row[3])
    false_positive = sum(1 for row in ranked if not row[2] and row[3])
    result: dict[str, object] = {
        "anomaly_recall": true_positive / anomalies,
        "normal_fpr": false_positive / normals,
        "inspection_candidate_count": true_positive + false_positive,
        "normal_false_positive_count": false_positive,
    }
    for k in (10, 20):
        top = ranked[:k]
        hits = sum(1 for row in top if row[2])
        result[f"precision_at_{k}"] = hits / k
        result[f"recall_at_{k}"] = hits / anomalies
    return result


def main() -> int:
    seed = json.loads((ROOT / "lightguard_v0_1" / "app_seed" / "suyeong_v02_seed.json").read_text(encoding="utf-8"))
    scenarios = json.loads((ROOT / "lightguard_v0_1" / "data" / "simulation_scenarios_v02.json").read_text(encoding="utf-8"))
    scenario_ids = {row["cabinet_uid"] for row in scenarios}
    solar = json.loads((CONTEXT_DIR / "kasi_solar_context_2026.json").read_text(encoding="utf-8"))
    weather = json.loads((CONTEXT_DIR / "kma_asos_busan_2026.json").read_text(encoding="utf-8"))
    observations_by_hour = {
        datetime.fromisoformat(row["timestamp"]).strftime("%Y-%m-%d %H"): row
        for row in weather.get("observations", [])
        if row.get("timestamp")
    }
    cases = make_cases(seed, scenario_ids)
    for case in cases:
        hour = datetime.fromisoformat(case["timestamp"]).strftime("%Y-%m-%d %H")
        observation = observations_by_hour.get(hour)
        case["official_weather_context"] = (
            {
                "timestamp": observation.get("timestamp"),
                "precipitation": observation.get("precipitation"),
                "cloud_amount": observation.get("cloud_amount"),
                "solar_radiation": observation.get("solar_radiation"),
                "source": observation.get("source"),
            }
            if observation
            else None
        )
    if (len(cases), sum(c["label"] == "injected_anomaly" for c in cases)) != (204, 46):
        raise RuntimeError("Frozen validation set must contain 46 anomalies and 158 controls")

    frozen_path = CONTEXT_DIR / "controlled_validation_frozen_2026.json"
    canonical_cases = json.dumps(
        cases, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    frozen_hash = hashlib.sha256(canonical_cases).hexdigest()
    write_json(frozen_path, {
        "schema_version": "lightguard-controlled-validation-v0.3",
        "generated_at": utc_now(),
        "frozen_set_sha256": frozen_hash,
        "case_count": len(cases),
        "injected_anomaly_count": 46,
        "normal_control_count": 158,
        "hard_negative_policy": "five cases each for A-E; remaining controls are inactive",
        "cases": cases,
    })
    mirror_to_app(frozen_path)

    solar_available = solar.get("context_source") == "official" and len(solar.get("dates", [])) == 4
    weather_available = weather.get("context_source") in ("official", "partial") and bool(weather.get("observations"))
    availability = {
        "M0": (True, "available"),
        "M1": (solar_available, "available" if solar_available else "unavailable_official_solar"),
        "M2": (solar_available, "available" if solar_available else "unavailable_official_solar"),
        "M3": (solar_available and weather_available, "available" if solar_available and weather_available else "unavailable_official_context"),
    }

    results = []
    for model in MODELS:
        available, status = availability[model]
        row: dict[str, object] = {"model": model, "status": status, "frozen_set_sha256": frozen_hash}
        if available:
            row.update(metrics(cases, model, weather_available))
        else:
            row.update({key: "" for key in (
                "anomaly_recall", "normal_fpr", "precision_at_10", "precision_at_20",
                "recall_at_10", "recall_at_20", "inspection_candidate_count", "normal_false_positive_count",
            )})
        results.append(row)

    report = REPORT_DIR / "context_ablation_results.csv"
    headers = ["model", "status", "anomaly_recall", "normal_fpr", "precision_at_10", "precision_at_20", "recall_at_10", "recall_at_20", "inspection_candidate_count", "normal_false_positive_count", "frozen_set_sha256"]
    with report.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)
    APP_CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
    (APP_CONTEXT_DIR / report.name).write_bytes(report.read_bytes())

    m0 = results[0]
    summary = [
        "# LightGuard v0.3 Context-Aware Controlled Validation",
        "",
        "This is controlled validation, not field accuracy.",
        "",
        f"- Frozen set: 204 cases (46 injected anomalies, 158 normal controls)",
        f"- Frozen SHA-256: `{frozen_hash}`",
        f"- Official KASI available: {solar_available}",
        f"- Official KMA available: {weather_available}",
        f"- M0 inspection candidates: {m0.get('inspection_candidate_count', '')}",
        "- M3 inspection candidates: unavailable" if not availability["M3"][0] else f"- M3 inspection candidates: {results[3]['inspection_candidate_count']}",
        "- Potential dispatch-cost conversion: prohibited until a sourced per-dispatch cost exists.",
        "",
        "## Results",
        "",
        "| Model | Status | Anomaly recall | Normal FPR | P@10 | P@20 | R@10 | R@20 |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in results:
        summary.append("| {model} | {status} | {anomaly_recall} | {normal_fpr} | {precision_at_10} | {precision_at_20} | {recall_at_10} | {recall_at_20} |".format(**row))
    summary += [
        "",
        "## Interpretation",
        "",
        "M1-M3 are intentionally unavailable when official snapshots cannot be collected. No internal or synthetic value is substituted for official context.",
        "Weather is implemented as a ranking confidence modifier; it never clears the M2 inspection-candidate decision.",
    ]
    (REPORT_DIR / "context_validation_summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    return 0 if availability["M3"][0] else 2


if __name__ == "__main__":
    raise SystemExit(main())
