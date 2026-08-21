# LightGuard v0.13 Independent Audit

## Verdict

**PASS WITH WARN**

The previously identified release blockers are resolved. The duplicate v13
import and duplicate v13 card were removed, the unit test now asserts the final
result contract, and the authoritative full preflight record completed with
exit 0. Remaining warnings are scientific limitations and truthful negative or
incomplete outcomes, not software release failures and not permission to
modify the frozen result.

## Scope and inspected artifacts

The audit inspected the v0.13 dataset registry, pre-confirmatory feature and
threshold seals, raw external manifest, feature-transfer protocol, MAD train
and confirmatory result CSVs, REFIT/UCR result gates, cross-dataset summary,
final summary, reproducibility references, `run_v13_mad_confirmatory.py`, the
v13 Flutter card and screen, and the v13 unit test. This final update relies on
the supplied authoritative verification evidence; this auditor did not run a
command, test, build, benchmark, Git operation, external download, or additional
research.

The inspected contracts consistently preserve the intended boundary:
external labeled electrical anomaly mechanism evidence only, never Suyeong-gu
streetlight field accuracy, field recall, asset condition, confirmed fault, or
fault probability.

## Scientific and methodological audit

The pre-test seals exist and bind the feature/configuration and thresholds to
the frozen MAD source hash. The feature-transfer protocol prohibits post-test
feature, normalization, threshold, candidate, label-grouping, metric, or
success-criterion changes. The confirmatory implementation records the first
all-finite guard failure and labels the second run as implementation-only
recovery; this is appropriate provenance rather than a hidden rerun.

The observed MAD outcome is SC3 coverage 5400/5414, balanced accuracy 0.5200,
and comparator balanced accuracy 0.6660. Because SC3 is not eligible for the
complete immutable test partition, the sealed primary result is
`NOT_EVALUABLE_INCOMPLETE_COVERAGE`. The comparator must not replace SC3, and
SC1 must not be promoted to rescue the primary gate. REFIT is blocked, UCR is
withheld because its license is unknown, pseudo-labels are excluded, Track B is
not assessable, and LG-S3 is unavailable due to missing normalization/physical
phase provenance.

This interpretation is consistent with the reviewed MAD repository and its
associated paper ([MAD repository](https://github.com/IISGLab/MeteringAnomalyDiagnosis), [doi:10.3390/en17050993](https://doi.org/10.3390/en17050993)), but the repository release is not silently treated as identical to every dataset description in the paper. The REFIT record ([doi:10.15129/9729a2a0-11ce-4cce-b0d0-144c483fcb33](https://doi.org/10.15129/9729a2a0-11ce-4cce-b0d0-144c483fcb33)) supports only a separately verified household-load anomaly study. Wu and Keogh ([doi:10.1109/TKDE.2021.3112126](https://doi.org/10.1109/TKDE.2021.3112126)) supports caution against treating benchmark behavior as universal validity. STARD 2015 ([doi:10.1136/bmj.h5527](https://doi.org/10.1136/bmj.h5527)) supports reporting incomplete index-test results and reference-standard limitations explicitly. NIST's official CUSUM guidance ([NIST CUSUM](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm)) supports interpreting cumulative deviation as change evidence, not as proof of a causal equipment fault.

## Authoritative release verification

The supplied `./scripts/v13_preflight.sh` run completed with exit 0 and records:

- deterministic raw/configuration/threshold/result regeneration;
- artifact contract PASS before Flutter and PASS again at the final gate;
- `flutter analyze`: no issues;
- `flutter test`: 26 passed;
- Flutter web release build: PASS;
- Flutter Android release build: PASS, APK 52.3 MB.

The duplicate import, duplicate card, and stale `PRE_CONFIRMATORY` unit-test
expectation are therefore closed blockers. No release-readiness blocker remains
within the audited scope.

## Warnings retained

- The primary result remains `NOT_EVALUABLE_INCOMPLETE_COVERAGE`; SC3 covers
  5400 of 5414 test records.
- SC3's descriptive balanced accuracy is 0.520, below the z-score comparator's
  0.666. This partial-coverage comparison does not receive an external-validity
  grade.
- Track B and meter leakage are not assessable because meter identity,
  timestamps, and meter-to-sample linkage are unavailable.
- LG-S3 remains unavailable because normalized data do not provide the
  physical phase provenance required by the frozen gate.
- REFIT remains blocked, UCR remains withheld for unknown licensing, and
  pseudo-labels remain excluded.
- MAD labels 1--6 remain opaque; no physical fault mechanism may be inferred.
- Human review and field confirmation remain pending.
- No result estimates Suyeong-gu streetlight field accuracy, field recall,
  asset condition, confirmed fault, or fault probability.

The negative descriptive comparison and incomplete coverage are valid,
transparent experimental outcomes. They do not constitute software release
failures, and they must not be hidden, retuned, imputed, or converted into a
positive external-validity claim.

## Required disposition

Release disposition is `PASS WITH WARN`. Preserve the primary status, the
5400/5414 partial coverage, the 0.520 SC3 score, the 0.666 comparator score, all
secondary gates, and the external-only claim boundary. The warnings can be
retired only by new, prospectively sealed evidence that directly resolves each
limitation; they cannot be removed through post-test tuning or reinterpretation.
