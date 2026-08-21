# LightGuard v0.7 goal progress

## Goal

Measure whether the frozen v0.4 detector behaves consistently across a wider
regional and seasonal context without claiming unavailable field generalization.

## Implemented

- Three asset regions: Suyeong 204, Gangneung 339, Chungju 871 cabinets
- Four representative 2025 seasons: January, April, July, October
- Twelve region-season cells with seven days of KMA ASOS hourly context each
- KASI area sunrise, sunset, and civil twilight context for every cell
- Eight fixed scenarios per cell: four normal and four anomaly cases
- Frozen v0.4 detector configuration, including zero weather score weight
- Per-cell Wilson 95% intervals and explicit external-AMI boundary
- Deterministic artifact manifest and preflight contract

## Result interpretation

The detector produced the same result in every controlled cell: recall 0.50 and
FPR 0.00. This supports context invariance for this small controlled design, but
also exposes inadequate sensitivity to two weaker anomaly patterns. It is not
evidence of deployment performance in Gangneung or Chungju.

Chungju provides cabinet and lamp-count distribution but no positive rated-load
values in the current seed. v0.7 records zero rated-load coverage and performs no
imputation. External AMI validation remains unavailable.

## Evidence basis

- Rolling-origin and context-separated evaluation: Hyndman et al., Forecasting:
  Principles and Practice, https://otexts.com/fpp3/tscv.html
- Small-cell uncertainty: Wilson score intervals rather than point estimates alone,
  https://doi.org/10.1080/01621459.1927.10502953
- Factorial context coverage: NIST Engineering Statistics Handbook,
  https://www.itl.nist.gov/div898/handbook/pri/section5/pri597.htm

## Next evidence gate

Acquire verified cabinet-linked field AMI from at least one non-Busan region,
freeze the mapping before analysis, and run a prospective seasonal holdout. Until
then, product copy must use "controlled cross-context invariance" rather than
"regional generalization".
