#!/usr/bin/env python3
"""Build Route-C proxy anomaly-sign artifacts from raw AMI currents only.

The implementation intentionally does not import H1, solar, weather, asset,
scenario, or prior detector code.  It freezes April-only parameters before
writing any May-June score, seals that score file, and only then reads the six
canonical rows for descriptive joins and deterministic controls.
"""

from __future__ import annotations

import csv
import glob
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import median

import openpyxl


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v11"
REPORTS = ROOT / "lightguard_v0_1/reports/v11"
APP_SUMMARY = ROOT / "lightguard_app/assets/data/context/v11_proxy_detector_summary.json"
CANONICAL_SIX = ROOT / "lightguard_app/assets/data/ami_events.csv"
V10_FREEZE = DATA / "v10_freeze_manifest.json"

TARGET_METERS = ("B-L-9", "B-L-12", "B-L-13", "B-L-14", "B-L-35")
RAW_SHA256 = "c18b49022d1c7dee2117a8d65a07d71351fb1aea8538751b7032867e4081b7d0"
V10_RELEASE = "d34d8323b3742c9116060d9548bd29c18750cb1f"
CAL_START, CAL_END = date(2026, 4, 1), date(2026, 4, 30)
SCORE_START, SCORE_END = date(2026, 5, 1), date(2026, 6, 30)
BOOTSTRAP_SEED, BOOTSTRAP_REPLICATES = 202611, 2000
CONTROL_NAMESPACE = "lightguard.v11.control.202611"
BLIND_NAMESPACE = "lightguard.v11.blind.202611"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def quantile(values: list[float], probability: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    low, high = math.floor(position), math.ceil(position)
    if low == high:
        return float(ordered[low])
    return float(ordered[low] + (ordered[high] - ordered[low]) * (position - low))


def mad_scale(values: list[float], center: float) -> float:
    deviations = [abs(value - center) for value in values]
    return max(0.05, 1.4826 * median(deviations))


def slot_of(timestamp: datetime) -> int:
    return timestamp.hour * 4 + timestamp.minute // 15


def parse_time(value: object) -> tuple[datetime, date]:
    text = str(value).strip()
    if text.endswith(" 24:00"):
        base = datetime.fromisoformat(text[:-5] + "00:00")
        return base + timedelta(days=1), base.date()
    parsed = datetime.fromisoformat(text)
    return parsed, parsed.date()


def number(value: object) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    return float(value)


def source_path() -> Path:
    matches = [Path(item) for item in glob.glob(str(ROOT / "official_docs/AMI Data Sample/*B*★.xlsx"))]
    if len(matches) != 1:
        raise RuntimeError(f"BLOCKED_NO_FULL_AMI: expected one B-line workbook, found {len(matches)}")
    if sha256_file(matches[0]) != RAW_SHA256:
        raise RuntimeError("BLOCKED_RAW_SOURCE_HASH_CHANGED")
    return matches[0]


def assert_v10_is_preserved() -> None:
    manifest = json.loads(V10_FREEZE.read_text(encoding="utf-8"))
    if manifest.get("v10_release_commit") != V10_RELEASE or manifest.get("frozen_h1_modified"):
        raise RuntimeError("BLOCKED_V10_FREEZE_NOT_PRESERVED")
    for item in manifest.get("files", []):
        path = ROOT / item["path"]
        if not path.exists() or sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"BLOCKED_V10_FROZEN_FILE_CHANGED: {item['path']}")


def load_raw_currents() -> list[dict]:
    workbook = openpyxl.load_workbook(source_path(), read_only=True, data_only=True)
    sheet = workbook["B선로 AMI DATA"]
    rows = []
    for source_row, values in enumerate(sheet.iter_rows(min_row=3, values_only=True), start=3):
        meter_id = str(values[0]).strip() if values and values[0] is not None else ""
        if meter_id not in TARGET_METERS or values[1] is None:
            continue
        timestamp, logical_date = parse_time(values[1])
        if not CAL_START <= logical_date <= SCORE_END:
            continue
        currents = [number(values[index]) for index in (13, 14, 15)]
        observed = [current for current in currents if current is not None]
        if not observed:
            continue
        sample_id = canonical_sha({
            "meter_id": meter_id,
            "source_row": source_row,
            "source_timestamp": str(values[1]),
            "current_presence": [current is not None for current in currents],
        })[:24]
        rows.append({
            "sample_id": sample_id,
            "meter_id": meter_id,
            "timestamp": timestamp,
            "logical_date": logical_date,
            "slot": slot_of(timestamp),
            "currents": currents,
            "total_current": sum(observed),
            "phase_count": len(observed),
        })
    workbook.close()
    return sorted(rows, key=lambda row: (row["meter_id"], row["timestamp"], row["sample_id"]))


def per_slot_profiles(
    calibration: list[dict],
    value_fn,
    required_meters: tuple[str, ...] = TARGET_METERS,
) -> dict[str, dict[str, dict[str, float | int]]]:
    grouped: dict[str, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    global_values: dict[str, list[float]] = defaultdict(list)
    for row in calibration:
        value = value_fn(row)
        if value is None:
            continue
        grouped[row["meter_id"]][row["slot"]].append(value)
        global_values[row["meter_id"]].append(value)
    profiles: dict[str, dict[str, dict[str, float | int]]] = {}
    for meter_id in required_meters:
        fallback_values = global_values[meter_id]
        if not fallback_values:
            raise RuntimeError(f"BLOCKED_NO_CALIBRATION_CURRENT: {meter_id}")
        fallback_center = median(fallback_values)
        fallback_scale = mad_scale(fallback_values, fallback_center)
        profiles[meter_id] = {}
        for slot in range(96):
            values = grouped[meter_id][slot] or fallback_values
            center = median(values)
            profiles[meter_id][str(slot)] = {
                "n": len(values),
                "center": round(center, 8),
                "scale": round(mad_scale(values, center), 8),
                "fallback_to_meter": int(not grouped[meter_id][slot]),
                "meter_fallback_center": round(fallback_center, 8),
                "meter_fallback_scale": round(fallback_scale, 8),
            }
    return profiles


def robust_z(row: dict, profiles: dict[str, dict[str, dict[str, float | int]]]) -> float:
    profile = profiles[row["meter_id"]][str(row["slot"])]
    return (row["total_current"] - float(profile["center"])) / float(profile["scale"])


def phase_score(row: dict, phase_profiles: dict[str, dict[str, dict[str, dict[str, float | int]]]]) -> float | None:
    if row["phase_count"] != 3 or row["total_current"] <= 0:
        return None
    profile = phase_profiles[row["meter_id"]][str(row["slot"])]
    fractions = [current / row["total_current"] for current in row["currents"]]
    return max(
        abs((fraction - float(profile[str(index)]["center"])) / float(profile[str(index)]["scale"]))
        for index, fraction in enumerate(fractions, start=1)
    )


def build_phase_profiles(calibration: list[dict]) -> dict[str, dict[str, dict[str, dict[str, float | int]]]]:
    phase_rows = [row for row in calibration if row["phase_count"] == 3 and row["total_current"] > 0]
    three_phase_meters = tuple(sorted({row["meter_id"] for row in phase_rows}))
    result: dict[str, dict[str, dict[str, dict[str, float | int]]]] = {}
    for phase_index in range(3):
        profiles = per_slot_profiles(
            phase_rows,
            lambda row, index=phase_index: row["currents"][index] / row["total_current"],
            required_meters=three_phase_meters,
        )
        for meter_id, slots in profiles.items():
            result.setdefault(meter_id, {})
            for slot, profile in slots.items():
                result[meter_id].setdefault(slot, {})[str(phase_index + 1)] = profile
    return result


def freeze_detectors(calibration: list[dict]) -> dict:
    residual_profiles = per_slot_profiles(calibration, lambda row: row["total_current"])
    d1_scores = [abs(robust_z(row, residual_profiles)) for row in calibration]
    phase_profiles = build_phase_profiles(calibration)
    d3_scores = [score for row in calibration if (score := phase_score(row, phase_profiles)) is not None]

    d2_by_meter: dict[str, list[float]] = defaultdict(list)
    d2_end_state: dict[str, dict[str, float]] = {}
    for meter_id in TARGET_METERS:
        state = {"ewma": 0.0, "cusum": 0.0}
        for row in (item for item in calibration if item["meter_id"] == meter_id):
            innovation = max(0.0, abs(robust_z(row, residual_profiles)) - 1.0)
            state["ewma"] = 0.25 * innovation + 0.75 * state["ewma"]
            state["cusum"] = max(0.0, 0.90 * state["cusum"] + innovation - 0.25)
            d2_by_meter[meter_id].append(max(state.values()))
        d2_end_state[meter_id] = {key: round(value, 8) for key, value in state.items()}

    return {
        "schema_version": "lightguard.v11.proxy-detector-freeze.1",
        "route": "C",
        "raw_source_sha256": RAW_SHA256,
        "v10_release_commit_preserved": V10_RELEASE,
        "calibration_window": {"start": CAL_START.isoformat(), "end": CAL_END.isoformat()},
        "scoring_window": {"start": SCORE_START.isoformat(), "end": SCORE_END.isoformat()},
        "input_boundary": "raw i1/i2/i3 only; no H1, context, asset, scenario, prior score, or outcome input",
        "D1_P1_robust_meter_local_time_slot_residual": {
            "score": "absolute((sum available phase currents - April meter-slot median) / robust MAD scale)",
            "threshold": round(max(4.0, quantile(d1_scores, 0.995)), 8),
            "slot_profiles": residual_profiles,
        },
        "D2_P2_causal_ewma_cusum_persistence": {
            "score": "max(EWMA, decayed CUSUM) of same-sample robust residual innovation; state updates after score",
            "ewma_alpha": 0.25,
            "cusum_decay": 0.90,
            "cusum_reference": 0.25,
            "innovation_deadband": 1.0,
            "threshold_by_meter": {meter: round(max(4.0, quantile(values, 0.995)), 8) for meter, values in d2_by_meter.items()},
            "state_at_calibration_end": d2_end_state,
        },
        "D3_P3_phase_pattern": {
            "score": "maximum absolute robust deviation of i1/i2/i3 current shares from April meter-slot baseline",
            "threshold": round(max(4.0, quantile(d3_scores, 0.995)), 8) if d3_scores else None,
            "not_applicable": "rows without all three observed phase currents",
            "slot_profiles": phase_profiles,
        },
        "calibration_counts": {
            "all_current_rows": len(calibration),
            "three_phase_rows": len(d3_scores),
        },
    }


def score_rows(scoring: list[dict], freeze: dict) -> list[dict]:
    d1 = freeze["D1_P1_robust_meter_local_time_slot_residual"]
    d2 = freeze["D2_P2_causal_ewma_cusum_persistence"]
    d3 = freeze["D3_P3_phase_pattern"]
    states = {meter: dict(values) for meter, values in d2["state_at_calibration_end"].items()}
    output = []
    for row in scoring:
        z = robust_z(row, d1["slot_profiles"])
        d1_score = abs(z)
        state = states[row["meter_id"]]
        innovation = max(0.0, d1_score - float(d2["innovation_deadband"]))
        d2_score = max(float(state["ewma"]), float(state["cusum"]))
        # The decision sees only April state and earlier score-window observations.
        d2_flag = d2_score >= float(d2["threshold_by_meter"][row["meter_id"]])
        state["ewma"] = float(d2["ewma_alpha"]) * innovation + (1.0 - float(d2["ewma_alpha"])) * float(state["ewma"])
        state["cusum"] = max(0.0, float(d2["cusum_decay"]) * float(state["cusum"]) + innovation - float(d2["cusum_reference"]))
        d3_score = phase_score(row, d3["slot_profiles"])
        output.append({
            "sample_id": row["sample_id"],
            "meter_id": row["meter_id"],
            "timestamp": row["timestamp"].isoformat(sep=" "),
            "logical_date": row["logical_date"].isoformat(),
            "month": row["logical_date"].strftime("%Y-%m"),
            "time_slot": row["slot"],
            "phase_count": row["phase_count"],
            "d1_residual_score": round(d1_score, 8),
            "d1_proxy_signal": int(d1_score >= float(d1["threshold"])),
            "d2_persistence_score": round(d2_score, 8),
            "d2_proxy_signal": int(d2_flag),
            "d3_phase_score": "NA" if d3_score is None else round(d3_score, 8),
            "d3_proxy_signal": "NA" if d3_score is None else int(d3_score >= float(d3["threshold"])),
        })
    return output


SCORE_FIELDS = [
    "sample_id", "meter_id", "timestamp", "logical_date", "month", "time_slot", "phase_count",
    "d1_residual_score", "d1_proxy_signal", "d2_persistence_score", "d2_proxy_signal",
    "d3_phase_score", "d3_proxy_signal",
]


def read_canonical_six() -> list[dict]:
    with CANONICAL_SIX.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 6:
        raise RuntimeError(f"BLOCKED_CANONICAL_SIX_COUNT: expected 6, found {len(rows)}")
    for row in rows:
        row["start"] = datetime.fromisoformat(row["first_sample"])
        row["end"] = datetime.fromisoformat(row["last_sample"])
    return rows


def canonical_join(scores: list[dict], score_sha: str) -> list[dict]:
    joined = []
    for event in read_canonical_six():
        rows = [row for row in scores if row["meter_id"] == event["meter_id"] and event["start"] <= datetime.fromisoformat(row["timestamp"]) <= event["end"]]
        d3_values = [float(row["d3_phase_score"]) for row in rows if row["d3_phase_score"] != "NA"]
        joined.append({
            "event_id": event["event_id"],
            "meter_id": event["meter_id"],
            "window_start": event["first_sample"],
            "window_end": event["last_sample"],
            "score_rows": len(rows),
            "d1_proxy_signal_rows": sum(int(row["d1_proxy_signal"]) for row in rows),
            "d2_proxy_signal_rows": sum(int(row["d2_proxy_signal"]) for row in rows),
            "d3_proxy_signal_rows": sum(int(row["d3_proxy_signal"]) for row in rows if row["d3_proxy_signal"] != "NA"),
            "max_d1_residual_score": round(max([float(row["d1_residual_score"]) for row in rows], default=0.0), 8),
            "max_d2_persistence_score": round(max([float(row["d2_persistence_score"]) for row in rows], default=0.0), 8),
            "max_d3_phase_score": round(max(d3_values, default=0.0), 8) if d3_values else "NA",
            "score_sha256_sealed_before_join": score_sha,
            "interpretation": "proxy-sign descriptive join only; no outcome label is available",
        })
    return joined


def within_exclusion(timestamp: datetime, events: list[dict], meter_id: str) -> bool:
    for event in events:
        if event["meter_id"] == meter_id and event["start"] - timedelta(hours=4) <= timestamp <= event["end"] + timedelta(hours=4):
            return True
    return False


def matched_controls(scores: list[dict]) -> list[dict]:
    events = read_canonical_six()
    controls = []
    for event in events:
        anchor = min(
            (row for row in scores if row["meter_id"] == event["meter_id"] and event["start"] <= datetime.fromisoformat(row["timestamp"]) <= event["end"]),
            key=lambda row: abs((datetime.fromisoformat(row["timestamp"]) - event["start"]).total_seconds()),
            default=None,
        )
        if anchor is None:
            controls.append({"event_id": event["event_id"], "match_status": "NO_ANCHOR_SCORE"})
            continue
        candidates = [
            row for row in scores
            if row["meter_id"] == event["meter_id"]
            and row["month"] == anchor["month"]
            and row["time_slot"] == anchor["time_slot"]
            and row["logical_date"] != anchor["logical_date"]
            and not within_exclusion(datetime.fromisoformat(row["timestamp"]), events, row["meter_id"])
        ]
        selected = min(
            candidates,
            key=lambda row: hashlib.sha256(f"{CONTROL_NAMESPACE}|{event['event_id']}|{row['sample_id']}".encode()).hexdigest(),
            default=None,
        )
        record = {
            "event_id": event["event_id"],
            "meter_id": event["meter_id"],
            "match_month": anchor["month"],
            "match_time_slot": anchor["time_slot"],
            "candidate_count_before_selection": len(candidates),
            "selection_policy": "minimum fixed hash over meter/month/time-slot candidates after event-window exclusion; detector scores not used",
            "anchor_sample_id": anchor["sample_id"],
            "match_status": "MATCHED" if selected else "NO_ELIGIBLE_CONTROL",
        }
        if selected:
            for prefix, row in (("anchor", anchor), ("control", selected)):
                record[f"{prefix}_sample_id"] = row["sample_id"]
                record[f"{prefix}_d1_proxy_signal"] = row["d1_proxy_signal"]
                record[f"{prefix}_d2_proxy_signal"] = row["d2_proxy_signal"]
                record[f"{prefix}_d3_proxy_signal"] = row["d3_proxy_signal"]
        controls.append(record)
    return controls


def concordance(scores: list[dict]) -> list[dict]:
    flags = {
        "D1/P1 robust residual": [bool(row["d1_proxy_signal"]) for row in scores],
        "D2/P2 causal persistence": [bool(row["d2_proxy_signal"]) for row in scores],
        "D3/P3 phase pattern": [row["d3_proxy_signal"] != "NA" and bool(row["d3_proxy_signal"]) for row in scores],
    }
    eligible = {
        "D1/P1 robust residual": len(scores),
        "D2/P2 causal persistence": len(scores),
        "D3/P3 phase pattern": sum(row["d3_proxy_signal"] != "NA" for row in scores),
    }
    rows = []
    names = list(flags)
    for index, left in enumerate(names):
        for right in names[index + 1:]:
            intersection = sum(a and b for a, b in zip(flags[left], flags[right]))
            union = sum(a or b for a, b in zip(flags[left], flags[right]))
            rows.append({
                "left_proxy": left,
                "right_proxy": right,
                "score_rows": len(scores),
                "left_eligible_rows": eligible[left],
                "right_eligible_rows": eligible[right],
                "left_signal_rows": sum(flags[left]),
                "right_signal_rows": sum(flags[right]),
                "intersection_signal_rows": intersection,
                "union_signal_rows": union,
                "jaccard_proxy_overlap": round(intersection / union, 8) if union else "NA",
                "interpretation": "same-source proxy concordance, not independent corroboration",
            })
    return rows


def bootstrap(scores: list[dict]) -> dict:
    clusters: dict[tuple[str, str], Counter] = defaultdict(Counter)
    for row in scores:
        cluster = clusters[(row["meter_id"], row["logical_date"])]
        cluster["rows"] += 1
        cluster["d1"] += int(row["d1_proxy_signal"])
        cluster["d2"] += int(row["d2_proxy_signal"])
        if row["d3_proxy_signal"] != "NA":
            cluster["d3_eligible"] += 1
            cluster["d3"] += int(row["d3_proxy_signal"])
        cluster["d1_d2"] += int(bool(row["d1_proxy_signal"]) and bool(row["d2_proxy_signal"]))
    cluster_values = list(clusters.values())
    randomizer = random.Random(BOOTSTRAP_SEED)
    metrics: dict[str, list[float]] = defaultdict(list)
    for _ in range(BOOTSTRAP_REPLICATES):
        draw = [cluster_values[randomizer.randrange(len(cluster_values))] for _ in cluster_values]
        total = sum(item["rows"] for item in draw)
        phase_total = sum(item["d3_eligible"] for item in draw)
        metrics["D1/P1 proxy-signal share"].append(sum(item["d1"] for item in draw) / total)
        metrics["D2/P2 proxy-signal share"].append(sum(item["d2"] for item in draw) / total)
        metrics["D1/D2 joint proxy-signal share"].append(sum(item["d1_d2"] for item in draw) / total)
        if phase_total:
            metrics["D3/P3 proxy-signal share among 3P"].append(sum(item["d3"] for item in draw) / phase_total)
    return {
        "schema_version": "lightguard.v11.meter-day-cluster-bootstrap.1",
        "route": "C",
        "seed": BOOTSTRAP_SEED,
        "replicates": BOOTSTRAP_REPLICATES,
        "cluster_unit": "meter_id x logical_date",
        "cluster_count": len(cluster_values),
        "metric_intervals": {
            name: {"median": round(median(values), 8), "p2_5": round(quantile(values, 0.025), 8), "p97_5": round(quantile(values, 0.975), 8)}
            for name, values in metrics.items()
        },
        "claim_boundary": "descriptive uncertainty for proxy-signal shares only; not an outcome evaluation",
    }


def blind_packet(scores: list[dict]) -> tuple[list[dict], dict]:
    buckets: dict[str, list[dict]] = defaultdict(list)
    for row in scores:
        if row["d3_proxy_signal"] != "NA" and int(row["d3_proxy_signal"]):
            stratum = "S3_PHASE_PATTERN"
        elif int(row["d2_proxy_signal"]):
            stratum = "S2_PERSISTENCE"
        elif int(row["d1_proxy_signal"]):
            stratum = "S1_RESIDUAL"
        else:
            stratum = "S0_NO_PROXY"
        buckets[stratum].append(row)
    packet, key_rows, availability = [], [], {}
    for stratum in ("S0_NO_PROXY", "S1_RESIDUAL", "S2_PERSISTENCE", "S3_PHASE_PATTERN"):
        selected = sorted(
            buckets[stratum],
            key=lambda row: hashlib.sha256(f"{BLIND_NAMESPACE}|{stratum}|{row['sample_id']}".encode()).hexdigest(),
        )[:15]
        availability[stratum] = {"available": len(buckets[stratum]), "requested": 15, "selected": len(selected)}
        for index, row in enumerate(selected, start=1):
            blind_id = f"V11-{stratum[:2]}-{index:02d}"
            meter_blind_id = hashlib.sha256(f"{BLIND_NAMESPACE}|meter|{row['meter_id']}".encode()).hexdigest()[:12]
            packet.append({
                "blind_id": blind_id,
                "meter_blind_id": meter_blind_id,
                "logical_month": row["month"],
                "time_slot": row["time_slot"],
                "phase_count": row["phase_count"],
                "sample_token": hashlib.sha256(f"{BLIND_NAMESPACE}|sample|{row['sample_id']}".encode()).hexdigest()[:16],
            })
            key_rows.append({"blind_id": blind_id, "stratum": stratum, "sample_id": row["sample_id"], "meter_id": row["meter_id"], "timestamp": row["timestamp"]})
    return packet, {"schema_version": "lightguard.v11.blind-key.1", "route": "C", "availability": availability, "key_rows": key_rows}


def report_markdown(freeze_sha: str, score_sha: str, scores: list[dict], blind_key: dict) -> str:
    d3_eligible = sum(row["d3_proxy_signal"] != "NA" for row in scores)
    return f"""# v0.11 H1-Independent Proxy Detector Run

## Scope

- Route: `C`; full label audit sealed usable Gold=`0`, usable Silver=`0`.
- Input: raw B-line `i1/i2/i3` currents only.
- Excluded by design: H1, solar, weather, asset attributes, scenarios, prior detector output, and operational outcomes.
- Calibration: `2026-04-01` through `2026-04-30`.
- Scoring: `2026-05-01` through `2026-06-30`.
- v0.10 preservation reference: `{V10_RELEASE}`.

## Seal order

1. Freeze file SHA-256: `{freeze_sha}`.
2. Independent May-June score SHA-256: `{score_sha}`.
3. Only after step 2, join the six canonical rows and construct controls.

## Produced coverage

- Score rows: `{len(scores)}`.
- Three-phase eligible score rows: `{d3_eligible}`.
- Bootstrap: `{BOOTSTRAP_REPLICATES}` meter-day cluster resamples with seed `{BOOTSTRAP_SEED}`.
- Blinded packet availability: `{json.dumps(blind_key['availability'], ensure_ascii=False)}`.

## Interpretation guard

Every output is a raw-current proxy anomaly-sign artifact. Detector overlap, matched-control contrast, and bootstrap intervals describe internal measurement behavior only. No field-outcome evaluation is available in this route.
"""


def main() -> None:
    assert_v10_is_preserved()
    raw_rows = load_raw_currents()
    calibration = [row for row in raw_rows if CAL_START <= row["logical_date"] <= CAL_END]
    scoring = [row for row in raw_rows if SCORE_START <= row["logical_date"] <= SCORE_END]
    if not calibration or not scoring:
        raise RuntimeError("BLOCKED_REQUIRED_TIME_WINDOW_EMPTY")

    freeze = freeze_detectors(calibration)
    freeze_path = DATA / "v11_proxy_detector_freeze.json"
    write_json(freeze_path, freeze)
    freeze_sha = sha256_file(freeze_path)

    scores = score_rows(scoring, freeze)
    score_path = DATA / "v11_proxy_scores_prejoin.csv"
    write_csv(score_path, scores, SCORE_FIELDS)
    score_sha = sha256_file(score_path)
    seal = {
        "schema_version": "lightguard.v11.proxy-score-seal.1",
        "route": "C",
        "score_path": score_path.relative_to(ROOT).as_posix(),
        "score_sha256": score_sha,
        "freeze_path": freeze_path.relative_to(ROOT).as_posix(),
        "freeze_sha256": freeze_sha,
        "sealed_before_canonical_join": True,
        "raw_source_sha256": RAW_SHA256,
    }
    write_json(DATA / "v11_proxy_score_seal.json", seal)

    canonical = canonical_join(scores, score_sha)
    write_csv(DATA / "v11_proxy_canonical_six.csv", canonical, list(canonical[0]))
    controls = matched_controls(scores)
    control_fields = sorted({field for row in controls for field in row})
    write_csv(DATA / "v11_proxy_matched_controls.csv", controls, control_fields)
    pairs = concordance(scores)
    write_csv(REPORTS / "v11_proxy_concordance.csv", pairs, list(pairs[0]))
    bootstrap_result = bootstrap(scores)
    write_json(REPORTS / "v11_proxy_meter_day_bootstrap.json", bootstrap_result)
    packet, blind_key = blind_packet(scores)
    write_json(DATA / "v11_proxy_artifact_manifest.json", {
        "schema_version": "lightguard.v11.proxy-artifact-manifest.1",
        "route": "C",
        "raw_source_sha256": RAW_SHA256,
        "v10_release_commit_preserved": V10_RELEASE,
        "artifacts": {path.relative_to(ROOT).as_posix(): sha256_file(path) for path in [freeze_path, score_path, DATA / "v11_proxy_score_seal.json", DATA / "v11_proxy_canonical_six.csv", DATA / "v11_proxy_matched_controls.csv", REPORTS / "v11_proxy_concordance.csv", REPORTS / "v11_proxy_meter_day_bootstrap.json"]},
    })
    write_json(APP_SUMMARY, {
        "schema_version": "lightguard.v11.proxy-detector-app-summary.1",
        "route": "C",
        "title": "Raw-current proxy anomaly signs",
        "claim_guard": "Proxy anomaly signs only. No field-outcome labels are available for this data slice.",
        "calibration_window": freeze["calibration_window"],
        "scoring_window": freeze["scoring_window"],
        "score_sha256": score_sha,
        "freeze_sha256": freeze_sha,
        "score_rows": len(scores),
        "three_phase_eligible_rows": sum(row["d3_proxy_signal"] != "NA" for row in scores),
        "detectors": ["D1/P1 robust meter-local time-slot residual", "D2/P2 causal EWMA/CUSUM persistence", "D3/P3 phase pattern (1P N/A)"],
        "canonical_rows_joined_after_score_seal": len(canonical),
        "control_selection": "deterministic meter/time/month match independent of detector scores",
        "blind_packet_availability": blind_key["availability"],
    })
    (REPORTS / "v11_proxy_detector_summary.md").write_text(report_markdown(freeze_sha, score_sha, scores, blind_key), encoding="utf-8")


if __name__ == "__main__":
    main()
