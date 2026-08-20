# LightGuard v0.9 Hard-Negative Specificity Recovery

## Decision

- Calibration-selected candidate: `H1`
- Confirmatory-selected candidate: `H1`
- Controlled promotion gate: `PASS`
- Retuning after holdout: `false`
- Claim boundary: controlled generated scenarios only; no field AMI accuracy or production-readiness claim.

## Freeze and episode separation

- Frozen v0.8 git baseline: `8772c2759d16ed7a6e669b940880e10cb242d1d6`
- Official-context episodes: `48` (`24` calibration / `24` confirmatory)
- Calibration cases: `384`; confirmatory cases: `576`
- Episode/date/KMA observation/case/signal/asset overlap: `0`
- Source year: `2025`; future 2026 context episodes: `0`
- KASI completion: official anchors plus official KASI web-calculator JavaScript with source hashes; no internal solar fallback.

## Confirmatory metrics

| metric | result | Wilson 95% |
|---|---:|---|
| recall | 0.91666667 | [0.87900183, 0.94336249] |
| normal FPR | 0.0 | [0.0, 0.01316283] |
| hard-negative FPR | 0.0 | [0.0, 0.01434229] |
| worst region-season recall | 0.91666667 | descriptive minimum |
| average precision | 1.0 | episode bootstrap reported separately |
| abstention | 0.0 | action coverage measure |

## Specificity result

The threshold-only comparator retained high recall but produced substantial normal and hard-negative false positives. H1's second-stage solar, persistence, load, phase, policy, and contradiction evidence recovered specificity without using weather in the score. H2/H3 preserved the detector result while exposing missing-data abstention and bounded queue ordering.

## Statistical evidence

- Wilson intervals are reported for recall, FPR, hard-negative FPR, and subgroup rates.
- Episode-cluster bootstrap resamples the 24 confirmatory episode units 2,000 times with seed `20260901`.
- Region, season, weather regime, episode, and region-season interaction outputs are controlled descriptive effects, not municipal field effects.
- Solar-boundary and missing-feature analyses are separate release artifacts.

## Actual AMI regression

- Replayed events: `6` anonymized competition AMI windows.
- Field truth labels: unavailable for all rows.
- Promotion-gate use: false for all rows.
- New actions: `inspect=2, normal=2, observe=2`.
- These rows demonstrate how the frozen decision contract behaves when linked to real intervals; they do not measure recall, specificity, or fault accuracy.

## Data policies

- Weather weight: `0`; KMA remains episode/context evidence only.
- Rated-load imputation: none. Chungju unavailable load remains unavailable.
- External Gangneung/Chungju cabinet-linked AMI: unavailable.
- Scenario signals, municipal assets, and anonymized competition AMI remain distinct.

## Product boundary

Flutter displays the episode-separated sample size, recall, normal FPR, hard-negative FPR, worst-cell recall, Wilson intervals, and controlled-only disclaimer. A failed future rerun must emit `selected_candidate: null` and display `Candidate not promoted`.
