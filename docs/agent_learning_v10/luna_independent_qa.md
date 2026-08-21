# LUNA v0.10 Independent QA Learning

Date: 2026-08-20 (Asia/Seoul)

Requested spawn model: `gpt-5.6-luna`. Independently observable runtime identity: GPT-5/Codex. This is recorded as provenance; it is not evidence of an artifact failure.

## Decision

`PASS with residual risks`.

Severity counts: Critical 0, High 0, Medium 0, Low 2, Informational 2.

The two low residuals are that the requested model identity is not independently observable in this session and Flutter execution was intentionally not rerun under the user’s no-Flutter instruction. The informational residuals are the honest `182/200` constructability rate and the absence of field truth. Neither is a critical finding.

## Method and primary-source lens

The repository harness startup order was followed. The existing append-only v0.10 rerun log record was present before these report writes. The only executable verification was `python3 scripts/test_v10_artifacts.py`, which returned `v0.10 artifact contracts: PASS`. No Flutter, build, full preflight, Git, `.env`, raw-source, or long-running command was used.

The brief source review was applied as follows:

- [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/): evaluate explicit invariants, inspectable artifacts, and feedback loops rather than narrative confidence.
- [NIST Measurement Process Characterization](https://itl.nist.gov/div898/handbook/mpc/mpc.htm): keep reference basis, bias, variability, and uncertainty explicit.
- [TimeSeriesBench](https://arxiv.org/abs/2402.10802): require industrially relevant, reproducible time-series evaluation boundaries.
- [Wu and Keogh](https://arxiv.org/abs/2009.13807): treat benchmark construction, density, labels, and temporal bias as potential sources of illusory progress.
- [Kaufman, Rosset, and Perlich, Leakage in Data Mining](https://cris.tau.ac.il/en/publications/leakage-in-data-mining-formulation-detection-and-avoidance-2/): require explicit leakage detection and prevention.
- [Pineau et al., Improving Reproducibility in Machine Learning Research](https://www.jmlr.org/papers/v22/20-303.html): require precise data, split, command, metric, and implementation records.

## Critical C1-C3 checks

### C1: B-L-12 reconciliation

PASS. `v10_b_l_12_reconciliation.md` records the scope-denominator decision: legacy processed evidence is 8,644 rows with 43 rows having a current gap; the complete v0.10 raw-workbook scope is 8,735 rows with 46 gaps; the difference is 91 rows, not a fabricated correction. It records 34 constructable B-L-12 pairs and 708 changed-cell provenance records. Incomplete source/target intervals remain non-constructable; missing values are neither filled nor converted to zero.

### C2: constructable injection provenance

PASS. The v0.10 artifact contract checked all 182 constructable rows, not just the representative rows inspected here. For each row, `len(cell_provenance) == copied_cell_count`; every serialized cell carries source/target meter and timestamp, phase, source row and cell hashes, semantic `interval_current_ampere`, quality `observed_finite_nonnegative`, operation `identity_current_residual_graft`, scale `1.0`, physical review `PASS_CONSTRAINED_CURRENT_ONLY`, and `energy_unchanged=true`. The manifest has 200 assigned rows: 182 constructable and 18 not constructable. Raw values are not committed and energy reconstruction is disabled.

The `182/200` result is an honest scope limitation, not a reason to relabel rejected rows or weaken the gate.

### C3: shadow causality and leakage audit

PASS. The artifact contract checked 455 meter-day replay rows and 43,582 origin rows. Representative origin records at the beginning and end of the CSV retain causal-proof and state/hash fields; the aggregate contract check found all 43,582 rows causal-proof true and complete state-before/state-after/history-membership hashes. `v10_shadow_causality_audit.json` records `origin_count=43582`, `prefix_invariance=PASS`, `prefix_mismatches=0`, `same_time_permutation=PASS_VACUOUS_NO_DUPLICATES`, and `canonical_loaded_after_seal=true`.

The protocol boundary is coherent: history is strictly before the cutoff, current rows are only inputs to their own decision, no later row or full-corpus statistic enters history, and the six canonical intervals are loaded only after the pre-canonical seal. The canonical artifact is therefore reporting-only and cannot affect origin/state construction.

## Freeze, transport, truth, and claim checks

- v0.9 freeze: PASS. The v0.10 freeze manifest retains H1 and verifies the frozen file hashes. H1 Track-A retuning is prohibited; v0.9 remains controlled generated evidence only.
- H1 unchanged: PASS. The v0.10 transport summary and freeze pointer identify H1; the artifact contract verifies the frozen hashes and the H1 transport row.
- R1 absent: PASS. The optional R1 configuration and results artifacts are absent; transport reports `r1_triggered=false`.
- No fabrication: PASS. Counterfactuals are current-only identity residual grafts. Unmodified AMI is not normal truth; current-only missingness is preserved; no energy reconstruction, rated-load imputation, municipal join, KMA/KASI join, maintenance label, or fault label is introduced.
- Truth boundary: PASS. The final summary, app asset, app documentation, Flutter card, and Flutter unit-test source all state that anonymous AMI has no field fault truth and prohibit field accuracy, actual fault recall, real-background FPR/specificity, municipal performance, and production-readiness claims.
- Flutter source boundary: PASS by inspection. The source reads the v10 summary asset, displays paired recovery/benign escalation/gate metrics, and visibly states the no-field-truth and no-context-join boundary. The unit-test source asserts `transport_gate=PASS`, `r1_triggered=false`, all three truth flags false, and the no-join policy. Flutter execution was not rerun by instruction.

## Residual interpretation

The transport result is semi-synthetic real-background counterfactual validation, not field accuracy. The 182 constructable rows support the stated paired analysis only for the constructable subset. The six canonical shadow actions and the 305 evaluable meter-days describe replay behavior and data availability, not fault outcomes. A prospective field-linked AMI/maintenance-truth study remains required for any field-performance claim.

