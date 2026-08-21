# v0.17 Data Quality Report

| source | observed rows | portal rows | status |
|---|---:|---:|---|
| D1 | 101,843 | 101,843 | MATCH |
| D2 | 71,973 | 71,973 | MATCH |
| D3 | 105,449 | 105,449 | MATCH |
| D4 | 614,241 | 145,365 | MISMATCH_REQUIRES_SOURCE_CONFIRMATION |
| D5 | 2,519 | 2,519 | MATCH |

## D1

- Unique management IDs: 40,148
- Duplicate event signatures excluding sequence: 673
- Valid durations: 101,839; negative durations: 4; unresolved: 0

## Join

- Verdict: `PARTIAL_JOIN`
- Exact ID overlap: 39,974/40,148 (99.57%)
- Ambiguous matched IDs: 137; unmatched IDs: 174
- Unambiguous exact-ID join candidates: 100,561
- Spatial analysis: `NO_SPATIAL_JOIN`; no hotspot result is published until semantic identity is verified.

## Blocking discrepancy

D4 local file has 614,241 rows while the official page advertises 145,365. D4 remains aggregate context and is not used for event-level or cost claims until the provider confirms the snapshot semantics.
