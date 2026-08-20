# LightGuard v0.8 Weak-Signal Detector Recovery Final Summary

## 1. v0.7 Freeze

- Preflight: PASS
- Frozen git SHA: `383c91e2c22d9364232c80683b6f8e4b6dc09d35`
- Baseline controlled recall/FPR: 0.50 / 0.00 on the separate v0.7 set
- Role: regression-only; not used for v0.8 tuning

## 2. v0.7 Failure Forensics

- Missed: `post_sunrise_persistence` (score 0.445, margin -0.105)
- Missed: `daytime_partial` (score 0.500, margin -0.050)
- Cause: insufficient activation-duration accumulation; region, season, weather,
  and asset values were not score inputs.

## 3. Experimental Design

- Calibration: 288 cases, SHA `b9825d7b8d336de9421a5941d2c7f069202b3f402fa4090b2837abb7d3a38b2f`
- Confirmatory: 432 cases, SHA `71a4d7099be61f073f8411acd3b0af999dd672060dde9621513e0505e32c1a1d`
- Design: 3 regions x 4 seasons, balanced blocked fractional allocation
- Calibration and confirmatory case IDs, seeds, factor tuples, signal parameter IDs,
  and asset pools are disjoint.

## 4. Candidate Detector

- C1: expected-operation residual plus activation-duration interaction, load mismatch,
  and phase selectivity
- C2: C1 plus missing-feature mask, availability handling, and abstention
- C3: C2 plus exploratory KMA weather modifier
- Threshold: fixed at 0.55; never lowered

## 5. Same-Holdout Confirmatory

| model | recall | FPR | AP | balanced accuracy | worst-cell recall | abstention | gate |
|---|---:|---:|---:|---:|---:|---:|---|
| frozen_v04 | 0.5046 | 0.3148 | 0.6991 | 0.5949 | 0.3333 | 0.0000 | baseline |
| C1 | 0.7315 | 0.1111 | 0.9238 | 0.8102 | 0.7222 | 0.0000 | FAIL: FPR > 0.05 |
| C2 | 0.7315 | 0.1111 | 0.8792 | 0.8102 | 0.7222 | 0.0139 | FAIL: FPR > 0.05 |
| C3 | 0.6991 | 0.1019 | 0.8940 | 0.7986 | 0.6111 | 0.0185 | FAIL: FPR > 0.05 |

No candidate passed the predeclared FPR <= 0.05 and hard-negative FPR <= 0.05
constraints. C1/C2 improved recall from 0.5046 to
0.7315, but FPR remained 0.1111; therefore
`selected_candidate = null` and no v0.8 candidate is promoted.

## 6. Per-Anomaly Recall

| anomaly type | frozen v0.4 | C1 experimental |
|---|---:|---:|
| deep_day_full_activation | 0.1667 | 0.5833 |
| deep_day_partial_activation | 0.5000 | 0.6667 |
| moderate_load_mismatch | 0.2500 | 0.5000 |
| partial_activation_long_persistence | 0.5000 | 1.0000 |
| phase_anomaly_moderate_activation | 0.7083 | 1.0000 |
| phase_selective_activation | 0.5000 | 0.5000 |
| post_sunrise_persistent_activation | 0.6111 | 0.6667 |
| weak_long_duration_activation | 0.7500 | 1.0000 |

## 7. Cross-Context

- C1 region recall range: 0.0278
- C1 season recall range: 0.0185
- C1 region x season recall range: 0.0556
- Effects are controlled generated-factor effects, not actual municipal effects.

## 8. Statistical Uncertainty

- Wilson intervals below use the full 216 abnormal / 216 normal holdout samples;
  abstentions are not counted as correct detections.
- Wilson recall 95% CI, frozen v0.4: [0.43845732, 0.57064014]
- Wilson recall 95% CI, C1: [0.66871275, 0.78616051]
- Wilson FPR 95% CI, C1: [0.07581156, 0.16000137]
- C2 evaluable-only recall/FPR after excluding abstentions:
  0.7524 / 0.1111
- Bootstrap: 1,000 fixed-seed cell/class-stratified resamples; see
  `v08_uncertainty_summary.md`.

## 9. Chungju Missing Load

- Official recovery status: per-cabinet load `NOT_RECOVERABLE` from current public data
- Imputation: none
- Asset stratum: unstratified because rated load is unavailable and fixture count is
  zero in every current source row
- Paired feature-removal cases: 1728; decision changes: 63;
  abstentions: 75

## 10. Weather Candidate

- C2 recall/FPR/AP: 0.7315 / 0.1111 / 0.8792
- C3 recall/FPR/AP: 0.6991 / 0.1019 / 0.8940
- Decision: weather remains `context_only`

## 11. External AMI Readiness

- Gangneung: `REQUEST_REQUIRED`
- Chungju: `REQUEST_REQUIRED`
- Public cabinet-linked interval AMI: not found
- Next step: authorized cabinet-to-meter mapping plus interval phase/current and
  maintenance labels

## 12. Flutter/Test/Build

- Independent QA: initial integrated command was blocked by restricted Flutter SDK
  cache permissions; the approved-permission rerun resolved it.
- Final independent QA: PASS with non-critical residual risks; all 11 gates met
- Final approved-permission v0.8 preflight: PASS
- Flutter analyze: no issues
- Flutter tests: 21 passed
- Web release build: PASS
- Android release APK: PASS, 52.2MB

## 13. Claims Allowed

- Controlled regional-seasonal experiment was expanded and independently held out.
- Weak-signal recall improved in an experimental candidate.
- The candidate failed the predeclared FPR gate and was not promoted.
- Missing-feature behavior and weather incremental value were explicitly tested.

## 14. Claims Prohibited

- Actual regional generalization or field accuracy
- Gangneung/Chungju AMI performance
- Actual fault detection rate or cost savings
- Production readiness of C1, C2, or C3

## 15. Remaining Risks

- Hard-negative false positives exceed the acceptance limit.
- Generated scenario dependence remains despite blocked/bootstrap analysis.
- Calibration and confirmatory splits share the same twelve official KMA/KASI
  context episodes. C3 was not selected and weather remains context-only; a future
  weather candidate requires date/episode-separated context.
- No external cabinet-linked field AMI exists for confirmation.

## 16. Next Recommended Step

Keep v0.4 as the product baseline, carry the failed v0.8 candidate evidence forward
without retuning this holdout, acquire actual cabinet-linked AMI, and design a new
v0.9 calibration set focused on pre-sunset and hard-negative discrimination.
