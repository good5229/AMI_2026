# v0.13 Cross-Dataset Summary

## Scope
External labeled electrical anomaly mechanism evidence only; never streetlight field accuracy or actual fault probability.

| Dataset | Gate | Result | Permitted interpretation |
|---|---|---|---|
| MAD | DG-A primary | NOT_EVALUABLE_INCOMPLETE_COVERAGE / NO_EV_GRADE_NOT_EVALUABLE | Named-dataset external electrical anomaly discrimination only |
| REFIT | DG-B secondary | BLOCKED_EXTERNAL_DATA | Blocked; no metric published |
| UCR ItalianPowerDemand | DG-C secondary | WITHHELD_LICENSE_UNKNOWN | Licence withheld; no metric published |
| Zenodo pseudo-labelled | DG-D | EXCLUDED | Never Gold, calibration, or confirmatory evidence |

## MAD sealed result
- SC3 balanced accuracy: 0.5200448502146089
- z-score comparator balanced accuracy: 0.665982584137444
- Primary gate: NOT_EVALUABLE_INCOMPLETE_COVERAGE
- External empirical grade: NO_EV_GRADE_NOT_EVALUABLE
- SC3 coverage: 5400/5414 (0.9974141115626154)
- z-score comparator coverage: 5414/5414 (1.0)
- Opaque repository classes remain opaque and are not assigned fault mechanisms.
- LG-S3: UNAVAILABLE_NORMALIZATION_PROVENANCE.
- Track B: NOT_ASSESSABLE because MAD has no retained meter IDs or timestamps.

## Non-transfer boundary
No table above estimates Suyeong-gu streetlight field accuracy, recall, specificity, asset condition, confirmed fault, or actual fault probability. Human review remains pending.
