# LightGuard v0.5 Causal Walk-Forward Summary

Actual anonymized AMI contains no confirmed fault labels. Coverage below refers only to six known detector candidates, not field recall or accuracy.

- Meters: B-L-9, B-L-12, B-L-13, B-L-14, B-L-35
- Evaluation range: 2026-04-01 through 2026-06-30
- Causal baseline rule: every baseline row has timestamp earlier than the evaluation day.
- Warm-up policy: no baseline is fabricated; unavailable days are marked `not_evaluable_warmup`.
- Existing detector comparison: full-sample medians include future observations and are retained only as a leakage-marked comparison.

| baseline | candidates | evaluable meter-days | warm-up meter-days | density | canonical-6 coverage | full-sample Jaccard |
|---|---:|---:|---:|---:|---:|---:|
| 7d | 6 | 420 | 35 | 0.014286 | 1.000000 | 1.000000 |
| 14d | 6 | 385 | 70 | 0.015584 | 1.000000 | 1.000000 |
| 30d | 6 | 305 | 150 | 0.019672 | 1.000000 | 1.000000 |
| expanding | 6 | 420 | 35 | 0.014286 | 1.000000 | 1.000000 |

Full-sample comparison produced 6 candidates and covered 6/6 known detector candidates.
