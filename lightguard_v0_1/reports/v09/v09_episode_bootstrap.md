# v0.9 episode-cluster bootstrap

## Scope

This is a controlled generated episode-separated confirmatory analysis only. It is not field AMI accuracy, fault truth, or a promotion retuning input.

## Frozen inputs

- Selected candidate: `H1`
- Candidate configuration SHA-256: `b536f8ca68222662c717cd27a6af4c3c64a3330782b0545503df6e4aff3e6232`
- Confirmatory episodes: `24`; cases: `576`
- Bootstrap resamples: `2000`; fixed seed: `20260901`
- Resampling unit: complete episode. Each resample draws 24 episode IDs with replacement and retains every case in each drawn episode.
- Comparator: `threshold_only`; delta is candidate minus comparator. Lower deltas are favorable for FPR metrics, higher deltas are favorable for recall/AP.
- No threshold, detector, configuration, scenario, or confirmatory result was changed.

## Observed metrics and bootstrap delta intervals

| Candidate | Metric | Observed candidate | Observed threshold_only | Observed delta | Bootstrap mean delta | 2.5% | 97.5% |
|---|---|---:|---:|---:|---:|---:|---:|
| H1 | recall | 0.91666667 | 1.00000000 | -0.08333333 | -0.08333333 | -0.08333333 | -0.08333333 |
| H1 | fpr | 0.00000000 | 0.33333333 | -0.33333333 | -0.33333333 | -0.33333333 | -0.33333333 |
| H1 | hard_negative_fpr | 0.00000000 | 0.36363636 | -0.36363636 | -0.36363636 | -0.36363636 | -0.36363636 |
| H1 | average_precision | 1.00000000 | 0.99334089 | 0.00665911 | 0.00665911 | 0.00665911 | 0.00665911 |
| H2 | recall | 0.91666667 | 1.00000000 | -0.08333333 | -0.08333333 | -0.08333333 | -0.08333333 |
| H2 | fpr | 0.00000000 | 0.33333333 | -0.33333333 | -0.33333333 | -0.33333333 | -0.33333333 |
| H2 | hard_negative_fpr | 0.00000000 | 0.36363636 | -0.36363636 | -0.36363636 | -0.36363636 | -0.36363636 |
| H2 | average_precision | 1.00000000 | 0.99334089 | 0.00665911 | 0.00665911 | 0.00665911 | 0.00665911 |
| H3 | recall | 0.91666667 | 1.00000000 | -0.08333333 | -0.08333333 | -0.08333333 | -0.08333333 |
| H3 | fpr | 0.00000000 | 0.33333333 | -0.33333333 | -0.33333333 | -0.33333333 | -0.33333333 |
| H3 | hard_negative_fpr | 0.00000000 | 0.36363636 | -0.36363636 | -0.36363636 | -0.36363636 | -0.36363636 |
| H3 | average_precision | 1.00000000 | 0.99334089 | 0.00665911 | 0.00665911 | 0.00665911 | 0.00665911 |

## Interpretation boundary

The percentile intervals quantify variation across resampled generated episodes under the frozen confirmatory decisions. They do not establish generalization to unobserved field AMI data or causal weather effects. Weather remains context-only with weight `0.0`.
