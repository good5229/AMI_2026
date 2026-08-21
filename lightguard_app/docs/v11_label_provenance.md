# v0.11 Label Provenance

## Current route

The full local source audit selected **Route C**. No record combines an independently confirmed field outcome or operational discrepancy with a verified target AMI/cabinet key and usable time alignment.

## Evidence hierarchy

| label | meaning | current availability |
|---|---|---|
| `GOLD_CONFIRMED_FAULT` | independently confirmed field outcome with verified target and time linkage | unavailable |
| `SILVER_OPERATIONAL_DISCREPANCY` | independently recorded controller, inspection, complaint, or maintenance discrepancy with verified linkage | unavailable |
| `EXPERT_REVIEWED_ANOMALY_SIGN` | blinded trace review without field confirmation | template prepared; labels not collected |
| `HIGH_CONFIDENCE_PROXY_ANOMALY_SIGN` | agreement of at least two predeclared AMI proxy-rule families | v0.11 descriptive evidence |
| `SINGLE_PROXY_ANOMALY_SIGN` | one AMI proxy-rule family fires | v0.11 descriptive evidence |
| `UNLABELED` | no usable outcome evidence | default for raw AMI |

## Claim boundary

AMI-derived signs may support concordance, overlap, enrichment, ranking, and candidate-density descriptions. They do not support actual fault accuracy, fault recall, precision, FPR, specificity, prevalence, or confirmed-cause claims.

The six prior cases are **previously identified anomaly-sign candidates**. They are not six actual faults. A later field-label import must preserve this provenance and expose any field-confirmed subset separately.
