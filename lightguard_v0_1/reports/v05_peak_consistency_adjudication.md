# v0.5 Peak Consistency Adjudication

## Decision

The historical v0.4 result remains **2/6**. It compared a window-wide maximum individual phase with a canonical per-record sum of available phases, so four three-phase events were not semantically comparable.

The separate adjudicated replay-integrity metric compares like for like: the maximum, within canonical event labels, of `sum(non-null I1, I2, I3)`. It is **6/6**. Neither metric is field accuracy or fault confirmation.

| event | legacy | primary cause | secondary cause | adjudicated |
|---|---|---|---|---|
| AMI-EVT-237615b73a | pass | AGGREGATION_DEFINITION | MISSING_DATA | pass |
| AMI-EVT-d406cc5296 | mismatch | AGGREGATION_DEFINITION | NONE | pass |
| AMI-EVT-fda2dd8737 | mismatch | AGGREGATION_DEFINITION | NONE | pass |
| AMI-EVT-f394b2a542 | mismatch | AGGREGATION_DEFINITION | NONE | pass |
| AMI-EVT-4ada00d8f3 | mismatch | AGGREGATION_DEFINITION | NONE | pass |
| AMI-EVT-d706634ed1 | pass | AGGREGATION_DEFINITION | MISSING_DATA | pass |

## Guardrails

- All 110 replay rows match the ignored original workbook values.
- Missing phases remain missing and are never coerced to zero.
- The old result is preserved rather than rewritten.
- Competition AMI is not joined to Busan KASI/KMA or Suyeong assets.
- The workbook does not explicitly define current timestamp start/end semantics; no current timestamp is shifted.
