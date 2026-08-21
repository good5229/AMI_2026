# LightGuard v0.10 Meter-Day Cluster Bootstrap

- seed: `20261020`
- replicates: `2000`
- whole-pair clusters: `182`
- 15-minute row bootstrap: `prohibited`

| metric | point | percentile 95% |
|---|---:|---:|
| IRR | 0.97315436 | [0.94557823, 0.99363057] |
| Benign escalation | 0.00000000 | [0.00000000, 0.00000000] |
| Median score uplift | 0.25000000 | [0.25000000, 0.25000000] |

## Leave-one-meter-out

| omitted meter | IRR | benign escalation | median uplift |
|---|---:|---:|---:|
| B-L-12 | 1.00000000 | 0.00000000 | 0.25000000 |
| B-L-13 | 0.96666667 | 0.00000000 | 0.25000000 |
| B-L-14 | 0.96551724 | 0.00000000 | 0.25000000 |
| B-L-35 | 0.96694215 | 0.00000000 | 0.25000000 |
| B-L-9 | 0.96610169 | 0.00000000 | 0.25000000 |

Intervals describe the frozen semi-synthetic paired sample; they do not establish field-fault uncertainty.
