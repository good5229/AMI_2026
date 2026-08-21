# LightGuard v0.5 Meter Generalization Audit

These are descriptive meter/data-quality profiles, not meter fault rates.

| meter | cadence | measured phases | energy availability | duplicate timestamps | 24:00 normalized | canonical candidates |
|---|---:|---:|---:|---:|---:|---:|
| B-L-9 | 15 min | 3 | 0.999428 | 0 | 91 | 2 |
| B-L-12 | 15 min | 3 | 0.999886 | 0 | 91 | 0 |
| B-L-13 | 15 min | 1 | 0.251151 | 0 | 91 | 1 |
| B-L-14 | 15 min | 3 | 0.999542 | 0 | 91 | 2 |
| B-L-35 | 15 min | 1 | 0.251323 | 0 | 91 | 1 |

## Guardrails

- B-L-12's persistent daytime structure is handled by a meter-specific OFF baseline, never a global current threshold.
- B-L-13 and B-L-35 have one measured current phase and sparse energy cadence; absent phases remain missing rather than zero.
- Monthly drift and candidate density are descriptive operational signals only.
