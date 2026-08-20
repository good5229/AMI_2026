# v0.7 Frozen Detector Failure Forensics

## Scope and boundary

This is a deterministic, no-tuning audit of the frozen v0.7 controlled scenario set. It evaluates **96 scenario-injection rows**, not field AMI observations. It does not estimate, validate, or claim actual AMI performance for Suyeong, Gangneung, Chungju, or any other location.

- Source: `lightguard_v0_1/data/validation/v07/regional_seasonal_cases.json`
- Frozen decision: score >= `0.55`
- Frozen weather weight: `0.0`
- Controlled rows: `96`; anomalies: `48`; normals: `48`
- Stored-score and stored-decision integrity: PASS for all `96` rows
- Controlled anomaly recall: `24/48 (0.500)`
- Controlled normal FPR: `0/48 (0.000)`

## Anomaly-type summary

| anomaly type | total | detected | recall | mean score | mean threshold margin |
| --- | --- | --- | --- | --- | --- |
| daytime_full | 12 | 12 | 1.000 | 0.69833333 | +0.14833333 |
| daytime_partial | 12 | 0 | 0.000 | 0.50000000 | -0.05000000 |
| phase_selective | 12 | 12 | 1.000 | 0.68000000 | +0.13000000 |
| post_sunrise_persistence | 12 | 0 | 0.000 | 0.44500000 | -0.10500000 |

The unobserved types are `daytime_partial` and `post_sunrise_persistence`: each is missed in all 12 controlled region-season cells. This conclusion is calculated from the frozen rows above, not inferred from the scenario names.

## Missed-anomaly score decomposition

| scenario type | score | threshold | margin | activation | duration | load | phase | policy | solar | transient |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| daytime_partial | 0.50000000 | 0.55000000 | -0.05000000 | 0.30000000 | 0.12500000 | 0.07500000 | 0.00000000 | 0.00000000 | 0.00000000 | 0.00000000 |
| post_sunrise_persistence | 0.44500000 | 0.55000000 | -0.10500000 | 0.12000000 | 0.25000000 | 0.07500000 | 0.00000000 | 0.00000000 | 0.00000000 | 0.00000000 |

`post_sunrise_persistence` receives the maximum duration component (`0.25000000`) but only `0.12000000` activation contribution, leaving a `-0.10500000` margin. `daytime_partial` receives moderate activation (`0.30000000`) and duration (`0.12500000`), leaving a `-0.05000000` margin. This is a feature-combination observation, not a proposed parameter change.

## Region x season x anomaly-type summary

| region | season | anomaly type | detected/total (recall) | score | threshold margin |
| --- | --- | --- | --- | --- | --- |
| chungju | autumn | daytime_full | 1/1 (1.000) | 0.69833333 | 0.14833333 |
| chungju | autumn | daytime_partial | 0/1 (0.000) | 0.50000000 | -0.05000000 |
| chungju | autumn | phase_selective | 1/1 (1.000) | 0.68000000 | 0.13000000 |
| chungju | autumn | post_sunrise_persistence | 0/1 (0.000) | 0.44500000 | -0.10500000 |
| chungju | spring | daytime_full | 1/1 (1.000) | 0.69833333 | 0.14833333 |
| chungju | spring | daytime_partial | 0/1 (0.000) | 0.50000000 | -0.05000000 |
| chungju | spring | phase_selective | 1/1 (1.000) | 0.68000000 | 0.13000000 |
| chungju | spring | post_sunrise_persistence | 0/1 (0.000) | 0.44500000 | -0.10500000 |
| chungju | summer | daytime_full | 1/1 (1.000) | 0.69833333 | 0.14833333 |
| chungju | summer | daytime_partial | 0/1 (0.000) | 0.50000000 | -0.05000000 |
| chungju | summer | phase_selective | 1/1 (1.000) | 0.68000000 | 0.13000000 |
| chungju | summer | post_sunrise_persistence | 0/1 (0.000) | 0.44500000 | -0.10500000 |
| chungju | winter | daytime_full | 1/1 (1.000) | 0.69833333 | 0.14833333 |
| chungju | winter | daytime_partial | 0/1 (0.000) | 0.50000000 | -0.05000000 |
| chungju | winter | phase_selective | 1/1 (1.000) | 0.68000000 | 0.13000000 |
| chungju | winter | post_sunrise_persistence | 0/1 (0.000) | 0.44500000 | -0.10500000 |
| gangneung | autumn | daytime_full | 1/1 (1.000) | 0.69833333 | 0.14833333 |
| gangneung | autumn | daytime_partial | 0/1 (0.000) | 0.50000000 | -0.05000000 |
| gangneung | autumn | phase_selective | 1/1 (1.000) | 0.68000000 | 0.13000000 |
| gangneung | autumn | post_sunrise_persistence | 0/1 (0.000) | 0.44500000 | -0.10500000 |
| gangneung | spring | daytime_full | 1/1 (1.000) | 0.69833333 | 0.14833333 |
| gangneung | spring | daytime_partial | 0/1 (0.000) | 0.50000000 | -0.05000000 |
| gangneung | spring | phase_selective | 1/1 (1.000) | 0.68000000 | 0.13000000 |
| gangneung | spring | post_sunrise_persistence | 0/1 (0.000) | 0.44500000 | -0.10500000 |
| gangneung | summer | daytime_full | 1/1 (1.000) | 0.69833333 | 0.14833333 |
| gangneung | summer | daytime_partial | 0/1 (0.000) | 0.50000000 | -0.05000000 |
| gangneung | summer | phase_selective | 1/1 (1.000) | 0.68000000 | 0.13000000 |
| gangneung | summer | post_sunrise_persistence | 0/1 (0.000) | 0.44500000 | -0.10500000 |
| gangneung | winter | daytime_full | 1/1 (1.000) | 0.69833333 | 0.14833333 |
| gangneung | winter | daytime_partial | 0/1 (0.000) | 0.50000000 | -0.05000000 |
| gangneung | winter | phase_selective | 1/1 (1.000) | 0.68000000 | 0.13000000 |
| gangneung | winter | post_sunrise_persistence | 0/1 (0.000) | 0.44500000 | -0.10500000 |
| suyeong | autumn | daytime_full | 1/1 (1.000) | 0.69833333 | 0.14833333 |
| suyeong | autumn | daytime_partial | 0/1 (0.000) | 0.50000000 | -0.05000000 |
| suyeong | autumn | phase_selective | 1/1 (1.000) | 0.68000000 | 0.13000000 |
| suyeong | autumn | post_sunrise_persistence | 0/1 (0.000) | 0.44500000 | -0.10500000 |
| suyeong | spring | daytime_full | 1/1 (1.000) | 0.69833333 | 0.14833333 |
| suyeong | spring | daytime_partial | 0/1 (0.000) | 0.50000000 | -0.05000000 |
| suyeong | spring | phase_selective | 1/1 (1.000) | 0.68000000 | 0.13000000 |
| suyeong | spring | post_sunrise_persistence | 0/1 (0.000) | 0.44500000 | -0.10500000 |
| suyeong | summer | daytime_full | 1/1 (1.000) | 0.69833333 | 0.14833333 |
| suyeong | summer | daytime_partial | 0/1 (0.000) | 0.50000000 | -0.05000000 |
| suyeong | summer | phase_selective | 1/1 (1.000) | 0.68000000 | 0.13000000 |
| suyeong | summer | post_sunrise_persistence | 0/1 (0.000) | 0.44500000 | -0.10500000 |
| suyeong | winter | daytime_full | 1/1 (1.000) | 0.69833333 | 0.14833333 |
| suyeong | winter | daytime_partial | 0/1 (0.000) | 0.50000000 | -0.05000000 |
| suyeong | winter | phase_selective | 1/1 (1.000) | 0.68000000 | 0.13000000 |
| suyeong | winter | post_sunrise_persistence | 0/1 (0.000) | 0.44500000 | -0.10500000 |

## Why the score structure is identical across region and season

Every region-season cell instantiates the same eight fixed v0.7 scenario specifications. For a given scenario type, activation, duration, load mismatch, phase selectivity, and all three policy/solar/transient flags are identical in all 12 cells. The frozen score does not consume region ID, season, station, timestamp, lamp count, rated load, or weather values; weather's frozen weight is zero. Therefore, equal score and decision rows across cells are a design consequence of the controlled generator, not empirical evidence that real regional or seasonal AMI behavior is identical.

## Feature availability observation

The matrix records raw feature availability rather than substituting absent values. `rated_load_kw` is unavailable for Chungju scenario rows and remains masked; it is not treated as a physical zero. Weather fields can be absent in the official context cache, and in this frozen detector they have no direct score contribution. This audit does not change those masks or infer operational meaning from them.

## Next-stage constraint

The two missed types may inform a future candidate design only after a separately generated, frozen calibration set is established. Reweighting, threshold changes, scenario changes, or any claim of field performance from this audit would contaminate the v0.7 baseline.
