# B-L-12 Missingness Denominator Reconciliation

## Decision

`RECONCILED_AS_SCOPE_DENOMINATOR_DIFFERENCE`

The legacy v0.1 quality table is a reduced processed release and has no row-level source provenance. v0.10 uses the complete ignored raw workbook under its frozen SHA and explicit April-June interval-end parser. The legacy denominator is retained as historical evidence, not substituted for the raw-source denominator.

| evidence | rows | rows with any measured-current gap |
|---|---:|---:|
| legacy processed v0.1 table | 8644 | 43 |
| v0.10 raw-workbook scope | 8735 | 46 |
| difference | 91 | 3 |

## Injection enforcement

- constructable B-L-12 pairs: `34`
- serialized changed-cell provenance records: `708`
- every used source cell is observed, finite, non-negative, and tagged `PASS_CONSTRAINED_CURRENT_ONLY`.
- incomplete source/target intervals remain `not_constructable`; no missing value is filled or converted to zero.
- v0.10 raw counts supersede the legacy processed denominator for this experiment; no claim is made that the two releases contain identical row populations.
