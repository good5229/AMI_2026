# LightGuard v0.9 Specificity Validation

## Product-facing result

The Flutter evidence card reads a generated release summary rather than embedding detector values in Dart. It displays the untouched episode-separated confirmatory sample size, selected candidate, recall, normal FPR, hard-negative FPR, worst region-season recall, and Wilson 95% intervals.

## Required boundaries

- The result is a controlled generated validation outcome, not field AMI accuracy.
- Calibration uses 24 official-context episodes and 384 cases. Confirmation uses 24 different episodes and 576 cases.
- Episode, calendar-date, KMA observation, case, signal-parameter, and asset overlap are zero.
- Weather remains context-only with weight `0`.
- Missing rated load, including Chungju, is never imputed.
- Six anonymized competition AMI events are technical regression cases without fault truth labels and do not affect promotion.
- If confirmatory gates fail, the summary must carry `selected_candidate: null` and the card must show `Candidate not promoted`.

## Promotion scope

Passing v0.9 gates promotes H1 only as the controlled-validation candidate represented in this evidence package. It does not authorize production deployment, municipal field-accuracy claims, or automatic maintenance action.
