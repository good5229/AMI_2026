# LightGuard v0.5 Real-Data Robustness Summary

## Frozen Baseline

- v0.3/v0.4 frozen hashes and weights remain unchanged.
- Weather scoring remains disabled (`0.0`, context-only).

## Actual AMI Peak Forensics

- Legacy peak consistency: 2/6.
- Adjudicated like-for-like replay integrity: 6/6.
- Root cause for all six: `AGGREGATION_DEFINITION`; missing phases remain explicit for B-L-13/B-L-35.

## Causal Walk-Forward

- Five meters, 2026-04-01 through 2026-06-30.
- 7/14/30-day and expanding baselines use only observations earlier than each evaluation day.
- Every window reproduced 6/6 known detector candidates; this is not field recall or accuracy.
- Full-sample detector is retained only as a comparison marked with future leakage.

## Robustness

- Random missingness 20% coverage: 0.833333.
- 30/60-minute downsample coverage: 1.000000 / 1.000000.
- 120-minute contiguous gap coverage: 0.000000.
- Missing measurement channels are never coerced to zero.

## Sensitivity

- Classification: Knife-edge or locally sensitive.
- Most sensitive parameter family: activation.
- Activation +20% diagnostic: normal FPR 0.018987 -> 0.069620; candidates 56. No retuning or promotion.
- Frozen v0.4 weights were not changed or retuned.

## Operational Evidence

- Public evidence supports the cabinet as an operational maintenance key.
- Suyeong per-dispatch cost and ROI conversion remain prohibited because a matching denominator is unavailable.

## Independent QA

- Status: available.

## Claims

Allowed: controlled validation, independent holdout, past-only replay, known-candidate coverage, technical robustness, public operational evidence.
Prohibited: field accuracy, actual municipal AMI accuracy, true fault rate, dispatch savings, public budget savings.
