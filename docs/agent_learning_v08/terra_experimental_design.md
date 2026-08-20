# Agent Learning Note

## Role

Subagent B: design the v0.8 blocked fractional calibration and independent confirmatory experiment, including separation and uncertainty rules. This note was completed before generating the design matrix.

## Model actually used

`gpt-5.6-terra`

## Sources

- URL: https://www.itl.nist.gov/div898/handbook/pri/section3/pri3.htm
  - Institution/author: NIST/SEMATECH e-Handbook of Statistical Methods
  - Checked: 2026-08-20
  - Key point: experimental design starts by declaring objectives, factor levels, and the design type.
  - LightGuard use: fixes success/failure rules before candidate results and treats region x season as planned blocks.

- URL: https://www.itl.nist.gov/div898/handbook/pri/section3/pri333.htm
  - Institution/author: NIST/SEMATECH
  - Checked: 2026-08-20
  - Key point: a two-level full factorial has 2^k runs and becomes inefficient with five or more factors.
  - LightGuard use: rules out complete crossing of context, asset, signal, and availability factors.

- URL: https://www.itl.nist.gov/div898/handbook/pri/section3/pri334.htm
  - Institution/author: NIST/SEMATECH
  - Checked: 2026-08-20
  - Key point: a suitably chosen fractional factorial can be balanced and orthogonal for screening.
  - LightGuard use: uses deterministic balanced fractional allocation and records that high-order interactions are not identified.

- URL: https://itl.nist.gov/div898/handbook/prc/section2/prc241.htm
  - Institution/author: NIST/SEMATECH
  - Checked: 2026-08-20
  - Key point: Wilson intervals are appropriate across a wide range of sample sizes/proportions and avoid impossible negative lower bounds.
  - LightGuard use: predeclares Wilson 95% intervals for recall, FPR, anomaly-type, and cell proportions.

- URL: https://www.itl.nist.gov/div898/handbook/pri/section3/pri33a.htm
  - Institution/author: NIST/SEMATECH
  - Checked: 2026-08-20
  - Key point: mixed-level factorials need deliberate allocations because factors can have two, three, or four levels.
  - LightGuard use: documents mixed levels instead of pretending severity, duration, solar position, and availability form a simple 2-level design.

- URL: https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm
  - Institution/author: NIST/SEMATECH
  - Checked: 2026-08-20
  - Key point: blocking controls known nuisance variation; within-block factor occurrence should be balanced, with remaining variation randomized.
  - LightGuard use: fixes region x season as blocks and uses separately seeded allocation inside them.

- URL: https://www.itl.nist.gov/div898/handbook/eda/section3/bootplot.htm
  - Institution/author: NIST/SEMATECH
  - Checked: 2026-08-20
  - Key point: bootstrap resampling estimates uncertainty for statistics with difficult analytic distributions; 500-1000 resamples are typical, but the method has limits.
  - LightGuard use: requires fixed-seed 1,000 cell-stratified resamples and keeps repeated Suyeong confirmation assets as dependence units.

- URL: https://scikit-learn.org/stable/modules/cross_validation.html
  - Institution/author: scikit-learn developers
  - Checked: 2026-08-20
  - Key point: grouped splits keep a group out of both train and validation; stratification can hide metric variability and should not be overinterpreted.
  - LightGuard use: split isolation is stronger than label stratification: assets, factor tuples, seeds, and signal parameters are all non-overlapping across calibration and confirmation.

## Risks

- All v0.8 rows are controlled injections, not real regional AMI observations.
- Scenario factors are deliberately not fully crossed, so unmodeled/high-order interaction effects are aliased and cannot support causal claims.
- Suyeong has 204 assets but 240 requested split-row exposures. Asset pools are disjoint across splits, but confirmatory reuse within its own pool creates clustered rows.
- Chungju source rows all have fixture_count 0 and no usable rated load. Inventing three strata or imputing load would fabricate information.
- Stratification can make summaries look less variable; later uncertainty analysis must retain cell and asset-pool structure.

## Adopted rules

1. Keep exact requested totals: 288 calibration and 432 confirmation rows, with 24/36 rows in every region-season cell and 18 normal/18 abnormal confirmation rows.
2. Use region x season as fixed blocks; use deterministic balanced fractional allocation inside blocks.
3. Freeze and verify the matrix with stable row hashes and one matrix SHA-256 before tuning.
4. Keep v0.7 96 cases regression-only; do not import them into the generator.
5. Require cross-split disjointness in case ID, seed, asset pool, factor tuple, and signal parameter ID.
6. Preserve Chungju `unavailable_no_imputation`: blank rated-load values, explicit feature mask, and a single observed all-zero fixture-count stratum.
