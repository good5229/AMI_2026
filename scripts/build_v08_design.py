#!/usr/bin/env python3
"""Build the frozen, blocked v0.8 calibration/confirmatory design.

This is a design generator, not a scenario injector or detector tuner.  It
never reads v0.7 cases: those remain regression-only by protocol.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "lightguard_v0_1/data/validation/v08_design_matrix.csv"
REQUIRED_OUT = ROOT / "lightguard_v0_1/data/validation/v08/v08_design_matrix.csv"
PROTOCOL = ROOT / "lightguard_v0_1/reports/v08/v08_design_protocol.md"

REGIONS = ("suyeong", "gangneung", "chungju")
SEASONS = ("winter", "spring", "summer", "autumn")
SPLITS = {
    "calibration": {"rows_per_cell": 24, "seed_base": 100_000_000},
    "confirmatory": {"rows_per_cell": 36, "seed_base": 200_000_000},
}

NORMAL_TYPES = (
    "normal_full_operation",
    "twilight_boundary_operation",
    "short_transient_spike",
    "allowed_partial_operation",
    "temporary_load_fluctuation",
    "feature_missing_normal",
    "high_cloud_or_rainfall_hard_negative",
)
ABNORMAL_TYPES = (
    "post_sunrise_persistent_activation",
    "deep_day_partial_activation",
    "deep_day_full_activation",
    "phase_selective_activation",
    "weak_long_duration_activation",
    "moderate_load_mismatch",
    "partial_activation_long_persistence",
    "phase_anomaly_moderate_activation",
)

FIELDNAMES = (
    "case_id", "split", "region_id", "season", "block_id", "block_order",
    "random_seed", "asset_cabinet_uid", "asset_stratum", "asset_stratum_basis",
    "asset_metric_value", "asset_reused_within_split", "label", "scenario_type",
    "severity", "duration_min", "solar_position", "phase_pattern", "weather_regime",
    "feature_availability", "available_features", "missing_features", "rated_load_status",
    "rated_load_w", "activation_fraction", "observed_load_ratio", "phase_imbalance_ratio",
    "signal_offset_min", "signal_parameter_id", "factor_tuple_id", "source_dataset",
    "row_sha256",
)


def stable_int(*parts: object) -> int:
    digest = hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).hexdigest()
    return int(digest[:12], 16)


def stable_order(values: list[dict], *parts: object) -> list[dict]:
    return sorted(values, key=lambda item: (stable_int(*parts, item["uid"]), item["uid"]))


def read_assets(region: str) -> list[dict]:
    seed = ROOT / f"lightguard_app/assets/data/{region}_v02_seed.json"
    payload = json.loads(seed.read_text(encoding="utf-8"))
    assets = []
    for obj in payload["objects"]:
        uid = obj["cabinet_uid"]
        expected = obj.get("expected_load", {})
        asset_info = obj.get("asset_info", {})
        if region == "chungju":
            metric = asset_info.get("fixture_count")
            if metric is None:
                metric = expected.get("lamp_count")
            status = "unavailable_no_imputation"
            rated = None
        else:
            metric = expected.get("rated_power_w")
            if metric is None:
                raise ValueError(f"{region}/{uid} has no rated_power_w")
            status = "available"
            rated = float(metric)
        assets.append({"uid": uid, "metric": float(metric or 0), "rated_w": rated, "status": status})
    return assets


def assign_strata(region: str, assets: list[dict]) -> dict[str, list[dict]]:
    if region == "chungju":
        values = {asset["metric"] for asset in assets}
        if values != {0.0}:
            raise ValueError("Chungju fixture_count status changed; update the protocol before design generation.")
        return {"fixture_count_all_zero_unstratified": stable_order(assets, region, "all_zero")}
    ordered = sorted(assets, key=lambda item: (item["metric"], item["uid"]))
    labels = ("low_rated_load_tertile", "medium_rated_load_tertile", "high_rated_load_tertile")
    strata = {label: [] for label in labels}
    for index, asset in enumerate(ordered):
        strata[labels[(index * 3) // len(ordered)]].append(asset)
    return {label: stable_order(group, region, label) for label, group in strata.items()}


def split_asset_pools(region: str, strata: dict[str, list[dict]]) -> dict[str, dict[str, list[dict]]]:
    pools = {"calibration": {}, "confirmatory": {}}
    for label, group in strata.items():
        if region == "suyeong":
            # 96 calibration + 144 confirmatory rows exceed 204 cabinets.  The
            # pools remain mutually exclusive; confirmation repeats only inside
            # its own 108-cabinet pool, never across the split boundary.
            calibration_n = 32
            confirmatory_n = len(group) - calibration_n
        elif region == "gangneung":
            calibration_n, confirmatory_n = 32, 48
        else:
            calibration_n, confirmatory_n = 96, 144
        if len(group) < calibration_n + confirmatory_n:
            raise ValueError(f"{region}/{label} lacks assets for disjoint split pools")
        pools["calibration"][label] = group[:calibration_n]
        pools["confirmatory"][label] = group[calibration_n:calibration_n + confirmatory_n]
    calibration_ids = {item["uid"] for group in pools["calibration"].values() for item in group}
    confirmatory_ids = {item["uid"] for group in pools["confirmatory"].values() for item in group}
    if calibration_ids & confirmatory_ids:
        raise AssertionError(f"asset leakage in {region}")
    return pools


def type_schedule(split: str, label: str) -> list[str]:
    if split == "calibration":
        if label == "normal":
            repeats = (2, 2, 2, 2, 2, 1, 1)
            types = NORMAL_TYPES
        else:
            repeats = (2, 2, 2, 2, 1, 1, 1, 1)
            types = ABNORMAL_TYPES
    else:
        if label == "normal":
            repeats = (3, 3, 3, 3, 2, 2, 2)
            types = NORMAL_TYPES
        else:
            repeats = (3, 3, 2, 2, 2, 2, 2, 2)
            types = ABNORMAL_TYPES
    return [name for name, count in zip(types, repeats) for _ in range(count)]


def semantic_defaults(scenario_type: str) -> tuple[str, str, tuple[int, ...], tuple[str, ...]]:
    """Return solar, phase, durations, and valid phases for the named case."""
    if scenario_type == "normal_full_operation":
        return "night", "all_phase", (30, 60, 90), ("all_phase",)
    if scenario_type == "twilight_boundary_operation":
        return "twilight_boundary", "all_phase", (15, 30, 60), ("all_phase",)
    if scenario_type == "short_transient_spike":
        return "night", "all_phase", (15,), ("all_phase", "not_applicable")
    if scenario_type == "allowed_partial_operation":
        return "night", "two_phase", (30, 60), ("two_phase", "single_phase")
    if scenario_type == "temporary_load_fluctuation":
        return "night", "all_phase", (15, 30), ("all_phase",)
    if scenario_type == "feature_missing_normal":
        return "night", "not_applicable", (30, 60), ("not_applicable", "all_phase")
    if scenario_type == "high_cloud_or_rainfall_hard_negative":
        return "pre_sunset", "all_phase", (30, 60), ("all_phase",)
    if scenario_type == "post_sunrise_persistent_activation":
        return "post_sunrise", "all_phase", (60, 90), ("all_phase",)
    if scenario_type == "deep_day_partial_activation":
        return "deep_day", "two_phase", (30, 60), ("two_phase", "single_phase")
    if scenario_type == "deep_day_full_activation":
        return "deep_day", "all_phase", (15, 30, 60), ("all_phase",)
    if scenario_type == "phase_selective_activation":
        return "deep_day", "single_phase", (30, 60), ("single_phase", "two_phase")
    if scenario_type == "weak_long_duration_activation":
        return "post_sunrise", "all_phase", (60, 90), ("all_phase", "two_phase")
    if scenario_type == "moderate_load_mismatch":
        return "deep_day", "all_phase", (30, 60), ("all_phase",)
    if scenario_type == "partial_activation_long_persistence":
        return "post_sunrise", "two_phase", (60, 90), ("two_phase", "single_phase")
    if scenario_type == "phase_anomaly_moderate_activation":
        return "deep_day", "single_phase", (30, 60), ("single_phase", "two_phase")
    raise ValueError(scenario_type)


def feature_state(region: str, scenario_type: str, index: int) -> tuple[str, str, str]:
    if region == "chungju":
        options = (
            ("load_unavailable_no_imputation", "phase,weather", "rated_load"),
            ("load_weather_unavailable_no_imputation", "phase", "rated_load,weather"),
            ("load_phase_unavailable_no_imputation", "weather", "rated_load,phase"),
        )
    elif scenario_type == "feature_missing_normal":
        options = (("weather_unavailable", "rated_load,phase", "weather"),)
    else:
        options = (
            ("complete", "rated_load,phase,weather", ""),
            ("weather_unavailable", "rated_load,phase", "weather"),
            ("phase_unavailable", "rated_load,weather", "phase"),
            ("load_unavailable", "phase,weather", "rated_load"),
        )
    return options[index % len(options)]


def signal_values(label: str, severity: str, index: int) -> tuple[float, float, float, int]:
    severity_index = {"none": 0, "weak": 1, "moderate": 2, "strong": 3}[severity]
    if label == "normal":
        activation = (0.78, 0.86, 0.94)[index % 3]
        load_ratio = (0.96, 1.00, 1.04)[index % 3]
        imbalance = (0.00, 0.03, 0.06)[index % 3]
    else:
        activation = (0.20, 0.48, 0.80)[severity_index - 1]
        load_ratio = (0.72, 0.52, 0.25)[severity_index - 1]
        imbalance = (0.20, 0.45, 0.75)[severity_index - 1]
    offset = -45 + ((index * 17 + severity_index * 11) % 91)
    return activation, load_ratio, imbalance, offset


def canonical_row(row: dict[str, object]) -> str:
    return "|".join(str(row[name]) for name in FIELDNAMES if name != "row_sha256")


def build_rows() -> tuple[list[dict[str, object]], dict[str, dict[str, list[dict]]], dict[str, object]]:
    assets = {region: assign_strata(region, read_assets(region)) for region in REGIONS}
    pools = {region: split_asset_pools(region, assets[region]) for region in REGIONS}
    cursors: dict[tuple[str, str, str], int] = defaultdict(int)
    rows: list[dict[str, object]] = []
    factor_tuples: set[tuple[object, ...]] = set()
    parameter_ids: set[str] = set()
    used_seeds: set[int] = set()
    used_case_ids: set[str] = set()
    block_order = 0

    for region in REGIONS:
        stratum_labels = tuple(pools[region]["calibration"])
        for season in SEASONS:
            block_order += 1
            for split, split_config in SPLITS.items():
                block_id = f"{region}_{season}_{split}"
                schedules = [("normal", type_schedule(split, "normal")), ("abnormal", type_schedule(split, "abnormal"))]
                block_rows = 0
                for label, schedule in schedules:
                    for local_index, scenario_type in enumerate(schedule):
                        global_index = len(rows) + 1
                        stratum = stratum_labels[(global_index + local_index + block_order) % len(stratum_labels)]
                        pool = pools[region][split][stratum]
                        cursor_key = (region, split, stratum)
                        asset = pool[cursors[cursor_key] % len(pool)]
                        reused = cursors[cursor_key] >= len(pool)
                        cursors[cursor_key] += 1
                        default_solar, default_phase, durations, phase_options = semantic_defaults(scenario_type)

                        for attempt in range(128):
                            variant = global_index + attempt * 37 + (0 if split == "calibration" else 701)
                            severity = "none" if label == "normal" else ("weak", "moderate", "strong")[variant % 3]
                            # Independent cyclic coordinates prevent the small
                            # semantic domains (for example fixed 15-minute
                            # transients) from collapsing into one repeated
                            # factor tuple across the two splits.
                            duration = durations[variant % len(durations)]
                            phase = phase_options[(variant // 3) % len(phase_options)]
                            weather = ("clear", "high_cloud", "overcast", "rainfall")[(variant // 7) % 4]
                            availability, available, missing = feature_state(region, scenario_type, variant // 11)
                            factor_tuple = (region, season, label, scenario_type, severity, duration, default_solar, phase, weather, availability)
                            if factor_tuple not in factor_tuples:
                                factor_tuples.add(factor_tuple)
                                break
                        else:
                            raise AssertionError(f"unable to allocate unique factor tuple for {block_id}")

                        seed = split_config["seed_base"] + global_index
                        case_id = f"V08-{split[:3].upper()}-{region[:3].upper()}-{season[:3].upper()}-{block_rows + 1:02d}"
                        parameter_id = hashlib.sha256(f"v08-signal|{split}|{seed}|{factor_tuple}".encode()).hexdigest()[:24]
                        if case_id in used_case_ids or seed in used_seeds or parameter_id in parameter_ids:
                            raise AssertionError("split isolation identifier collision")
                        used_case_ids.add(case_id)
                        used_seeds.add(seed)
                        parameter_ids.add(parameter_id)
                        activation, load_ratio, imbalance, offset = signal_values(label, severity, variant)
                        if asset["rated_w"] is None:
                            rated_value: object = ""
                        else:
                            rated_value = f"{asset['rated_w']:.1f}"
                        basis = "fixture_count_observed_all_zero" if region == "chungju" else "rated_load_w_tertile"
                        row: dict[str, object] = {
                            "case_id": case_id,
                            "split": split,
                            "region_id": region,
                            "season": season,
                            "block_id": block_id,
                            "block_order": block_order,
                            "random_seed": seed,
                            "asset_cabinet_uid": asset["uid"],
                            "asset_stratum": stratum,
                            "asset_stratum_basis": basis,
                            "asset_metric_value": f"{asset['metric']:.1f}",
                            "asset_reused_within_split": str(reused).lower(),
                            "label": label,
                            "scenario_type": scenario_type,
                            "severity": severity,
                            "duration_min": duration,
                            "solar_position": default_solar,
                            "phase_pattern": phase,
                            "weather_regime": weather,
                            "feature_availability": availability,
                            "available_features": available,
                            "missing_features": missing,
                            "rated_load_status": asset["status"],
                            "rated_load_w": rated_value,
                            "activation_fraction": f"{activation:.2f}",
                            "observed_load_ratio": f"{load_ratio:.2f}",
                            "phase_imbalance_ratio": f"{imbalance:.2f}",
                            "signal_offset_min": offset,
                            "signal_parameter_id": parameter_id,
                            "factor_tuple_id": hashlib.sha256(repr(factor_tuple).encode()).hexdigest()[:24],
                            "source_dataset": "v08_design_only;v07_regression_only_not_ingested",
                        }
                        row["row_sha256"] = hashlib.sha256(canonical_row(row).encode()).hexdigest()
                        rows.append(row)
                        block_rows += 1
                if block_rows != split_config["rows_per_cell"]:
                    raise AssertionError(f"{block_id} row count {block_rows}")
    metadata = {"assets": assets, "pools": pools}
    return rows, pools, metadata


def csv_bytes(rows: list[dict[str, object]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDNAMES, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def assert_design(rows: list[dict[str, object]], pools: dict[str, dict[str, dict[str, list[dict]]]]) -> None:
    assert len(rows) == 720
    counts = Counter((row["split"], row["region_id"], row["season"]) for row in rows)
    for region in REGIONS:
        for season in SEASONS:
            calibration = [row for row in rows if row["split"] == "calibration" and row["region_id"] == region and row["season"] == season]
            assert len(calibration) == 24
            assert Counter(row["label"] for row in calibration) == {"normal": 12, "abnormal": 12}
            confirmatory = [row for row in rows if row["split"] == "confirmatory" and row["region_id"] == region and row["season"] == season]
            assert len(confirmatory) == 36
            assert Counter(row["label"] for row in confirmatory) == {"normal": 18, "abnormal": 18}
            if region != "chungju":
                assert set(Counter(row["asset_stratum"] for row in calibration).values()) == {8}
                assert set(Counter(row["asset_stratum"] for row in confirmatory).values()) == {12}
    assert Counter(row["split"] for row in rows) == {"calibration": 288, "confirmatory": 432}
    assert len({row["case_id"] for row in rows}) == len(rows)
    assert len({row["random_seed"] for row in rows}) == len(rows)
    assert len({row["signal_parameter_id"] for row in rows}) == len(rows)
    assert len({row["factor_tuple_id"] for row in rows}) == len(rows)
    for region in REGIONS:
        calibration_ids = {row["asset_cabinet_uid"] for row in rows if row["region_id"] == region and row["split"] == "calibration"}
        confirmatory_ids = {row["asset_cabinet_uid"] for row in rows if row["region_id"] == region and row["split"] == "confirmatory"}
        assert not calibration_ids & confirmatory_ids, f"{region} asset leakage"
        assert {asset["uid"] for group in pools[region]["calibration"].values() for asset in group} >= calibration_ids
        assert {asset["uid"] for group in pools[region]["confirmatory"].values() for asset in group} >= confirmatory_ids
    assert {row["scenario_type"] for row in rows if row["label"] == "normal"} == set(NORMAL_TYPES)
    assert {row["scenario_type"] for row in rows if row["label"] == "abnormal"} == set(ABNORMAL_TYPES)
    assert {row["severity"] for row in rows if row["label"] == "abnormal"} == {"weak", "moderate", "strong"}
    assert {int(row["duration_min"]) for row in rows} == {15, 30, 60, 90}
    assert {row["solar_position"] for row in rows} == {"night", "twilight_boundary", "post_sunrise", "pre_sunset", "deep_day"}
    assert {row["phase_pattern"] for row in rows} == {"all_phase", "single_phase", "two_phase", "not_applicable"}
    assert {row["weather_regime"] for row in rows} == {"clear", "high_cloud", "overcast", "rainfall"}
    chungju_rows = [row for row in rows if row["region_id"] == "chungju"]
    assert {row["asset_stratum"] for row in chungju_rows} == {"fixture_count_all_zero_unstratified"}
    assert {row["rated_load_status"] for row in chungju_rows} == {"unavailable_no_imputation"}
    assert all(row["rated_load_w"] == "" for row in chungju_rows)
    assert all(row["source_dataset"] == "v08_design_only;v07_regression_only_not_ingested" for row in rows)


def protocol_text(rows: list[dict[str, object]], pools: dict[str, dict[str, dict[str, list[dict]]]], matrix_sha256: str) -> str:
    count_by = Counter((row["split"], row["region_id"], row["season"], row["label"]) for row in rows)
    asset_pool_summary = []
    for region in REGIONS:
        for split in SPLITS:
            size = sum(len(group) for group in pools[region][split].values())
            asset_pool_summary.append(f"| {region} | {split} | {size} | {', '.join(pools[region][split])} |")
    cell_rows = []
    for region in REGIONS:
        for season in SEASONS:
            cell_rows.append(
                f"| {region} | {season} | 24 | 12 | 12 | 36 | "
                f"{count_by[('confirmatory', region, season, 'normal')]} | "
                f"{count_by[('confirmatory', region, season, 'abnormal')]} |"
            )
    return f"""# LightGuard v0.8 Experimental Design Protocol

## Status and scope

This pre-result protocol was frozen on 2026-08-20 by Subagent B / TERRA before any v0.8 detector outcome was generated. It designs controlled scenario injection only; it does not claim actual regional AMI performance. The v0.7 96-case matrix is regression-only and is neither read nor used for calibration or confirmatory allocation.

## Predeclared objective and decision rules

Primary objective: on the frozen v0.8 confirmatory holdout, improve macro anomaly recall over the frozen v0.4 detector evaluated on that same holdout.

Secondary constraints: macro FPR <= 0.05, normal hard-negative FPR <= 0.05, and weak-anomaly recall improvement. A successful candidate must additionally improve at least one of worst-cell recall, average precision, or false-certainty reduction through a documented abstention rule. Evaluation will report Wilson 95% intervals for all principal proportions and a fixed-seed, 1,000-resample, cell-stratified bootstrap interval for baseline-candidate deltas.

Failure is predeclared if recall improves with FPR above either limit; weak-anomaly recovery harms strong-anomaly recall; Chungju missing-load cases are unstable or treated as zero-load evidence; a weather candidate does not improve over its non-weather parent; or confirmatory performance collapses relative to calibration. Confirmatory outcomes must not change weights, threshold, scenario membership, seed, or this matrix.

## Design choice

Region x season is a fixed 3 x 4 block structure. Inside every block, scenario class is balanced and the remaining mixed-level factors use deterministic cyclic fractional allocation. A complete crossing is deliberately not used: type, severity, duration, solar position, phase pattern, weather, feature availability, asset stratum, region, and season would create an uninformative combinatorial explosion. The allocation retains coverage of every required level while preserving exact block totals and explicitly records every aliasing limitation; it is for screening and robustness contrasts, not estimation of unrestricted high-order interactions.

The confirmatory set is a separately seeded, frozen holdout. Calibration and confirmatory rows are disjoint in case ID, random seed, factor tuple, generated signal parameter ID, and selected asset pool. For Suyeong, 96 calibration plus 144 confirmatory row exposures exceed 204 cabinets. Its 96-cabinet calibration and 108-cabinet confirmatory pools are therefore mutually exclusive, and confirmatory assets repeat only within confirmation; this within-split repetition is a block/dependence unit for later bootstrap analysis. Gangneung and Chungju have sufficient assets for their selected row pools without reuse.

## Required totals

| region | season | calibration | calibration normal | calibration abnormal | confirmatory | confirmatory normal | confirmatory abnormal |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(cell_rows)}

Totals: calibration = **288**, confirmatory = **432**, all controlled v0.8 design rows = **720**. Each of the twelve confirmatory cells has exactly 18 normal and 18 abnormal cases.

## Factors and controlled coverage

| factor | allocation |
| --- | --- |
| Region, season | Fixed 3 x 4 blocks: suyeong, gangneung, chungju x winter, spring, summer, autumn. |
| Asset stratum | Suyeong/Gangneung use deterministic observed-rated-load tertiles. Chungju is `fixture_count_all_zero_unstratified`: all 871 source rows report fixture_count 0, so pseudo low/medium/high strata are prohibited. |
| Normal / hard-negative type | Seven types: full operation, twilight boundary, short transient, allowed partial, temporary load fluctuation, feature-missing normal, and high-cloud/rainfall hard negative. |
| Abnormal type | Eight types: post-sunrise persistence, deep-day partial/full, phase-selective, weak long-duration, moderate load mismatch, partial-plus-persistence, and phase-plus-moderate activation. |
| Severity | none for normal; weak, moderate, strong for abnormal. |
| Duration | 15, 30, 60, 90 minutes. |
| Solar position | night, twilight boundary, post-sunrise, pre-sunset, deep daytime. |
| Phase pattern | all-phase, single-phase, two-phase, not-applicable. |
| Weather regime | clear, high-cloud, overcast, rainfall; weather is controlled context unless a later frozen candidate demonstrates incremental value. |
| Feature availability | complete, weather unavailable, phase unavailable, load unavailable; Chungju always retains `load_unavailable_no_imputation` and blank rated-load fields. |

## Asset-pool freeze

| region | split | selected asset-pool size | strata |
| --- | --- | ---: | --- |
{chr(10).join(asset_pool_summary)}

## Deterministic freeze

- Generator: `scripts/build_v08_design.py`
- Matrix: `lightguard_v0_1/data/validation/v08_design_matrix.csv`
- Matrix SHA-256: `{matrix_sha256}`
- Row integrity: every row contains SHA-256 over its canonical non-hash fields.
- Reproduction: `python3 scripts/build_v08_design.py`; verification without writing: `python3 scripts/build_v08_design.py --check`.

## Analysis boundaries

Use blocked summaries for region, season, and region x season controlled factor effects; do not interpret scenario-generated effects as actual municipal AMI generalization. Report macro and per-cell results, preserve abstentions separately from correct normal calls, and use asset-pool-aware/cell-stratified resampling because repeated Suyeong confirmation exposures are not independent cabinets.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify existing frozen outputs without writing")
    args = parser.parse_args()
    rows, pools, _metadata = build_rows()
    assert_design(rows, pools)
    rendered_csv = csv_bytes(rows)
    matrix_sha256 = hashlib.sha256(rendered_csv).hexdigest()
    rendered_protocol = protocol_text(rows, pools, matrix_sha256).encode("utf-8")
    if args.check:
        if not OUT.exists() or not REQUIRED_OUT.exists() or not PROTOCOL.exists():
            raise SystemExit("v0.8 design outputs are missing; run without --check first")
        if OUT.read_bytes() != rendered_csv:
            raise SystemExit("v0.8 design matrix differs from deterministic freeze")
        if REQUIRED_OUT.read_bytes() != rendered_csv:
            raise SystemExit("v0.8 required-path design matrix differs from deterministic freeze")
        if PROTOCOL.read_bytes() != rendered_protocol:
            raise SystemExit("v0.8 design protocol differs from deterministic freeze")
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        REQUIRED_OUT.parent.mkdir(parents=True, exist_ok=True)
        PROTOCOL.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_bytes(rendered_csv)
        REQUIRED_OUT.write_bytes(rendered_csv)
        PROTOCOL.write_bytes(rendered_protocol)
    print(f"v0.8 design: calibration=288 confirmatory=432 total=720 sha256={matrix_sha256}")


if __name__ == "__main__":
    main()
