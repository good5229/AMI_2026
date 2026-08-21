# LightGuard v0.18 Retrospective Operational Triage Utility

## 1. Freeze

- v0.17: frozen `ON-A`; D1 hash `a21d87de8da61d5793fd87655efbd857be5990e7188aaec8d913c4ced788cbd0`.

## 2. Temporal Split

- Development: 2020-01-01 to 2023-12-01, 71,162 asset-day episodes; 30-day year-end embargo follows.
- Validation: 2024-01-01 to 2024-12-01, 16,618 episodes; 30-day year-end embargo follows.
- Confirmatory: 2025-01-01 to 2025-07-10, 9,145 fully observed 30-day episodes.

## 3. Outcomes

| split | repeat-30 prevalence |
|---|---:|
| development | 11.1% |
| validation | 9.0% |
| confirmatory | 7.3% |

Long-resolution and recurrence are operational outcomes, not physical fault labels.

## 4. Causal Features

Receipt type, district, month/weekday, prior 30/90/365-day records, elapsed days, already-completed long histories, open prior cases, start-of-day backlog, and prior 7/30-day intake are used. Leakage audit: `PASS`.

## 5. Prediction

| model | holdout AP | top10 precision | top10 enrichment | Brier |
|---|---:|---:|---:|---:|
| B0_NO_PREDICTION | 0.073 | 7.3% | 1.00x | 0.069 |
| B1_REPEAT_AWARE_RULE | 0.106 | 17.8% | 2.45x | 0.067 |
| B2_LOGISTIC | 0.199 | 22.6% | 3.12x | 0.064 |

## 6. Primary Outcome

- Selected before holdout: `REPEAT_WITHIN_30D`.
- Model selected on validation: `B2_LOGISTIC`.
- Confirmatory result: AP 0.199, top-decile enrichment 3.12x, asset-cluster bootstrap lower bound 2.71x.

## 7. Queue Capacity

- C25=0 (`NONREVIEWING_SCENARIO`), C50=62, C75=80 observed-record review opportunities/day.

## 8. Queue Policies

At C50, Q0 burden restricted mean review delay is 0.54 days and Q2 is 0.57 days. This is simulated time-to-review, not actual repair time.

## 9. Operational Utility

- Grade: **OU-B**
- Product status: `LIMITED_OPERATIONAL_PRIORITY_EVIDENCE`
- FIFO comparison: burden delay improvement -0.03 days; nonburden change -0.01 days.

## 10. Distribution

District and receipt-route distributions are reported with support thresholds in `v18_fairness_distribution.csv`. Year shift is material: repeat-30 prevalence declines from 11.1% to 7.3%.

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
