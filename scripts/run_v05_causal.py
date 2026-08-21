#!/usr/bin/env python3
"""Run leakage-free walk-forward and temporal audits on five actual AMI meters."""

from __future__ import annotations

import csv
import glob
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import openpyxl


ROOT = Path(__file__).resolve().parents[1]
V05_DATA = ROOT / "lightguard_v0_1" / "data" / "validation" / "v05"
V05_REPORTS = ROOT / "lightguard_v0_1" / "reports" / "v05"
APP_DATA = ROOT / "lightguard_app" / "assets" / "data"
TARGET_METERS = ("B-L-9", "B-L-12", "B-L-13", "B-L-14", "B-L-35")
WINDOWS = ("7d", "14d", "30d", "expanding")
START_DATE = date(2026, 4, 1)
END_DATE = date(2026, 6, 30)
KST = ZoneInfo("Asia/Seoul")
EXPECTED = {
    "v03": "935bc5ea7d70e878f15113dc08d11dfee7ebcbb350d90d421f46a7704cf27368",
    "calibration": "8fe85425f6ca3b9bc2517a137da96d3edc22bbf387209b53efd933364496032e",
    "holdout": "1be716621da5b53bce11a748d9b05e63d4aa329e7d62b8f16e606b2ccff09831",
    "workbook": "c18b49022d1c7dee2117a8d65a07d71351fb1aea8538751b7032867e4081b7d0",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict], headers: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if headers is None:
        headers = []
        seen = set()
        for row in rows:
            for key in row:
                if key not in seen:
                    seen.add(key)
                    headers.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_interval_end(value: object) -> tuple[datetime, bool]:
    text = str(value).strip()
    if text.endswith(" 24:00"):
        parsed = datetime.fromisoformat(text[:-5] + "00:00") + timedelta(days=1)
        return parsed.replace(tzinfo=KST), True
    return datetime.fromisoformat(text).replace(tzinfo=KST), False


def midnight(day: date) -> datetime:
    return datetime.combine(day, time.min, tzinfo=KST)


def number(value: object) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    return float(value)


def locate_workbook() -> Path:
    matches = [Path(path) for path in glob.glob(str(ROOT / "official_docs" / "AMI Data Sample" / "*B*★.xlsx"))]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one ignored B-line MDMS workbook, found {len(matches)}")
    return matches[0]


def load_actual_rows(path: Path) -> dict[str, list[dict]]:
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet = workbook["B선로 AMI DATA"]
    result = {meter: [] for meter in TARGET_METERS}
    for source_row, values in enumerate(sheet.iter_rows(min_row=3, values_only=True), start=3):
        meter = str(values[0]) if values[0] is not None else ""
        if meter not in result:
            continue
        timestamp, normalized_24h = parse_interval_end(values[1])
        if not (midnight(START_DATE) < timestamp <= midnight(END_DATE + timedelta(days=1))):
            continue
        currents = tuple(number(values[index]) for index in (13, 14, 15))
        measured = [value for value in currents if value is not None]
        result[meter].append({
            "meter_id": meter,
            "timestamp": timestamp,
            "availability_time": timestamp,
            "availability_basis": "source interval-end timestamp proxy; source receipt time unavailable",
            "source_timestamp": str(values[1]),
            "normalized_24h": normalized_24h,
            "recv_active_kwh": number(values[3]),
            "v1": number(values[10]),
            "v2": number(values[11]),
            "v3": number(values[12]),
            "i1": currents[0],
            "i2": currents[1],
            "i3": currents[2],
            "total_current": sum(measured) if measured else None,
            "source_row": source_row,
        })
    workbook.close()
    for meter, rows in result.items():
        rows.sort(key=lambda row: (row["timestamp"], row["source_row"]))
        if not rows:
            raise RuntimeError(f"No actual rows for {meter}")
    return result


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def cadence_minutes(rows: list[dict]) -> int:
    unique = sorted({row["timestamp"] for row in rows})
    gaps = [int((right - left).total_seconds() / 60) for left, right in zip(unique, unique[1:]) if right > left]
    return int(statistics.median(gaps)) if gaps else 15


def baseline(rows: list[dict], cutoff: datetime, window: str) -> dict | None:
    if window == "expanding":
        start = midnight(START_DATE)
        if cutoff < start + timedelta(days=7):
            return None
    else:
        days = int(window[:-1])
        start = cutoff - timedelta(days=days)
        if start < midnight(START_DATE):
            return None
    history = [row for row in rows if start <= row["timestamp"] < cutoff and row["total_current"] is not None]
    off_values = [row["total_current"] for row in history if 10 <= row["timestamp"].hour < 15]
    on_values = [row["total_current"] for row in history if row["timestamp"].hour >= 22 or row["timestamp"].hour < 4]
    if len(off_values) < 16 or len(on_values) < 16:
        return None
    phase = {}
    for key in ("i1", "i2", "i3"):
        off = [row[key] for row in history if 10 <= row["timestamp"].hour < 15 and row[key] is not None]
        on = [row[key] for row in history if (row["timestamp"].hour >= 22 or row["timestamp"].hour < 4) and row[key] is not None]
        phase[key] = {"off": median(off), "on": median(on)}
    off_value, on_value = median(off_values), median(on_values)
    if off_value is None or on_value is None or on_value <= off_value:
        return None
    return {
        "off": off_value,
        "on": on_value,
        "separation": on_value - off_value,
        "history_start": min(row["timestamp"] for row in history),
        "history_end": max(row["timestamp"] for row in history),
        "history_rows": len(history),
        "phase": phase,
    }


def full_sample_baseline(rows: list[dict]) -> dict:
    cutoff = midnight(END_DATE + timedelta(days=1)) + timedelta(minutes=1)
    result = baseline(rows, cutoff, "expanding")
    if result is None:
        raise RuntimeError("Full-sample baseline unavailable")
    return result


def detect_for_day(rows: list[dict], day: date, base: dict, meter: str, window: str) -> list[dict]:
    cadence = cadence_minutes(rows)
    decision_time = midnight(day + timedelta(days=1)) + timedelta(minutes=cadence)
    day_rows = [
        row for row in rows
        if (row["timestamp"].date() - timedelta(days=1) if row["normalized_24h"] else row["timestamp"].date()) == day
        and row["availability_time"] < decision_time
        and row["total_current"] is not None
    ]
    if any(row["availability_time"] >= decision_time for row in day_rows):
        raise RuntimeError("causal availability cutoff violated")
    points = []
    for row in day_rows:
        activation = (row["total_current"] - base["off"]) / base["separation"]
        if 9 <= row["timestamp"].hour < 17 and activation >= 0.20:
            points.append({**row, "activation": activation})
    groups: list[list[dict]] = []
    for row in points:
        if not groups or (row["timestamp"] - groups[-1][-1]["timestamp"]).total_seconds() / 60 > max(30, cadence * 2):
            groups.append([row])
        else:
            groups[-1].append(row)
    events = []
    for group in groups:
        maximum = max(row["activation"] for row in group)
        duration = len(group) * cadence
        if not (maximum >= .80 or (maximum >= .40 and duration >= 15) or (maximum >= .20 and duration >= 30)):
            continue
        phase_max = {}
        measured_phases = []
        for key, values in base["phase"].items():
            off, on = values["off"], values["on"]
            if off is None or on is None or on <= off:
                continue
            measured_phases.append(key)
            activations = [(row[key] - off) / (on - off) for row in group if row[key] is not None]
            if activations:
                phase_max[key] = max(activations)
        active_phases = sorted(key for key, value in phase_max.items() if value >= .20)
        if maximum >= .80:
            event_type = "daytime_full_activation"
        elif len(measured_phases) >= 2 and 0 < len(active_phases) < len(measured_phases):
            event_type = "daytime_phase_selective_activation"
        else:
            event_type = "daytime_partial_activation"
        first, last = group[0]["timestamp"], group[-1]["timestamp"]
        event_id = hashlib.sha1(f"{window}|{meter}|{first.isoformat()}|{last.isoformat()}".encode()).hexdigest()[:12]
        events.append({
            "event_id": f"WF-{event_id}",
            "meter_id": meter,
            "baseline_window": window,
            "evaluation_date": day.isoformat(),
            "status": "candidate",
            "first_sample": first.isoformat(sep=" "),
            "last_sample": last.isoformat(sep=" "),
            "estimated_end": (last + timedelta(minutes=cadence)).isoformat(sep=" "),
            "duration_min": duration,
            "max_activation": round(maximum, 6),
            "peak_total_current_a": round(max(row["total_current"] for row in group), 6),
            "event_type": event_type,
            "active_phases": ",".join(active_phases),
            "off_baseline_a": round(base["off"], 6),
            "on_baseline_a": round(base["on"], 6),
            "baseline_history_start": base["history_start"].isoformat(sep=" "),
            "baseline_history_end": base["history_end"].isoformat(sep=" "),
            "baseline_history_rows": base["history_rows"],
            "decision_time": decision_time.isoformat(sep=" "),
            "latest_consumed_availability_time": max(row["availability_time"] for row in group).isoformat(sep=" "),
            "availability_basis": "Asia/Seoul source interval-end timestamp proxy; receipt time unavailable",
            "causal_rule": "baseline timestamp < evaluation-day 00:00 and consumed availability_time < next-day 00:15 decision",
            "truth_label": "unavailable_known_detector_candidate_only",
        })
    return events


def load_canonical_events() -> list[dict]:
    path = APP_DATA / "ami_events.csv"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["start_dt"] = datetime.fromisoformat(row["first_sample"]).replace(tzinfo=KST)
        row["end_dt"] = datetime.fromisoformat(row["last_sample"]).replace(tzinfo=KST) + timedelta(minutes=15)
    return rows


def overlaps(left_start: datetime, left_end: datetime, right_start: datetime, right_end: datetime) -> bool:
    return left_start < right_end and right_start < left_end


def coverage(candidates: list[dict], canonical: list[dict]) -> tuple[int, dict[str, bool]]:
    result = {}
    for event in canonical:
        matched = any(
            row["meter_id"] == event["meter_id"]
            and overlaps(datetime.fromisoformat(row["first_sample"]), datetime.fromisoformat(row["estimated_end"]),
                         event["start_dt"], event["end_dt"])
            for row in candidates
        )
        result[event["event_id"]] = matched
    return sum(result.values()), result


def candidate_jaccard(left: list[dict], right: list[dict]) -> float:
    matched_right: set[int] = set()
    matches = 0
    for lrow in left:
        for index, rrow in enumerate(right):
            if index in matched_right or lrow["meter_id"] != rrow["meter_id"]:
                continue
            if overlaps(datetime.fromisoformat(lrow["first_sample"]), datetime.fromisoformat(lrow["estimated_end"]),
                        datetime.fromisoformat(rrow["first_sample"]), datetime.fromisoformat(rrow["estimated_end"])):
                matched_right.add(index)
                matches += 1
                break
    union = len(left) + len(right) - matches
    return matches / union if union else 1.0


def full_sample_candidates(actual: dict[str, list[dict]]) -> list[dict]:
    result = []
    for meter, rows in actual.items():
        base = full_sample_baseline(rows)
        day = START_DATE
        while day <= END_DATE:
            result.extend(detect_for_day(rows, day, base, meter, "full_sample"))
            day += timedelta(days=1)
    return result


def run_walkforward(actual: dict[str, list[dict]]) -> tuple[list[dict], dict[str, list[dict]], dict]:
    output = []
    candidates_by_window = {window: [] for window in WINDOWS}
    evaluable_days = Counter()
    warmup_days = Counter()
    for meter, rows in actual.items():
        for window in WINDOWS:
            day = START_DATE
            while day <= END_DATE:
                cutoff = midnight(day)
                base = baseline(rows, cutoff, window)
                if base is None:
                    warmup_days[window] += 1
                    output.append({
                        "event_id": "", "meter_id": meter, "baseline_window": window,
                        "evaluation_date": day.isoformat(), "status": "not_evaluable_warmup",
                        "decision_time": (midnight(day + timedelta(days=1)) + timedelta(minutes=15)).isoformat(sep=" "),
                        "availability_basis": "Asia/Seoul source interval-end timestamp proxy; receipt time unavailable",
                        "causal_rule": "no synthetic baseline; baseline timestamp < evaluation-day 00:00",
                        "truth_label": "unavailable_known_detector_candidate_only",
                    })
                else:
                    evaluable_days[window] += 1
                    events = detect_for_day(rows, day, base, meter, window)
                    candidates_by_window[window].extend(events)
                    output.append({
                        "event_id": "", "meter_id": meter, "baseline_window": window,
                        "evaluation_date": day.isoformat(), "status": "evaluable",
                        "off_baseline_a": round(base["off"], 6), "on_baseline_a": round(base["on"], 6),
                        "baseline_history_start": base["history_start"].isoformat(sep=" "),
                        "baseline_history_end": base["history_end"].isoformat(sep=" "),
                        "baseline_history_rows": base["history_rows"],
                        "decision_time": (midnight(day + timedelta(days=1)) + timedelta(minutes=cadence_minutes(rows))).isoformat(sep=" "),
                        "availability_basis": "Asia/Seoul source interval-end timestamp proxy; receipt time unavailable",
                        "causal_rule": "baseline timestamp < evaluation-day 00:00 and consumed availability_time < decision_time",
                        "truth_label": "unavailable_known_detector_candidate_only",
                    })
                    output.extend(events)
                day += timedelta(days=1)
    return output, candidates_by_window, {"evaluable_days": dict(evaluable_days), "warmup_days": dict(warmup_days)}


def coefficient_of_variation(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    mean = statistics.mean(values)
    return statistics.pstdev(values) / mean if mean else None


def transition_minutes(rows: list[dict], off: float, on: float) -> tuple[list[int], list[int]]:
    separation = on - off
    by_day = defaultdict(list)
    for row in rows:
        if row["total_current"] is not None:
            by_day[row["timestamp"].date()].append(row)
    morning, evening = [], []
    for day_rows in by_day.values():
        day_rows.sort(key=lambda row: row["timestamp"])
        for previous, current in zip(day_rows, day_rows[1:]):
            pa = (previous["total_current"] - off) / separation
            ca = (current["total_current"] - off) / separation
            if 4 <= current["timestamp"].hour < 9 and pa >= .5 > ca:
                morning.append(current["timestamp"].hour * 60 + current["timestamp"].minute)
                break
        for previous, current in zip(day_rows, day_rows[1:]):
            pa = (previous["total_current"] - off) / separation
            ca = (current["total_current"] - off) / separation
            if 17 <= current["timestamp"].hour < 23 and pa < .5 <= ca:
                evening.append(current["timestamp"].hour * 60 + current["timestamp"].minute)
                break
    return morning, evening


def temporal_profiles(actual: dict[str, list[dict]], causal_30d: list[dict], canonical: list[dict]) -> tuple[list[dict], dict]:
    rows_out = []
    profiles = {}
    for meter, rows in actual.items():
        duplicates = len(rows) - len({row["timestamp"] for row in rows})
        phase_counts = {key: sum(row[key] is not None for row in rows) for key in ("i1", "i2", "i3")}
        energy_count = sum(row["recv_active_kwh"] is not None for row in rows)
        meter_profile = {
            "sampling_interval_min": cadence_minutes(rows),
            "row_count": len(rows),
            "duplicate_timestamp_count": duplicates,
            "hour24_normalization_count": sum(row["normalized_24h"] for row in rows),
            "phase_non_missing_counts": phase_counts,
            "measured_phase_count": sum(count > 0 for count in phase_counts.values()),
            "energy_non_missing_count": energy_count,
            "energy_availability": energy_count / len(rows),
            "canonical_candidate_count": sum(event["meter_id"] == meter for event in canonical),
        }
        monthly = []
        for month in (4, 5, 6):
            month_rows = [row for row in rows if row["timestamp"].month == month and row["timestamp"].date() <= END_DATE]
            valid = [row for row in month_rows if row["total_current"] is not None]
            off_values = [row["total_current"] for row in valid if 10 <= row["timestamp"].hour < 15]
            on_values = [row["total_current"] for row in valid if row["timestamp"].hour >= 22 or row["timestamp"].hour < 4]
            off, on = median(off_values), median(on_values)
            night_daily = defaultdict(list)
            for row in valid:
                if row["timestamp"].hour >= 22 or row["timestamp"].hour < 4:
                    night_daily[row["timestamp"].date()].append(row["total_current"])
            night_medians = [statistics.median(values) for values in night_daily.values() if values]
            morning, evening = transition_minutes(valid, off, on) if off is not None and on is not None and on > off else ([], [])
            month_candidates = [row for row in causal_30d if row["meter_id"] == meter and datetime.fromisoformat(row["first_sample"]).month == month]
            expected = 30 * 96 if month in (4, 6) else 31 * 96
            record = {
                "meter_id": meter,
                "month": f"2026-{month:02d}",
                "off_baseline_a": round(off, 6) if off is not None else None,
                "on_baseline_a": round(on, 6) if on is not None else None,
                "on_off_separation_a": round(on - off, 6) if off is not None and on is not None else None,
                "night_current_cv": round(coefficient_of_variation(night_medians), 6) if coefficient_of_variation(night_medians) is not None else None,
                "transition_off_median_minute": round(statistics.median(morning)) if morning else None,
                "transition_on_median_minute": round(statistics.median(evening)) if evening else None,
                "candidate_count_30d_causal": len(month_candidates),
                "data_availability": round(len(valid) / expected, 6),
                "missing_current_rows": len(month_rows) - len(valid),
                "interpretation": "descriptive meter behavior; not a fault rate",
            }
            rows_out.append(record)
            monthly.append(record)
        meter_profile["monthly"] = monthly
        profiles[meter] = meter_profile
    return rows_out, profiles


def main() -> int:
    V05_DATA.mkdir(parents=True, exist_ok=True)
    V05_REPORTS.mkdir(parents=True, exist_ok=True)
    summary_path = ROOT / "lightguard_v0_1" / "data" / "context" / "v04_validation_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary["v03_frozen_set_sha256"] != EXPECTED["v03"]:
        raise RuntimeError("v0.3 frozen SHA changed")
    if summary["calibration_sha256"] != EXPECTED["calibration"]:
        raise RuntimeError("v0.4 calibration SHA changed")
    if summary["confirmatory_holdout_sha256"] != EXPECTED["holdout"]:
        raise RuntimeError("v0.4 holdout SHA changed")
    if summary["frozen_weights"]["weather"] != 0 or summary["weather_decision"] != "context_only":
        raise RuntimeError("Frozen weather decision changed")
    workbook_path = locate_workbook()
    workbook_hash = sha256(workbook_path)
    if workbook_hash != EXPECTED["workbook"]:
        raise RuntimeError("Original B-line workbook hash changed")
    canonical_path = APP_DATA / "ami_events.csv"
    canonical = load_canonical_events()
    if len(canonical) != 6:
        raise RuntimeError("Canonical AMI event count changed")
    integrity = {
        "schema_version": "lightguard-v0.5-baseline-integrity",
        "v03_frozen_sha256": EXPECTED["v03"],
        "v04_calibration_sha256": EXPECTED["calibration"],
        "v04_confirmatory_holdout_sha256": EXPECTED["holdout"],
        "frozen_weights": summary["frozen_weights"],
        "weather_decision": summary["weather_decision"],
        "canonical_ami_event_count": len(canonical),
        "canonical_ami_events_sha256": sha256(canonical_path),
        "source_workbook_sha256": workbook_hash,
        "source_workbook_tracked": False,
    }
    write_json(V05_REPORTS / "baseline_integrity.json", integrity)

    actual = load_actual_rows(workbook_path)
    walk_rows, causal_by_window, day_status = run_walkforward(actual)
    write_csv(V05_DATA / "causal_walkforward_results.csv", walk_rows)
    full_candidates = full_sample_candidates(actual)
    comparison = {}
    for window in WINDOWS:
        candidate_rows = causal_by_window[window]
        covered, event_map = coverage(candidate_rows, canonical)
        comparison[window] = {
            "candidate_count": len(candidate_rows),
            "evaluable_meter_days": day_status["evaluable_days"].get(window, 0),
            "warmup_meter_days": day_status["warmup_days"].get(window, 0),
            "candidate_density_per_meter_day": len(candidate_rows) / day_status["evaluable_days"].get(window, 1),
            "canonical_event_replay_coverage": covered / len(canonical),
            "canonical_event_covered_count": covered,
            "canonical_event_map": event_map,
            "full_sample_candidate_jaccard": candidate_jaccard(candidate_rows, full_candidates),
        }
    full_covered, full_event_map = coverage(full_candidates, canonical)
    comparison["full_sample"] = {
        "candidate_count": len(full_candidates),
        "canonical_event_replay_coverage": full_covered / len(canonical),
        "canonical_event_covered_count": full_covered,
        "canonical_event_map": full_event_map,
        "leakage_status": "uses future observations for historical baselines",
    }
    write_json(V05_DATA / "causal_walkforward_summary.json", comparison)

    temporal_rows, meter_profiles = temporal_profiles(actual, causal_by_window["30d"], canonical)
    write_csv(V05_REPORTS / "temporal_stability.csv", temporal_rows)
    write_json(V05_DATA / "temporal_meter_profiles.json", meter_profiles)
    summary_lines = [
        "# LightGuard v0.5 Causal Walk-Forward Summary", "",
        "Actual anonymized AMI contains no confirmed fault labels. Coverage below refers only to six known detector candidates, not field recall or accuracy.", "",
        "- Meters: B-L-9, B-L-12, B-L-13, B-L-14, B-L-35",
        "- Evaluation range: 2026-04-01 through 2026-06-30",
        "- Causal baseline rule: every baseline row has timestamp earlier than the evaluation day.",
        "- Warm-up policy: no baseline is fabricated; unavailable days are marked `not_evaluable_warmup`.",
        "- Existing detector comparison: full-sample medians include future observations and are retained only as a leakage-marked comparison.", "",
        "| baseline | candidates | evaluable meter-days | warm-up meter-days | density | canonical-6 coverage | full-sample Jaccard |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for window in WINDOWS:
        row = comparison[window]
        summary_lines.append(
            f"| {window} | {row['candidate_count']} | {row['evaluable_meter_days']} | {row['warmup_meter_days']} | "
            f"{row['candidate_density_per_meter_day']:.6f} | {row['canonical_event_replay_coverage']:.6f} | {row['full_sample_candidate_jaccard']:.6f} |"
        )
    summary_lines += ["", f"Full-sample comparison produced {len(full_candidates)} candidates and covered {full_covered}/6 known detector candidates."]
    (V05_REPORTS / "causal_walkforward_summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    meter_lines = [
        "# LightGuard v0.5 Meter Generalization Audit", "",
        "These are descriptive meter/data-quality profiles, not meter fault rates.", "",
        "| meter | cadence | measured phases | energy availability | duplicate timestamps | 24:00 normalized | canonical candidates |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for meter in TARGET_METERS:
        profile = meter_profiles[meter]
        meter_lines.append(
            f"| {meter} | {profile['sampling_interval_min']} min | {profile['measured_phase_count']} | "
            f"{profile['energy_availability']:.6f} | {profile['duplicate_timestamp_count']} | "
            f"{profile['hour24_normalization_count']} | {profile['canonical_candidate_count']} |"
        )
    meter_lines += [
        "", "## Guardrails", "",
        "- B-L-12's persistent daytime structure is handled by a meter-specific OFF baseline, never a global current threshold.",
        "- B-L-13 and B-L-35 have one measured current phase and sparse energy cadence; absent phases remain missing rather than zero.",
        "- Monthly drift and candidate density are descriptive operational signals only.",
    ]
    (V05_REPORTS / "meter_generalization.md").write_text("\n".join(meter_lines) + "\n", encoding="utf-8")
    print(json.dumps({"workbook_rows": sum(len(rows) for rows in actual.values()),
                      "full_sample_candidates": len(full_candidates), "comparison": comparison}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
