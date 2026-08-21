# LightGuard v0.5 Data-Quality Robustness

Controlled metrics and actual replay metrics are reported separately. Actual six-event coverage is not field recall or accuracy.

| stress | controlled recall | FPR | P@20 | actual coverage | interval IoU | phase consistency | candidate Jaccard |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline | 0.978261 | 0.018987 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| missing_5pct | 0.913043 | 0.012658 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| missing_10pct | 0.934783 | 0.018987 | 1.000000 | 1.000000 | 0.972222 | 1.000000 | 1.000000 |
| missing_20pct | 0.782609 | 0.012658 | 1.000000 | 0.833333 | 0.750000 | 0.833333 | 0.833333 |
| gap_30m | 0.978261 | 0.018987 | 1.000000 | 0.166667 | 0.111111 | 0.166667 | 0.166667 |
| gap_60m | 0.760870 | 0.018987 | 1.000000 | 0.166667 | 0.055556 | 0.166667 | 0.166667 |
| gap_120m | 0.478261 | 0.018987 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| downsample_30m | 0.978261 | 0.018987 | 1.000000 | 1.000000 | 0.722222 | 1.000000 | 1.000000 |
| downsample_60m | 0.891304 | 0.037975 | 1.000000 | 1.000000 | 0.611111 | 1.000000 | 1.000000 |
| drop_i1 | 0.956522 | 0.018987 | 1.000000 | 0.666667 | 0.500000 | 0.666667 | 0.666667 |
| drop_i2 | 0.956522 | 0.018987 | 1.000000 | 0.833333 | 0.666667 | 0.833333 | 0.833333 |
| drop_i3 | 0.956522 | 0.018987 | 1.000000 | 1.000000 | 0.833333 | 1.000000 | 1.000000 |
| duplicate_timestamp | 0.978261 | 0.018987 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| duplicate_conflict | 0.978261 | 0.018987 | 1.000000 | 0.666667 | 0.416667 | 0.666667 | 0.666667 |
| measurement_channel_missing | 0.782609 | 0.018987 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

Missing channels are never interpreted as zero current. Stress outcomes measure technical replay stability only.
