# LightGuard v0.13 External Labeled AMI Benchmark Transfer

## 1. Freeze
- v0.12R reproducibility witness: 6fbba284f4a3aec83e869e9c22b7be3156530a814f092c4c2a6a0c69ca5f9ab1
- v0.13 configuration/threshold seals remain PRE_CONFIRMATORY and hash-bound to the raw MAD archive.

## 2. Dataset table
| Dataset | Grade | Status | Use |
|---|---|---|---|
| MAD | DG-A | NOT_EVALUABLE_INCOMPLETE_COVERAGE | Primary external electrical anomaly mechanism benchmark |
| REFIT | DG-B | BLOCKED_EXTERNAL_DATA | Secondary blocked |
| UCR | DG-C | WITHHELD_LICENSE_UNKNOWN | Licence withheld |
| Zenodo pseudo-labelled | DG-D | EXCLUDED | Not Gold/calibration/confirmatory |

## 3. MAD split and overlap
- Author train/test shapes: train=[2319, 14, 48]; test=[5414, 14, 48].
- Frozen fit/calibration counts: fit=1891; calibration=428.
- Meter overlap assessment: NOT_ASSESSABLE; MAD retains no meter IDs or timestamps.

## 4. Signal Core
- LG-S1: record-relative surrogate deviation only; it is not meter-relative without identity/history.
- LG-S2: persistence/temporal accumulation external mechanism sign.
- LG-S3: UNAVAILABLE_NORMALIZATION_PROVENANCE.
- LG-S4: abrupt/structural-change external mechanism sign.
- LG-S5: transparent external multivariate mechanism sign using available components.

## 5. Confirmatory table including coverage
| Candidate | Status | Balanced accuracy | Coverage |
|---|---|---:|---|
| SC3 | EVALUATED_PARTIAL | 0.5200448502146089 | 5400/5414 (0.9974141115626154) |
| z-score comparator | EVALUATED | 0.665982584137444 | 5414/5414 (1.0) |
| SC3 primary gate | NOT_EVALUABLE_INCOMPLETE_COVERAGE | 0.5200448502146089 | 5400/5414 (0.9974141115626154) |

## 6. Classwise
- Classwise output is in `v13_mad_classwise_results.csv`; labels 1--6 remain opaque repository classes with no inferred fault mechanism.

## 7. Secondary
- REFIT is blocked and publishes no metric.
- UCR is withheld for UNKNOWN licence and publishes no metric.
- Pseudo-labelled Zenodo data is excluded.

## 8. External validity
- Empirical grade: **NO_EV_GRADE_NOT_EVALUABLE**.
- This applies only to the named external mechanism benchmark and does not transfer to streetlight field performance.

## 9. Canonical six
- Six frozen v0.11 cases are joined in `v13_case_evidence_matrix.csv` without probability or performance columns.

## 10. Claims allowed and prohibited
- Allowed: external electrical anomaly mechanism evidence within the frozen MAD author split.
- Prohibited: Suyeong-gu streetlight accuracy, recall, specificity, asset condition, confirmed fault, and fault probability.

## 11. Human review
- Status: PENDING. No human-derived performance or agreement result is available.

## 12. QA / Build
- Independent QA: PASS WITH WARN.
- v0.13 preflight: PASS.
- Flutter analyze: No issues.
- Flutter tests: 26 passed.
- Flutter web release build: PASS.
- Flutter Android release build: PASS; APK 52.3 MB.
- Field confirmation: NOT_AVAILABLE.
- Independent human agreement: NOT_AVAILABLE.
- Track B meter/temporal transport: NOT_ASSESSABLE.

## 13. Next steps
- Obtain actual human review and field outcome joins under a new sealed protocol.
- Do not retune this confirmatory result; new hypotheses require a new protocol identifier.

## Release status
- Primary MAD gate: **NOT_EVALUABLE_INCOMPLETE_COVERAGE**
- External empirical grade: **NO_EV_GRADE_NOT_EVALUABLE**
- REFIT: **BLOCKED_EXTERNAL_DATA**
- UCR: **WITHHELD_LICENSE_UNKNOWN**
- Human review: **PENDING**
- Streetlight field accuracy: **NOT AVAILABLE**
- Actual fault probability: **NOT AVAILABLE**

## Result boundary
External labeled electrical anomaly mechanism evidence only; never streetlight field accuracy or actual fault probability.

The MAD labels are binary-grouped only for the sealed external benchmark; labels 1--6 remain opaque repository classes. A primary pass is not a municipal field-performance claim. A primary fail is reported without retuning or replacement.

## Controls retained
- Pre-confirmatory feature/config and threshold seals are bound to raw MAD hashes.
- REFIT remains secondary blocked.
- UCR remains licence-withheld.
- Pseudo-labelled Zenodo data is excluded from Gold, calibration, and confirmatory analysis.
- LG-S3 is unavailable because normalized MAD tensors lack required physical provenance.
- Track B is not assessable because meter identity and timestamps are unavailable.
