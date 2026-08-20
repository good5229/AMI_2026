# LightGuard v0.10 Independent Audit

Date: 2026-08-20 (Asia/Seoul)

## Result

`PASS with residual risks`

Severity counts: Critical 0, High 0, Medium 0, Low 2, Informational 2.

## Scope and execution boundary

Fresh final independent QA after the hung QA session. Requested model: `gpt-5.6-luna`; observable runtime: GPT-5/Codex. The existing v0.10 rerun log record was present before report changes. Only `python3 scripts/test_v10_artifacts.py` was run, and it returned `v0.10 artifact contracts: PASS`. No Flutter command, build, full preflight, Git mutation, `.env` access, or raw-source value inspection was performed.

## Gate matrix

| Gate | Result | Evidence |
|---|---|---|
| C1 B-L-12 reconciliation | PASS | 8,644 legacy rows / 43 gap rows versus 8,735 v0.10 raw-scope rows / 46 gap rows; 91-row scope difference is documented; 34 constructable pairs and 708 provenance cells are reported. |
| C2 injection provenance | PASS | All 182 constructable manifest rows satisfy provenance-count equality and complete cell fields; 18 rows remain `not_constructable`. |
| C3 causal shadow audit | PASS | 43,582 origin rows; representative head/tail inspection plus aggregate contract check; all causal-proof flags true; state-before/state-after/history hashes present. |
| Prefix invariance | PASS | `prefix_mismatches=0`; `prefix_invariance=PASS`. |
| Pre-canonical isolation | PASS | `canonical_loaded_after_seal=true`; canonical data is reporting-only under the protocol. |
| v0.9 freeze / H1 | PASS | Frozen hashes verify; H1 remains selected and Track-A retuning is prohibited. |
| R1 | PASS | Optional R1 config and results are absent; `r1_triggered=false`. |
| Truth and context integrity | PASS | No field truth, normal-truth relabeling, energy reconstruction, municipal/KMA/KASI/rated-load join, or maintenance/fault fabrication. |
| Flutter claim boundary | PASS by source inspection | Summary asset, card, documentation, and unit-test source preserve the semi-synthetic/no-field-truth boundary. Runtime was not rerun by instruction. |

## C1-C3 findings

The B-L-12 report correctly treats the discrepancy as a denominator/scope difference rather than reconciling by overwriting one release with another. The injection manifest is fail-closed: incomplete slices are excluded, not imputed. The contract’s all-row checks ensure every constructable row’s `cell_provenance` count equals `copied_cell_count`, with identity current semantics, finite non-negative observed source quality, scale 1.0, constrained physical review, and unchanged energy.

The shadow audit is causally adequate for its stated estimand. The origin population is 43,582, and the contract confirms causal proof for every origin row. The audit records zero prefix mismatches, no duplicate same-time permutation issue, and a post-seal canonical load. The protocol explicitly excludes later rows, cross-meter state, future derived statistics, and canonical intervals from causal state construction.

## Claim boundary

The permitted claim is frozen-H1 transport validation over paired current-only counterfactuals on anonymized real AMI backgrounds, plus past-only shadow replay behavior. The prohibited claims remain field accuracy, actual fault recall, real-background FPR/specificity, municipal performance, and production readiness. Anonymous AMI has no maintenance or fault truth; unmodified background is not labeled normal truth. The Flutter source mirrors these boundaries and asserts them in its unit-test source.

## Residual risks

Low residuals: the requested spawn-model identity cannot be independently confirmed from the session, and Flutter execution was intentionally omitted. Informational residuals: only 182 of 200 assigned injection units are constructable, and field truth remains unavailable. These limitations are honestly represented and do not create a Critical finding.

## Reviewed primary sources

[OpenAI Harness Engineering](https://openai.com/index/harness-engineering/), [NIST Measurement Process Characterization](https://itl.nist.gov/div898/handbook/mpc/mpc.htm), [TimeSeriesBench](https://arxiv.org/abs/2402.10802), [Wu and Keogh](https://arxiv.org/abs/2009.13807), [Kaufman et al. leakage audit](https://cris.tau.ac.il/en/publications/leakage-in-data-mining-formulation-detection-and-avoidance-2/), and [Pineau et al. reproducibility](https://www.jmlr.org/papers/v22/20-303.html) were reviewed for invariant, uncertainty, leakage, temporal-benchmark, and reproducibility criteria.

