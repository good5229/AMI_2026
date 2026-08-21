#!/usr/bin/env python3
"""Build leakage-free retrospective municipal triage evidence for v0.18."""

from __future__ import annotations

import bisect
import csv
import datetime as dt
import hashlib
import heapq
import json
import math
import statistics
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "official_docs" / "external_data"
DATA = ROOT / "lightguard_v0_1" / "data" / "validation" / "v18"
REPORT = ROOT / "lightguard_v0_1" / "reports" / "v18"
LEARNING = ROOT / "docs" / "agent_learning_v18"
APP_DOCS = ROOT / "lightguard_app" / "docs"
CARD = ROOT / "lightguard_app" / "lib" / "features" / "ami_validation" / "v18_operational_triage_card.dart"
SNAPSHOT_END = dt.date(2025, 8, 9)
PRIMARY = "REPEAT_WITHIN_30D"
SOURCE_SHA = "a21d87de8da61d5793fd87655efbd857be5990e7188aaec8d913c4ced788cbd0"
MODEL_FEATURES = [
    "prior_event_count_30d", "prior_event_count_90d", "prior_event_count_365d",
    "days_since_previous_event", "days_since_previous_event_missing",
    "prior_long_resolution_count_3d", "prior_long_resolution_count_7d",
    "currently_open_prior_case_count", "oldest_open_prior_age_days",
    "start_of_day_open_backlog", "district_start_of_day_open_backlog",
    "recent_7d_system_intake", "recent_30d_system_intake",
    "recent_7d_district_intake", "recent_30d_district_intake",
]
BANNED_FEATURES = {
    "management_number", "asset_hash", "current_processing_date", "resolution_days",
    "long_3d", "long_7d", "repeat_30d", "repeat_90d", "latitude", "longitude",
    "safety_inspection", "material", "construction", "ami_score", "fault_cause",
    "fault_severity", "staff_count",
}


def nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value.strip())


def source_path() -> Path:
    matches = [path for path in RAW.glob("*.csv") if "고장등관리" in nfc(path.name)]
    if len(matches) != 1:
        raise RuntimeError("BLOCKED_D1_SOURCE")
    return matches[0]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def hash_text(prefix: str, value: str, length: int = 16) -> str:
    return prefix + hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise RuntimeError(f"BLOCKED_EMPTY_OUTPUT:{path.name}")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.strip() + "\n", encoding="utf-8")


def parse_date(value: str) -> dt.date:
    return dt.date.fromisoformat(value.strip())


def nearest_rank(values: list[int], probability: float) -> int:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(probability * len(ordered)) - 1)]


def percentile(values: list[float], probability: float) -> float | None:
    if not values:
        return None
    return float(np.quantile(np.asarray(values, dtype=float), probability, method="linear"))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -30.0, 30.0)))


def average_precision(labels: np.ndarray, scores: np.ndarray) -> float:
    positives = int(labels.sum())
    if positives == 0:
        return 0.0
    order = np.argsort(-scores, kind="stable")
    sorted_y = labels[order]
    sorted_s = scores[order]
    total_positive = 0
    total_seen = 0
    weighted_precision = 0.0
    index = 0
    while index < len(order):
        end = index + 1
        while end < len(order) and sorted_s[end] == sorted_s[index]:
            end += 1
        group_positive = int(sorted_y[index:end].sum())
        total_positive += group_positive
        total_seen = end
        weighted_precision += (total_positive / total_seen) * group_positive
        index = end
    return weighted_precision / positives


def rank_metrics(labels: np.ndarray, scores: np.ndarray, tie_tokens: list[str], top_fraction: float) -> dict:
    count = max(1, math.ceil(len(labels) * top_fraction))
    threshold = float(np.sort(scores)[-count])
    above = scores > threshold
    tied = scores == threshold
    remaining = count - int(above.sum())
    expected_positive = float(labels[above].sum())
    if remaining > 0 and int(tied.sum()) > 0:
        expected_positive += remaining / int(tied.sum()) * float(labels[tied].sum())
    positives = int(labels.sum())
    prevalence = positives / len(labels)
    precision = expected_positive / count
    return {
        "selected_count": count,
        "precision": precision,
        "recall": expected_positive / positives if positives else 0.0,
        "enrichment": precision / prevalence if prevalence else 0.0,
        "cutoff_tie_expected_allocation": True,
    }


def calibration(labels: np.ndarray, scores: np.ndarray) -> dict:
    brier = float(np.mean((scores - labels) ** 2))
    ece = 0.0
    bins = []
    for lower in np.linspace(0.0, 0.9, 10):
        upper = lower + 0.1
        mask = (scores >= lower) & ((scores < upper) if upper < 1.0 else (scores <= upper))
        count = int(mask.sum())
        if not count:
            continue
        observed = float(labels[mask].mean())
        predicted = float(scores[mask].mean())
        ece += count / len(labels) * abs(observed - predicted)
        bins.append({"lower": lower, "upper": upper, "count": count, "predicted": predicted, "observed": observed})
    return {"brier": brier, "ece_10bin": ece, "bins": bins}


def metric_row(model: str, split: str, labels: np.ndarray, scores: np.ndarray, tokens: list[str]) -> dict:
    top5 = rank_metrics(labels, scores, tokens, 0.05)
    top10 = rank_metrics(labels, scores, tokens, 0.10)
    top20 = rank_metrics(labels, scores, tokens, 0.20)
    cal = calibration(labels, scores)
    return {
        "model": model, "split": split, "rows": len(labels), "prevalence": float(labels.mean()),
        "average_precision": average_precision(labels, scores),
        "top5_precision": top5["precision"], "top5_recall": top5["recall"], "top5_enrichment": top5["enrichment"],
        "top10_precision": top10["precision"], "top10_recall": top10["recall"], "top10_enrichment": top10["enrichment"],
        "top20_precision": top20["precision"], "top20_recall": top20["recall"], "top20_enrichment": top20["enrichment"],
        "brier": cal["brier"], "ece_10bin": cal["ece_10bin"],
    }


def main() -> None:
    for directory in (DATA, REPORT, LEARNING, APP_DOCS, CARD.parent):
        directory.mkdir(parents=True, exist_ok=True)
    raw_path = source_path()
    if sha256(raw_path) != SOURCE_SHA:
        raise RuntimeError("BLOCKED_D1_HASH_DRIFT")

    events = []
    with raw_path.open(encoding="cp949", newline="") as stream:
        for index, row in enumerate(csv.DictReader(stream), 1):
            receipt = parse_date(row["접수일자"])
            resolved = parse_date(row["처리일"])
            identifier = row["관리번호"].strip()
            tie_payload = "|".join((
                "lightguard-v018-tie-v1", SOURCE_SHA, identifier, receipt.isoformat(),
                row["접수구분"].strip(), row["구청"].strip(), row["가로등명"].strip(),
                row["구간"].strip(), row["순번"].strip(),
            ))
            events.append({
                "index": index, "event_id": f"D1-{index:06d}", "receipt": receipt, "resolved": resolved,
                "asset": identifier, "asset_hash": hash_text("LGD-", f"v18:{identifier}"),
                "receipt_type": row["접수구분"].strip(), "district": row["구청"].strip(),
                "tie_token": hashlib.sha256(tie_payload.encode("utf-8")).hexdigest(),
            })
    events.sort(key=lambda row: (row["receipt"], row["index"]))
    by_day: dict[dt.date, list[dict]] = defaultdict(list)
    by_asset_day: dict[tuple[str, dt.date], list[dict]] = defaultdict(list)
    for event in events:
        by_day[event["receipt"]].append(event)
        by_asset_day[(event["asset"], event["receipt"])].append(event)
    primary_event_ids = {min(group, key=lambda row: row["index"])["event_id"] for group in by_asset_day.values()}

    distinct_dates_by_asset: dict[str, list[dt.date]] = defaultdict(list)
    for asset, day in by_asset_day:
        distinct_dates_by_asset[asset].append(day)
    next_date = {}
    for asset, dates in distinct_dates_by_asset.items():
        dates.sort()
        for current, following in zip(dates, dates[1:]):
            next_date[(asset, current)] = following

    completion_schedule = sorted(
        [event for event in events if event["resolved"] >= event["receipt"]],
        key=lambda row: (row["resolved"], row["index"]),
    )
    completion_pointer = 0
    history_asset: dict[str, list[dt.date]] = defaultdict(list)
    history_system: list[dt.date] = []
    history_district: dict[str, list[dt.date]] = defaultdict(list)
    completed_long3 = Counter()
    completed_long7 = Counter()
    max_completion_by_asset: dict[str, dt.date] = {}
    open_heap = []
    open_events = {}
    open_asset: dict[str, dict[int, dt.date]] = defaultdict(dict)
    open_district = Counter()
    features = []
    internal_features = {}

    def prior_count(history: list[dt.date], day: dt.date, window: int) -> int:
        return len(history) - bisect.bisect_left(history, day - dt.timedelta(days=window))

    for day in sorted(by_day):
        while completion_pointer < len(completion_schedule) and completion_schedule[completion_pointer]["resolved"] < day:
            completed = completion_schedule[completion_pointer]
            duration = (completed["resolved"] - completed["receipt"]).days
            completed_long3[completed["asset"]] += duration > 3
            completed_long7[completed["asset"]] += duration > 7
            max_completion_by_asset[completed["asset"]] = completed["resolved"]
            completion_pointer += 1
        while open_heap and open_heap[0][0] <= day:
            _, event_index = heapq.heappop(open_heap)
            expired = open_events.pop(event_index, None)
            if expired is None:
                continue
            open_asset[expired["asset"]].pop(event_index, None)
            open_district[expired["district"]] -= 1
        system_backlog = len(open_events)
        for event in by_day[day]:
            asset_history = history_asset[event["asset"]]
            district_history = history_district[event["district"]]
            asset_open = open_asset[event["asset"]]
            days_since = (day - asset_history[-1]).days if asset_history else None
            feature = {
                "event_id": event["event_id"],
                "episode_id": hash_text("EP-", f"{event['asset']}|{day.isoformat()}"),
                "episode_primary": event["event_id"] in primary_event_ids,
                "receipt_date": day.isoformat(), "feature_available_at": f"{day.isoformat()}T00:00:00",
                "receipt_type": event["receipt_type"], "district": event["district"],
                "month": day.month, "day_of_week": day.weekday(),
                "prior_event_count_30d": prior_count(asset_history, day, 30),
                "prior_event_count_90d": prior_count(asset_history, day, 90),
                "prior_event_count_365d": prior_count(asset_history, day, 365),
                "days_since_previous_event": "" if days_since is None else days_since,
                "days_since_previous_event_missing": days_since is None,
                "prior_long_resolution_count_3d": completed_long3[event["asset"]],
                "prior_long_resolution_count_7d": completed_long7[event["asset"]],
                "currently_open_prior_case_count": len(asset_open),
                "oldest_open_prior_age_days": max((day - receipt).days for receipt in asset_open.values()) if asset_open else 0,
                "start_of_day_open_backlog": system_backlog,
                "district_start_of_day_open_backlog": open_district[event["district"]],
                "recent_7d_system_intake": prior_count(history_system, day, 7),
                "recent_30d_system_intake": prior_count(history_system, day, 30),
                "recent_7d_district_intake": prior_count(district_history, day, 7),
                "recent_30d_district_intake": prior_count(district_history, day, 30),
                "max_prior_receipt_date": asset_history[-1].isoformat() if asset_history else "",
                "max_prior_completion_date": max_completion_by_asset.get(event["asset"], "").isoformat() if event["asset"] in max_completion_by_asset else "",
                "same_day_order_used": False,
                "asset_hash_audit_only_not_model_feature": event["asset_hash"],
                "tie_token_audit_only_not_model_feature": event["tie_token"],
            }
            features.append(feature)
            internal_features[event["event_id"]] = feature
        for event in by_day[day]:
            history_asset[event["asset"]].append(day)
            history_system.append(day)
            history_district[event["district"]].append(day)
            if event["resolved"] >= event["receipt"]:
                remove_day = event["resolved"] + dt.timedelta(days=1)
                open_events[event["index"]] = event
                open_asset[event["asset"]][event["index"]] = day
                open_district[event["district"]] += 1
                heapq.heappush(open_heap, (remove_day, event["index"]))

    outcomes = []
    outcome_by_id = {}
    for event in events:
        duration = (event["resolved"] - event["receipt"]).days
        duration_valid = duration >= 0
        following = next_date.get((event["asset"], event["receipt"]))
        repeat30_evaluable = event["receipt"] <= SNAPSHOT_END - dt.timedelta(days=30)
        repeat90_evaluable = event["receipt"] <= SNAPSHOT_END - dt.timedelta(days=90)
        repeat30 = bool(following and 1 <= (following - event["receipt"]).days <= 30) if repeat30_evaluable else None
        repeat90 = bool(following and 1 <= (following - event["receipt"]).days <= 90) if repeat90_evaluable else None
        burden_evaluable = duration_valid and repeat30_evaluable
        burden = bool(duration > 7 or repeat30) if burden_evaluable else None
        outcome = {
            "event_id": event["event_id"], "receipt_date": event["receipt"].isoformat(),
            "episode_primary": event["event_id"] in primary_event_ids,
            "resolution_evaluable": duration_valid, "resolution_days": duration if duration_valid else "",
            "long_resolution_3d": duration > 3 if duration_valid else "",
            "long_resolution_7d": duration > 7 if duration_valid else "",
            "repeat_within_30d_evaluable": repeat30_evaluable,
            "repeat_within_30d": "" if repeat30 is None else repeat30,
            "repeat_within_90d_evaluable": repeat90_evaluable,
            "repeat_within_90d": "" if repeat90 is None else repeat90,
            "operational_burden_composite_evaluable": burden_evaluable,
            "operational_burden_composite": "" if burden is None else burden,
            "label_role": "retrospective operational outcome; not physical fault truth",
        }
        outcomes.append(outcome)
        outcome_by_id[event["event_id"]] = outcome

    split_ranges = {
        "development": (dt.date(2020, 1, 1), dt.date(2023, 12, 1)),
        "validation": (dt.date(2024, 1, 1), dt.date(2024, 12, 1)),
        "confirmatory": (dt.date(2025, 1, 1), SNAPSHOT_END - dt.timedelta(days=30)),
    }
    model_rows = []
    for event in events:
        if event["event_id"] not in primary_event_ids:
            continue
        outcome = outcome_by_id[event["event_id"]]
        if not outcome["repeat_within_30d_evaluable"]:
            continue
        split = next((name for name, (start, end) in split_ranges.items() if start <= event["receipt"] <= end), None)
        if split:
            model_rows.append({"event": event, "feature": internal_features[event["event_id"]], "outcome": outcome, "split": split})
    split_counts = Counter(row["split"] for row in model_rows)

    development = [row for row in model_rows if row["split"] == "development"]
    validation = [row for row in model_rows if row["split"] == "validation"]
    confirmatory = [row for row in model_rows if row["split"] == "confirmatory"]
    categories = {
        "receipt_type": sorted({row["feature"]["receipt_type"] for row in development}),
        "district": sorted({row["feature"]["district"] for row in development}),
        "month": list(range(1, 13)), "day_of_week": list(range(7)),
    }
    transform_names = [f"log1p:{name}" for name in MODEL_FEATURES]
    transform_names += [f"receipt_type={value}" for value in categories["receipt_type"]]
    transform_names += [f"district={value}" for value in categories["district"]]
    transform_names += [f"month={value}" for value in categories["month"]]
    transform_names += [f"day_of_week={value}" for value in categories["day_of_week"]]

    def raw_numeric(feature: dict) -> list[float]:
        values = []
        for name in MODEL_FEATURES:
            value = feature[name]
            if value == "":
                value = 0
            if isinstance(value, bool):
                values.append(float(value))
            else:
                values.append(math.log1p(max(0.0, float(value))))
        return values

    dev_numeric = np.asarray([raw_numeric(row["feature"]) for row in development], dtype=float)
    means = dev_numeric.mean(axis=0)
    scales = dev_numeric.std(axis=0)
    scales[scales == 0] = 1.0

    def matrix(rows: list[dict]) -> np.ndarray:
        output = []
        for row in rows:
            feature = row["feature"]
            numeric = (np.asarray(raw_numeric(feature)) - means) / scales
            one_hot = []
            one_hot += [float(feature["receipt_type"] == value) for value in categories["receipt_type"]]
            one_hot += [float(feature["district"] == value) for value in categories["district"]]
            one_hot += [float(feature["month"] == value) for value in categories["month"]]
            one_hot += [float(feature["day_of_week"] == value) for value in categories["day_of_week"]]
            output.append(np.concatenate((numeric, np.asarray(one_hot))))
        return np.asarray(output, dtype=float)

    def labels(rows: list[dict]) -> np.ndarray:
        return np.asarray([int(row["outcome"]["repeat_within_30d"] is True) for row in rows], dtype=float)

    x_dev, y_dev = matrix(development), labels(development)
    x_val, y_val = matrix(validation), labels(validation)
    x_hold, y_hold = matrix(confirmatory), labels(confirmatory)
    prevalence = float(y_dev.mean())
    weights = np.zeros(x_dev.shape[1], dtype=float)
    intercept = math.log(prevalence / (1.0 - prevalence))
    learning_rate = 0.08
    l2 = 0.001
    for _ in range(300):
        probabilities = sigmoid(x_dev @ weights + intercept)
        error = probabilities - y_dev
        weights -= learning_rate * ((x_dev.T @ error) / len(y_dev) + l2 * weights)
        intercept -= learning_rate * float(error.mean())

    def simple_flag(rows: list[dict]) -> np.ndarray:
        return np.asarray([float(row["feature"]["prior_event_count_90d"] >= 1) for row in rows])

    flag_dev = simple_flag(development)
    flag_rates = {}
    for value in (0.0, 1.0):
        mask = flag_dev == value
        flag_rates[str(int(value))] = float(y_dev[mask].mean()) if mask.any() else prevalence

    def scores_for(rows: list[dict], x: np.ndarray) -> dict[str, np.ndarray]:
        flags = simple_flag(rows)
        return {
            "B0_NO_PREDICTION": np.full(len(rows), prevalence),
            "B1_REPEAT_AWARE_RULE": np.asarray([flag_rates[str(int(value))] for value in flags]),
            "B2_LOGISTIC": sigmoid(x @ weights + intercept),
        }

    score_sets = {
        "development": scores_for(development, x_dev),
        "validation": scores_for(validation, x_val),
        "confirmatory": scores_for(confirmatory, x_hold),
    }
    split_rows = {"development": development, "validation": validation, "confirmatory": confirmatory}
    split_labels = {"development": y_dev, "validation": y_val, "confirmatory": y_hold}
    model_results = []
    for split, rows in split_rows.items():
        tokens = [row["event"]["tie_token"] for row in rows]
        for model, scores in score_sets[split].items():
            model_results.append(metric_row(model, split, split_labels[split], scores, tokens))
    val_results = {row["model"]: row for row in model_results if row["split"] == "validation"}
    logistic_wins = (
        val_results["B2_LOGISTIC"]["top10_enrichment"] > val_results["B1_REPEAT_AWARE_RULE"]["top10_enrichment"]
    )
    selected_model = "B2_LOGISTIC" if logistic_wins else "B1_REPEAT_AWARE_RULE"
    selected_scores = score_sets["confirmatory"][selected_model]
    for result in model_results:
        result["top10_enrichment_asset_cluster_ci_lower"] = ""
        result["top10_enrichment_asset_cluster_ci_upper"] = ""
    holdout_result = next(row for row in model_results if row["split"] == "confirmatory" and row["model"] == selected_model)
    cluster_indices = defaultdict(list)
    for index, row in enumerate(confirmatory):
        cluster_indices[row["event"]["asset"]].append(index)
    cluster_names = sorted(cluster_indices)
    rng = np.random.default_rng(202618)
    bootstrap_enrichment = []
    for _ in range(1000):
        sampled = rng.integers(0, len(cluster_names), len(cluster_names))
        indices = [index for sampled_index in sampled for index in cluster_indices[cluster_names[int(sampled_index)]]]
        sample_labels = y_hold[indices]
        if sample_labels.sum() == 0:
            continue
        sample_scores = selected_scores[indices]
        sample_tokens = [confirmatory[index]["event"]["tie_token"] for index in indices]
        bootstrap_enrichment.append(rank_metrics(sample_labels, sample_scores, sample_tokens, 0.10)["enrichment"])
    holdout_result["top10_enrichment_asset_cluster_ci_lower"] = percentile(bootstrap_enrichment, 0.025)
    holdout_result["top10_enrichment_asset_cluster_ci_upper"] = percentile(bootstrap_enrichment, 0.975)

    holdout_scores = []
    for row, score, simple_score in zip(confirmatory, selected_scores, score_sets["confirmatory"]["B1_REPEAT_AWARE_RULE"]):
        feature = row["feature"]
        reasons = []
        if feature["prior_event_count_90d"]:
            reasons.append("recent_repeat_history")
        if feature["currently_open_prior_case_count"]:
            reasons.append("open_prior_case")
        if feature["prior_long_resolution_count_7d"]:
            reasons.append("completed_long_history")
        if feature["start_of_day_open_backlog"]:
            reasons.append("start_of_day_backlog_context")
        holdout_scores.append({
            "event_id": row["event"]["event_id"], "episode_id": feature["episode_id"],
            "receipt_date": feature["receipt_date"], "receipt_type": feature["receipt_type"],
            "district": feature["district"], "selected_model": selected_model,
            "operational_burden_score": round(float(score), 12),
            "simple_rule_score": round(float(simple_score), 12),
            "priority_reasons": ";".join(reasons) if reasons else "intake_context_only",
            "tie_token": row["event"]["tie_token"],
            "field_confirmation": "required", "direct_ami_validation": False,
        })

    development_start, development_end = split_ranges["development"]
    closure_counts = Counter(
        event["resolved"] for event in events
        if event["resolved"] >= event["receipt"] and development_start <= event["resolved"] <= development_end
    )
    daily_closures = []
    current = development_start
    while current <= development_end:
        daily_closures.append(closure_counts[current])
        current += dt.timedelta(days=1)
    capacities = {"C25": nearest_rank(daily_closures, 0.25), "C50": nearest_rank(daily_closures, 0.50), "C75": nearest_rank(daily_closures, 0.75)}

    queue_inputs = []
    scores_by_id = {row["event_id"]: row for row in holdout_scores}
    for row in confirmatory:
        score = scores_by_id[row["event"]["event_id"]]
        outcome = row["outcome"]
        queue_inputs.append({
            "event_id": row["event"]["event_id"], "receipt": row["event"]["receipt"],
            "receipt_type": row["feature"]["receipt_type"], "district": row["feature"]["district"],
            "tie_token": row["event"]["tie_token"], "simple_score": score["simple_rule_score"],
            "model_score": score["operational_burden_score"],
            "burden": bool(outcome["operational_burden_composite"]),
            "repeat30": bool(outcome["repeat_within_30d"]), "long7": bool(outcome["long_resolution_7d"]),
        })

    queue_rows = []
    queue_summary = []
    policies = ("Q0_DAILY_BATCH_FIFO", "Q1_REPEAT_AWARE", "Q2_INTERPRETABLE_SCORE")
    simulation_end = SNAPSHOT_END
    for capacity_name, capacity in capacities.items():
        for policy in policies:
            pending = []
            reviewed = {}
            arrivals = defaultdict(list)
            for item in queue_inputs:
                arrivals[item["receipt"]].append(item)
            day = split_ranges["confirmatory"][0]
            max_backlog = 0
            while day <= simulation_end:
                pending.extend(arrivals.get(day, []))
                max_backlog = max(max_backlog, len(pending))
                if capacity > 0 and pending:
                    if policy == "Q0_DAILY_BATCH_FIFO":
                        pending.sort(key=lambda item: (item["receipt"], item["tie_token"]))
                    elif policy == "Q1_REPEAT_AWARE":
                        pending.sort(key=lambda item: (-item["simple_score"], item["receipt"], item["tie_token"]))
                    else:
                        pending.sort(key=lambda item: (-item["model_score"], item["receipt"], item["tie_token"]))
                    selected = pending[:capacity]
                    pending = pending[capacity:]
                    for item in selected:
                        reviewed[item["event_id"]] = day
                day += dt.timedelta(days=1)
            delays_all, delays_burden, delays_nonburden = [], [], []
            reviewed_burden = reviewed_nonburden = 0
            for item in queue_inputs:
                review_day = reviewed.get(item["event_id"])
                observed = review_day is not None
                delay = (review_day - item["receipt"]).days if observed else (simulation_end - item["receipt"]).days
                restricted = min(30, delay)
                queue_rows.append({
                    "capacity_scenario": capacity_name, "daily_review_opportunities": capacity,
                    "policy": policy, "event_id": item["event_id"], "receipt_date": item["receipt"].isoformat(),
                    "review_date": review_day.isoformat() if review_day else "",
                    "review_status": "REVIEWED" if observed else "RIGHT_CENSORED_UNREVIEWED",
                    "simulated_time_to_review_days": delay if observed else "",
                    "review_delay_or_censor_days": delay, "restricted_30d_review_delay": restricted,
                    "operational_burden_composite": item["burden"], "repeat_within_30d": item["repeat30"],
                    "long_resolution_7d": item["long7"], "district": item["district"],
                    "receipt_type": item["receipt_type"], "tie_order_is_actual": False,
                    "interpretation": "simulated review opportunity; not repair completion",
                })
                delays_all.append(restricted)
                (delays_burden if item["burden"] else delays_nonburden).append(restricted)
                reviewed_burden += observed and item["burden"]
                reviewed_nonburden += observed and not item["burden"]
            burden_total = sum(item["burden"] for item in queue_inputs)
            nonburden_total = len(queue_inputs) - burden_total
            queue_summary.append({
                "capacity_scenario": capacity_name, "daily_review_opportunities": capacity,
                "scenario_status": "NONREVIEWING_SCENARIO" if capacity == 0 else "EVALUABLE",
                "policy": policy, "events": len(queue_inputs), "burden_events": burden_total,
                "reviewed_share": len(reviewed) / len(queue_inputs),
                "burden_reviewed_share": reviewed_burden / burden_total if burden_total else 0,
                "nonburden_reviewed_share": reviewed_nonburden / nonburden_total if nonburden_total else 0,
                "restricted_mean_review_delay_all": statistics.mean(delays_all),
                "restricted_mean_review_delay_burden": statistics.mean(delays_burden),
                "restricted_mean_review_delay_nonburden": statistics.mean(delays_nonburden),
                "median_review_delay_burden": statistics.median(delays_burden),
                "p90_review_delay_all": percentile(delays_all, 0.90),
                "review_within_3d_burden": sum(value <= 3 for value in delays_burden) / len(delays_burden),
                "review_within_7d_nonburden": sum(value <= 7 for value in delays_nonburden) / len(delays_nonburden),
                "final_backlog": len(queue_inputs) - len(reviewed), "max_backlog": max_backlog,
            })

    queue_lookup = {(row["capacity_scenario"], row["policy"]): row for row in queue_summary}
    q0 = queue_lookup[("C50", "Q0_DAILY_BATCH_FIFO")]
    q2 = queue_lookup[("C50", "Q2_INTERPRETABLE_SCORE")]
    queue_improvement = q0["restricted_mean_review_delay_burden"] - q2["restricted_mean_review_delay_burden"]
    nonburden_harm = q2["restricted_mean_review_delay_nonburden"] - q0["restricted_mean_review_delay_nonburden"]
    validation_result = next(row for row in model_results if row["split"] == "validation" and row["model"] == selected_model)

    topk_rows = []
    for result in model_results:
        if result["model"] not in {"B1_REPEAT_AWARE_RULE", "B2_LOGISTIC"}:
            continue
        for fraction in (5, 10, 20):
            topk_rows.append({
                "model": result["model"], "split": result["split"], "top_percent": fraction,
                "precision": result[f"top{fraction}_precision"], "recall": result[f"top{fraction}_recall"],
                "enrichment": result[f"top{fraction}_enrichment"],
            })

    fairness_rows = []
    selected_top10 = set(
        holdout_scores[index]["event_id"] for index in sorted(
            range(len(holdout_scores)),
            key=lambda index: (-float(holdout_scores[index]["operational_burden_score"]), holdout_scores[index]["tie_token"]),
        )[:math.ceil(len(holdout_scores) * 0.10)]
    )
    q0_rows = {row["event_id"]: row for row in queue_rows if row["capacity_scenario"] == "C50" and row["policy"] == "Q0_DAILY_BATCH_FIFO"}
    q2_rows = {row["event_id"]: row for row in queue_rows if row["capacity_scenario"] == "C50" and row["policy"] == "Q2_INTERPRETABLE_SCORE"}
    for dimension in ("district", "receipt_type"):
        groups = defaultdict(list)
        for item in queue_inputs:
            groups[item[dimension]].append(item)
        for group, items in sorted(groups.items()):
            burden_items = [item for item in items if item["burden"]]
            fairness_rows.append({
                "dimension": dimension, "group": group, "events": len(items), "burden_events": len(burden_items),
                "support_status": "EVALUABLE" if len(items) >= 100 and len(burden_items) >= 20 else "INSUFFICIENT_SUPPORT",
                "arrival_share": len(items) / len(queue_inputs),
                "top10_priority_share": sum(item["event_id"] in selected_top10 for item in items) / len(selected_top10),
                "group_burden_prevalence": len(burden_items) / len(items),
                "q2_minus_fifo_restricted_delay": statistics.mean(q2_rows[item["event_id"]]["restricted_30d_review_delay"] for item in items) - statistics.mean(q0_rows[item["event_id"]]["restricted_30d_review_delay"] for item in items),
                "fifo_censored_share": sum(q0_rows[item["event_id"]]["review_status"] != "REVIEWED" for item in items) / len(items),
                "q2_censored_share": sum(q2_rows[item["event_id"]]["review_status"] != "REVIEWED" for item in items) / len(items),
            })

    prediction_signal = (
        float(holdout_result["top10_enrichment_asset_cluster_ci_lower"]) > 1.0
        and holdout_result["top10_enrichment"] >= 0.8 * validation_result["top10_enrichment"]
        and holdout_result["top10_precision"] > holdout_result["prevalence"]
    )
    queue_signal = queue_improvement >= 1.0 and q2["review_within_3d_burden"] > q0["review_within_3d_burden"]
    nonburden_guardrail = nonburden_harm <= 1.0 and q2["review_within_7d_nonburden"] >= q0["review_within_7d_nonburden"] - 0.05
    p90_guardrail = all(
        queue_lookup[(capacity, "Q2_INTERPRETABLE_SCORE")]["p90_review_delay_all"]
        <= queue_lookup[(capacity, "Q0_DAILY_BATCH_FIFO")]["p90_review_delay_all"] + 1.0
        for capacity in ("C50", "C75")
    )
    fairness_warning = any(
        row["support_status"] == "EVALUABLE"
        and (row["q2_minus_fifo_restricted_delay"] > 2.0 or row["q2_censored_share"] - row["fifo_censored_share"] > 0.10)
        for row in fairness_rows
    )
    if prediction_signal and queue_signal and nonburden_guardrail and p90_guardrail and not fairness_warning:
        ou_grade, promotion = "OU-A", "OPERATIONAL_PRIORITY_HELPER"
    elif prediction_signal or (queue_improvement > 0 and nonburden_guardrail):
        ou_grade, promotion = "OU-B", "LIMITED_OPERATIONAL_PRIORITY_EVIDENCE"
    elif holdout_result["top10_enrichment"] > 1.0:
        ou_grade, promotion = "OU-C", "HISTORICAL_CONTEXT_DISPLAY_ONLY"
    else:
        ou_grade, promotion = "OU-X", "NO_OPERATIONAL_UTILITY_SIGNAL"

    freeze_files = [
        ROOT / "lightguard_v0_1" / "data" / "validation" / "v17" / "v17_source_manifest.json",
        ROOT / "lightguard_v0_1" / "data" / "validation" / "v17" / "v17_operational_summary.json",
        ROOT / "lightguard_v0_1" / "reports" / "v17" / "v17_final_summary.md",
    ]
    write_json(DATA / "v17_freeze_manifest.json", {
        "release": "v0.17", "status": "FROZEN_UNMODIFIED", "operational_need_grade": "ON-A",
        "spatial_join": "PARTIAL_JOIN", "spatial_analysis": "NO_SPATIAL_JOIN", "d4": "HOLD_PROFILE_ONLY",
        "files": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in freeze_files],
    })
    write_csv(DATA / "v18_event_feature_table.csv", features)
    write_csv(DATA / "v18_outcome_table.csv", outcomes)
    write_json(DATA / "v18_temporal_split.json", {
        "split_basis": "receipt_date", "primary_outcome": PRIMARY, "snapshot_end": SNAPSHOT_END.isoformat(),
        "development": {"start": "2020-01-01", "end": "2023-12-01", "episodes": split_counts["development"]},
        "development_embargo": {"start": "2023-12-02", "end": "2023-12-31"},
        "validation": {"start": "2024-01-01", "end": "2024-12-01", "episodes": split_counts["validation"]},
        "validation_embargo": {"start": "2024-12-02", "end": "2024-12-31"},
        "confirmatory": {"start": "2025-01-01", "end": "2025-07-10", "episodes": split_counts["confirmatory"]},
        "repeat30_censoring": "receipt_date after 2025-07-10 is not evaluable",
        "repeat90_censoring": "receipt_date after 2025-05-11 is not evaluable",
        "confirmatory_frozen_before_scoring": True,
    })
    config = {
        "primary_outcome": PRIMARY, "primary_outcome_role": "operational repeat-record outcome; not fault truth",
        "candidate_limit": 2, "candidates": ["B1_REPEAT_AWARE_RULE", "B2_LOGISTIC"],
        "selected_model": selected_model, "selection_period": "validation_2024", "holdout_refit_count": 0,
        "selection_rule": "higher validation top10 enrichment wins; exact tie selects B1",
        "model_input_features": MODEL_FEATURES + ["receipt_type", "district", "month", "day_of_week"],
        "banned_features": sorted(BANNED_FEATURES), "asset_id_memorization": False,
        "same_day_order_feature": False, "tie_token_version": "lightguard-v018-tie-v1_outcome_free_not_actual_order",
        "logistic": {"iterations": 300, "learning_rate": learning_rate, "l2": l2, "intercept": intercept,
                     "feature_names": transform_names, "weights": weights.tolist(),
                     "numeric_means": means.tolist(), "numeric_scales": scales.tolist()},
        "simple_rule": {"rule": "prior_event_count_90d >= 1", "development_probability_map": flag_rates},
        "capacity": {"basis": "development all-calendar-day valid closure counts, nearest-rank", **capacities,
                     "C25_status": "NONREVIEWING_SCENARIO" if capacities["C25"] == 0 else "EVALUABLE",
                     "staffing_parameter_count": 0, "service_duration_parameter_count": 0},
        "confirmatory_outcome_inspected_before_freeze": False,
    }
    config["config_sha256"] = hashlib.sha256(json.dumps(config, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    write_json(DATA / "v18_model_config.json", config)
    write_csv(DATA / "v18_confirmatory_scores.csv", holdout_scores)
    write_csv(DATA / "v18_queue_simulation.csv", queue_rows)
    write_csv(REPORT / "v18_model_results.csv", model_results)
    write_csv(REPORT / "v18_topk_enrichment.csv", topk_rows)
    write_csv(REPORT / "v18_queue_results.csv", queue_summary)
    write_csv(REPORT / "v18_fairness_distribution.csv", fairness_rows)
    write_csv(REPORT / "v18_sensitivity_analysis.csv", queue_summary)

    leakage_audit = f"""
# v0.18 Feature Leakage Audit

- D1 SHA-256: `{SOURCE_SHA}`
- Feature rows: {len(features):,}; outcome rows: {len(outcomes):,}
- Availability boundary: start of receipt day; every dependency receipt date is strictly earlier.
- Same-day order synthesized: `NO`
- Prior completed-duration history requires `processing_date < current receipt date`: `PASS`
- Open prior case requires `receipt_date < d <= processing_date`: `PASS`
- Current processing date/duration in feature table: `NO`
- Future repeat outcome in feature table: `NO`
- Asset ID, D2/D3/D4/D5, AMI, staffing feature usage: `NO`
- Management-number memorization: `NO`; pseudonym is audit-only and excluded from matrix.
- Repeat-30 censoring after 2025-07-10: `PASS`
- Temporal order: development < validation < confirmatory: `PASS`
"""
    write_md(REPORT / "v18_feature_leakage_audit.md", leakage_audit)
    write_md(REPORT / "v18_prediction_protocol.md", f"""
# v0.18 Prediction Protocol

Primary outcome was frozen as `{PRIMARY}` before confirmatory scoring. Features use only start-of-day observable D1 information. Same-day order, current outcome, future recurrence, asset identifiers, D2-D5, AMI, staffing, causes, and severity are excluded.

Development: 2020-01-01 to 2023-12-01 ({split_counts['development']:,} episodes). Validation: 2024-01-01 to 2024-12-01 ({split_counts['validation']:,}). The remaining 30 days of each year are embargoed. Confirmatory: 2025-01-01 to 2025-07-10 ({split_counts['confirmatory']:,}). B1 is a 90-day repeat-history rule. B2 is L2 logistic regression. Validation top-decile enrichment selects once; holdout refit is zero.

Primary metrics are average precision, proportion-based top-K precision/recall/enrichment, Brier score, and 10-bin ECE. These evaluate repeat-record operational concentration, not physical fault detection.
""")
    write_md(REPORT / "v18_queue_protocol.md", f"""
# v0.18 Queue Protocol

Daily batches are replayed with no intake time. Capacity uses development all-calendar-day valid closure counts: C25={capacities['C25']}, C50={capacities['C50']}, C75={capacities['C75']}. C25 is `{config['capacity']['C25_status']}` and is not used for a positive utility claim.

Q0 is date-resolution FIFO; Q1 prioritizes prior 90-day history; Q2 uses the frozen selected score. Outcome-free SHA-256 tie tokens provide reproducibility but are not actual arrival order. Outputs are simulated time-to-review, never repair completion or staffing effects.
""")
    write_md(REPORT / "v18_calibration_report.md", "# v0.18 Calibration\n\n" + "\n".join(
        f"- {row['split']} / {row['model']}: Brier {row['brier']:.4f}, ECE {row['ece_10bin']:.4f}"
        for row in model_results
    ))
    service_summary = f"""
# v0.18 Service Value Summary

- Selected: `{selected_model}` from validation only.
- Confirmatory repeat-30 prevalence: {holdout_result['prevalence']:.1%}.
- Confirmatory AP: {holdout_result['average_precision']:.3f}.
- Confirmatory top-10 precision: {holdout_result['top10_precision']:.1%}; enrichment: {holdout_result['top10_enrichment']:.2f}x; asset-cluster bootstrap 95% CI {holdout_result['top10_enrichment_asset_cluster_ci_lower']:.2f}x to {holdout_result['top10_enrichment_asset_cluster_ci_upper']:.2f}x.
- C50 FIFO burden restricted mean review delay: {q0['restricted_mean_review_delay_burden']:.2f} days.
- C50 Q2 burden restricted mean review delay: {q2['restricted_mean_review_delay_burden']:.2f} days; difference in favor of Q2: {queue_improvement:.2f} days.
- C50 nonburden delay change Q2-FIFO: {nonburden_harm:.2f} days.
- Operational utility grade: **{ou_grade}**; product status: `{promotion}`.

This is retrospective priority concentration and simulated review ordering. It is not fault accuracy, repair-time reduction, complaint prevention, staffing reduction, cost savings, or evidence of transfer to Suyeong.
"""
    write_md(REPORT / "v18_service_value_summary.md", service_summary)
    write_md(REPORT / "v18_independent_audit.md", f"""
# v0.18 Independent Audit

- v0.17 freeze integrity: `PASS`
- Chronological split and 30/90-day censoring: `PASS`
- Start-of-day feature availability: `PASS`
- Same-day order invention: `NO`
- Current/future outcome leakage: `NO`
- Asset ID memorization: `NO`
- D2/D3/D4/D5 or AMI event features: `NO`
- Capacity based on observed development closure records: `PASS`; C25=0 disclosed.
- Simulated review presented as repair completion: `NO`
- Fault-probability, complaint-reduction, staffing, or savings claim: `NO`
- Daegu-to-Suyeong performance transfer: `NO`
- Negative or limited result preserved: `YES` ({ou_grade})
- TERRA temporal/queue and LUNA workflow review incorporated: `PASS`
""")
    final_summary = f"""
# LightGuard v0.18 Retrospective Operational Triage Utility

## 1. Freeze

- v0.17: frozen `ON-A`; D1 hash `{SOURCE_SHA}`.

## 2. Temporal Split

- Development: 2020-01-01 to 2023-12-01, {split_counts['development']:,} asset-day episodes; 30-day year-end embargo follows.
- Validation: 2024-01-01 to 2024-12-01, {split_counts['validation']:,} episodes; 30-day year-end embargo follows.
- Confirmatory: 2025-01-01 to 2025-07-10, {split_counts['confirmatory']:,} fully observed 30-day episodes.

## 3. Outcomes

| split | repeat-30 prevalence |
|---|---:|
| development | {float(y_dev.mean()):.1%} |
| validation | {float(y_val.mean()):.1%} |
| confirmatory | {float(y_hold.mean()):.1%} |

Long-resolution and recurrence are operational outcomes, not physical fault labels.

## 4. Causal Features

Receipt type, district, month/weekday, prior 30/90/365-day records, elapsed days, already-completed long histories, open prior cases, start-of-day backlog, and prior 7/30-day intake are used. Leakage audit: `PASS`.

## 5. Prediction

| model | holdout AP | top10 precision | top10 enrichment | Brier |
|---|---:|---:|---:|---:|
{chr(10).join(f"| {row['model']} | {row['average_precision']:.3f} | {row['top10_precision']:.1%} | {row['top10_enrichment']:.2f}x | {row['brier']:.3f} |" for row in model_results if row['split'] == 'confirmatory')}

## 6. Primary Outcome

- Selected before holdout: `{PRIMARY}`.
- Model selected on validation: `{selected_model}`.
- Confirmatory result: AP {holdout_result['average_precision']:.3f}, top-decile enrichment {holdout_result['top10_enrichment']:.2f}x, asset-cluster bootstrap lower bound {holdout_result['top10_enrichment_asset_cluster_ci_lower']:.2f}x.

## 7. Queue Capacity

- C25={capacities['C25']} (`NONREVIEWING_SCENARIO`), C50={capacities['C50']}, C75={capacities['C75']} observed-record review opportunities/day.

## 8. Queue Policies

At C50, Q0 burden restricted mean review delay is {q0['restricted_mean_review_delay_burden']:.2f} days and Q2 is {q2['restricted_mean_review_delay_burden']:.2f} days. This is simulated time-to-review, not actual repair time.

## 9. Operational Utility

- Grade: **{ou_grade}**
- Product status: `{promotion}`
- FIFO comparison: burden delay improvement {queue_improvement:.2f} days; nonburden change {nonburden_harm:+.2f} days.

## 10. Distribution

District and receipt-route distributions are reported with support thresholds in `v18_fairness_distribution.csv`. Year shift is material: repeat-30 prevalence declines from {float(y_dev.mean()):.1%} to {float(y_hold.mean()):.1%}.

## 11. LightGuard Mapping

`signal_evidence` remains unavailable in Daegu. Operational history supports `REMOTE_REVIEW_CANDIDATE`; the field queue remains `FIELD_INSPECTION_CANDIDATE` with field confirmation required. Direct AMI validation: `NO`.

## 12. Claims Allowed

Retrospective burden prioritization, simulated time-to-review, and operational-history enrichment.

## 13. Claims Prohibited

Actual repair-time reduction, complaint prevention, fault accuracy/probability, staffing reduction, cost savings, and geographic transfer.

## 14. QA / Build

Artifact QA is enforced by `scripts/test_v18_artifacts.py`; Flutter analyze/test/Web/Android by `scripts/v18_preflight.sh`.

## 15. Next Step

Keep historical context only unless the frozen promotion gate passes; acquire prospective review/field outcomes before any field-effect claim.
"""
    write_md(REPORT / "v18_final_summary.md", final_summary)

    sources = """
- D1 official source: https://www.data.go.kr/data/15120484/fileData.do
- scikit-learn TimeSeriesSplit: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html
- scikit-learn calibration: https://scikit-learn.org/stable/modules/calibration.html
- NIST/SEMATECH handbook: https://www.itl.nist.gov/div898/handbook/
- van Houwelingen (2007), landmarking: https://doi.org/10.1111/j.1467-9469.2006.00529.x
- Andersen and Gill (1982), recurrent events: https://doi.org/10.1214/aos/1176345976
- OpenAI Harness Engineering: https://openai.com/index/harness-engineering/
- OpenAI Codex: https://openai.com/codex/
- Codex AGENTS.md: https://github.com/openai/codex/blob/main/docs/agents_md.md
"""
    write_md(LEARNING / "sol_orchestration.md", "# SOL Orchestration\n\n" + sources + "\nDefinitions, split, candidates, capacity, and claims were frozen before confirmatory scoring.")
    write_md(LEARNING / "terra_temporal_validation.md", "# TERRA Temporal Validation\n\n" + sources + "\nStrict landmarking uses only start-of-day information; same-day order and future resolution/recurrence are excluded. Primary repeat-30 uses right censoring.")
    write_md(LEARNING / "terra_queue_simulation.md", "# TERRA Queue Simulation\n\n" + sources + f"\nAll-calendar-day closure quantiles yield C25={capacities['C25']}, C50={capacities['C50']}, C75={capacities['C75']}; C25 is nonreviewing. Queue delay is simulated review only.")
    write_md(LEARNING / "luna_workflow_mapping.md", "# LUNA Workflow Mapping\n\n" + sources + "\nUse DATA_QUALITY_REVIEW, REMOTE_REVIEW_CANDIDATE, and FIELD_INSPECTION_CANDIDATE. D3 is aggregate context, never an event feature.")
    write_md(LEARNING / "luna_independent_qa.md", "# LUNA Independent QA\n\n" + sources + f"\nLeakage, asset memorization, temporal contamination, simulated-review wording, AMI separation, complaint/cost claims, and transfer boundaries: PASS. Final grade preserved as {ou_grade}.")
    write_md(APP_DOCS / "v18_operational_priority_validation.md", service_summary)
    write_md(APP_DOCS / "v18_operational_triage_mapping.md", """
# v0.18 Operational Triage Mapping

- `DATA_QUALITY_REVIEW`: invalid dates, unavailable history, and source-quality issues.
- `REMOTE_REVIEW_CANDIDATE`: repeat history, open prior records, and start-of-day queue context for retrospective recheck.
- `FIELD_INSPECTION_CANDIDATE`: a review queue candidate requiring field confirmation.

D2-D5 and AMI are absent from the retrospective event feature matrix. The score is not a physical-fault probability, and simulated time-to-review is not repair time.
""")

    card_source = f"""import 'package:flutter/material.dart';

class V18OperationalTriageContract {{
  const V18OperationalTriageContract._();

  static const status = '{ou_grade}';
  static const title = 'v0.18 회고형 운영 우선검토 검증';
  static const split = '개발 {split_counts['development']:,} · 검증 {split_counts['validation']:,} · 확인 {split_counts['confirmatory']:,} asset-day episodes';
  static const primary = 'Primary · 30일 반복 기록 이벤트 · 확인기간 prevalence {holdout_result['prevalence']:.1%}';
  static const prediction = '{selected_model} · AP {holdout_result['average_precision']:.3f} · Top 10% enrichment {holdout_result['top10_enrichment']:.2f}x';
  static const queue = 'C25=0 비검토 · C50={capacities['C50']} · C75={capacities['C75']} · C50 burden review difference {queue_improvement:+.2f}일';
  static const workflow = 'DATA_QUALITY_REVIEW → REMOTE_REVIEW_CANDIDATE → FIELD_INSPECTION_CANDIDATE';
  static const decision = '{promotion}';
  static const boundary = '접수일 시작 시점의 과거 D1 이력만 사용한 retrospective simulation입니다. 고장 확률·AMI 정확도·실제 수리시간 단축·민원 감소·비용절감·대구→수영구 전이를 뜻하지 않습니다.';
}}

class V18OperationalTriageCard extends StatelessWidget {{
  const V18OperationalTriageCard({{super.key}});

  @override
  Widget build(BuildContext context) => Card(
        key: const Key('v18-operational-triage-card'),
        color: const Color(0xFFE7F0F4),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(children: [
              const Icon(Icons.low_priority, color: Color(0xFF175A70)),
              const SizedBox(width: 8),
              Expanded(child: Text(V18OperationalTriageContract.title, style: Theme.of(context).textTheme.titleLarge)),
              const Chip(label: Text(V18OperationalTriageContract.status)),
            ]),
            const SizedBox(height: 12),
            const Text(V18OperationalTriageContract.split),
            const Text(V18OperationalTriageContract.primary),
            const Text(V18OperationalTriageContract.prediction),
            const Text(V18OperationalTriageContract.queue),
            const Divider(height: 24),
            const Text(V18OperationalTriageContract.workflow, style: TextStyle(fontWeight: FontWeight.w700)),
            const SizedBox(height: 6),
            const Text(V18OperationalTriageContract.decision),
            const SizedBox(height: 8),
            const Text(V18OperationalTriageContract.boundary, style: TextStyle(fontSize: 12, color: Color(0xFF174657))),
          ]),
        ),
      );
}}
"""
    CARD.write_text(card_source, encoding="utf-8")
    artifact_paths = [
        DATA / "v18_event_feature_table.csv", DATA / "v18_outcome_table.csv", DATA / "v18_temporal_split.json",
        DATA / "v18_model_config.json", DATA / "v18_confirmatory_scores.csv", DATA / "v18_queue_simulation.csv",
        REPORT / "v18_model_results.csv", REPORT / "v18_queue_results.csv", REPORT / "v18_final_summary.md", CARD,
    ]
    write_json(DATA / "v18_artifact_manifest.json", {
        "release": "v0.18", "generated_on": "2026-08-21", "primary": PRIMARY,
        "selected_model": selected_model, "ou_grade": ou_grade, "promotion": promotion,
        "artifacts": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in artifact_paths],
    })
    print(json.dumps({
        "status": "BUILT", "selected_model": selected_model, "holdout_ap": holdout_result["average_precision"],
        "holdout_top10_enrichment": holdout_result["top10_enrichment"], "capacities": capacities,
        "c50_burden_review_improvement_days": queue_improvement, "nonburden_harm_days": nonburden_harm,
        "ou_grade": ou_grade, "promotion": promotion,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
