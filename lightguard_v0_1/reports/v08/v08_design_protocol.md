# LightGuard v0.8 Experimental Design Protocol

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
| suyeong | winter | 24 | 12 | 12 | 36 | 18 | 18 |
| suyeong | spring | 24 | 12 | 12 | 36 | 18 | 18 |
| suyeong | summer | 24 | 12 | 12 | 36 | 18 | 18 |
| suyeong | autumn | 24 | 12 | 12 | 36 | 18 | 18 |
| gangneung | winter | 24 | 12 | 12 | 36 | 18 | 18 |
| gangneung | spring | 24 | 12 | 12 | 36 | 18 | 18 |
| gangneung | summer | 24 | 12 | 12 | 36 | 18 | 18 |
| gangneung | autumn | 24 | 12 | 12 | 36 | 18 | 18 |
| chungju | winter | 24 | 12 | 12 | 36 | 18 | 18 |
| chungju | spring | 24 | 12 | 12 | 36 | 18 | 18 |
| chungju | summer | 24 | 12 | 12 | 36 | 18 | 18 |
| chungju | autumn | 24 | 12 | 12 | 36 | 18 | 18 |

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
| suyeong | calibration | 96 | low_rated_load_tertile, medium_rated_load_tertile, high_rated_load_tertile |
| suyeong | confirmatory | 108 | low_rated_load_tertile, medium_rated_load_tertile, high_rated_load_tertile |
| gangneung | calibration | 96 | low_rated_load_tertile, medium_rated_load_tertile, high_rated_load_tertile |
| gangneung | confirmatory | 144 | low_rated_load_tertile, medium_rated_load_tertile, high_rated_load_tertile |
| chungju | calibration | 96 | fixture_count_all_zero_unstratified |
| chungju | confirmatory | 144 | fixture_count_all_zero_unstratified |

## Deterministic freeze

- Generator: `scripts/build_v08_design.py`
- Matrix: `lightguard_v0_1/data/validation/v08_design_matrix.csv`
- Matrix SHA-256: `9fba439a9bd22d184e6a705af559a9b43a39fb4b9498cfa3d3a50c2f5853dbb0`
- Row integrity: every row contains SHA-256 over its canonical non-hash fields.
- Reproduction: `python3 scripts/build_v08_design.py`; verification without writing: `python3 scripts/build_v08_design.py --check`.

## Analysis boundaries

Use blocked summaries for region, season, and region x season controlled factor effects; do not interpret scenario-generated effects as actual municipal AMI generalization. Report macro and per-cell results, preserve abstentions separately from correct normal calls, and use asset-pool-aware/cell-stratified resampling because repeated Suyeong confirmation exposures are not independent cabinets.
