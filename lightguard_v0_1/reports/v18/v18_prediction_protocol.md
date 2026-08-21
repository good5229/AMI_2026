# v0.18 Prediction Protocol

Primary outcome was frozen as `REPEAT_WITHIN_30D` before confirmatory scoring. Features use only start-of-day observable D1 information. Same-day order, current outcome, future recurrence, asset identifiers, D2-D5, AMI, staffing, causes, and severity are excluded.

Development: 2020-01-01 to 2023-12-01 (71,162 episodes). Validation: 2024-01-01 to 2024-12-01 (16,618). The remaining 30 days of each year are embargoed. Confirmatory: 2025-01-01 to 2025-07-10 (9,145). B1 is a 90-day repeat-history rule. B2 is L2 logistic regression. Validation top-decile enrichment selects once; holdout refit is zero.

Primary metrics are average precision, proportion-based top-K precision/recall/enrichment, Brier score, and 10-bin ECE. These evaluate repeat-record operational concentration, not physical fault detection.
