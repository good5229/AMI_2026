# LUNA Independent v0.13 QA Learning Record

## Role

Independent red-team auditor and methodology reviewer for the v0.13 external
labeled AMI benchmark transfer. The task is to inspect the frozen contracts,
result artifacts, execution code, and Flutter presentation only. This record
does not rerun the experiment, read new external data, retune a feature,
change a threshold, or create human labels.

## Actual Model

The actual implementation is a small, transparent, label-free Signal Core
transferred to the author-provided MAD train/test arrays. The pre-test contract
freezes per-record robust residual features, temporal persistence, CUSUM-style
change evidence, and an equal-weight percentile-rank combination. The allowed
candidate set is SC1, SC2, and SC3; the ordinary z-score comparator is a
comparator, not a replacement candidate. Calibration uses the frozen train
partition only, and the primary gate requires eligible SC3 coverage of the
immutable MAD test partition, balanced accuracy at least 0.70, and at least
0.05 improvement over the comparator.

The observed implementation state is:

- SC3 coverage is 5400/5414, so the primary gate is
  `NOT_EVALUABLE_INCOMPLETE_COVERAGE`.
- SC3 balanced accuracy is 0.5200; the z-score comparator is 0.6660.
- The first confirmatory attempt stopped after loading `y_test` because an
  all-finite-score guard failed before metrics were computed.
- The second attempt is explicitly implementation-only recovery. It leaves
  formulas, scores, thresholds, configuration, and seals unchanged.
- LG-S3 is unavailable because normalized MAD tensors do not establish the
  physical scale and phase provenance required for phase-current analysis.
- Track B is not assessable because meter identifiers, timestamps, and
  meter-to-sample linkage are absent.
- MAD classes 1 through 6 remain opaque repository labels; no mechanism is
  inferred from their numbers or names.

The secondary gates are correctly conservative: REFIT is blocked, UCR is
withheld for unknown licensing, and Zenodo pseudo-labels are excluded from
Gold, calibration, and confirmatory evidence.

## Sources Reviewed

The following already-reviewed authoritative sources are used only to test
whether the transfer logic and claim boundary are methodologically defensible:

- MAD repository, [IISGLab/MeteringAnomalyDiagnosis](https://github.com/IISGLab/MeteringAnomalyDiagnosis), including its frozen release metadata and license.
- MAD associated primary paper, [doi:10.3390/en17050993](https://doi.org/10.3390/en17050993).
- [Wu and Keogh, doi:10.1109/TKDE.2021.3112126](https://doi.org/10.1109/TKDE.2021.3112126), for the danger of treating benchmark anomaly results as universal detector validity.
- REFIT official dataset record, [doi:10.15129/9729a2a0-11ce-4cce-b0d0-144c483fcb33](https://doi.org/10.15129/9729a2a0-11ce-4cce-b0d0-144c483fcb33), for the domain and annotation boundary of appliance-load anomalies.
- [STARD 2015, doi:10.1136/bmj.h5527](https://doi.org/10.1136/bmj.h5527), for transparent reporting of index-test, reference-standard, and incomplete-result limitations.
- [NIST Engineering Statistics Handbook CUSUM](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm), as an official primary-method reference for interpreting cumulative deviation as change evidence rather than causal fault proof.

## Dataset/Method Relevance

MAD is the only currently admissible primary dataset, and only for a narrow
sample-level binary external electrical-anomaly mechanism check on its frozen
author split. Its relationship to the associated paper is not assumed to be
release-equivalent: the repository arrays and the paper report different
sampling/sample details. The repository's opaque classes and unavailable
meter-level linkage prevent class-mechanism claims and meter-disjoint transport
claims.

REFIT can support a separately frozen household-load anomaly mechanism study
if the official annotation files and split are acquired and verified. It
cannot validate streetlight or distribution-cabinet faults. UCR
ItalianPowerDemand is not an electrical-fault Gold set, and its license remains
withheld in this release. Pseudo-label data cannot serve as independent truth.

The frozen robust residual, persistence, and change-point signals are
reasonable descriptive anomaly signs. The phase-current signal is correctly
abstained when physical phase provenance is unavailable; RMS magnitudes alone
cannot be relabeled as negative sequence or symmetrical components. The
resulting external metric, even if fully evaluable, would describe only the
named MAD benchmark and not Suyeong-gu streetlight field accuracy, field
recall, asset condition, confirmed fault, or fault probability.

## Risks

1. The primary result is incomplete by contract, not a failed full-coverage
   confirmatory evaluation. Reporting the 0.5200 score without its 5400/5414
   eligibility would overstate evidence.
2. The first all-finite guard failure and the second implementation-only
   recovery must remain visible in provenance; silently presenting attempt 2 as
   an untouched first run would violate transparent incomplete-result
   reporting.
3. A successful external benchmark result could still be misread as municipal
   performance. The claim boundary must remain attached to every report and UI
   summary.
4. Human review, field confirmation, meter-disjoint transport, and mechanism
   labels remain unavailable. No κ, diagnostic accuracy, or field outcome
   estimate is admissible yet.
5. SC3's descriptive balanced accuracy of 0.520 is below the z-score
   comparator's 0.666. Because SC3 coverage is incomplete, this remains a
   descriptive partial-coverage comparison and supplies no external-validity
   grade.

## Adopted Rules

- Treat pre-test seals, thresholds, candidate set, feature mapping, split,
  label grouping, and success criteria as immutable after test-label access.
- Preserve `NOT_EVALUABLE_INCOMPLETE_COVERAGE` as the primary status; do not
  substitute SC1, the comparator, or a complete-case redefinition for SC3.
- Describe SC3's 5400/5414 result as partial coverage only. Do not turn it into
  a full-test balanced-accuracy claim.
- Keep LG-S3 unavailable and call any residual three-phase magnitude pattern a
  phase-current asymmetry observation only when its gate passes; never call it
  negative sequence from RMS data.
- Keep REFIT blocked, UCR license-withheld, pseudo-labels excluded, Track B
  not assessable, and MAD classes opaque.
- Accept the supplied authoritative verification record: the duplicate v13
  import and card were removed, the unit test was updated to the final result
  contract, and `./scripts/v13_preflight.sh` completed with exit 0. The run
  deterministically regenerated raw/configuration/threshold/result artifacts,
  passed the artifact contract before Flutter and at the final gate, reported
  no analyzer issues, passed 26 Flutter tests, and completed web and Android
  release builds; the APK size was 52.3 MB.
- The final QA verdict is `PASS WITH WARN`. The warnings are scientific and
  evidentiary limits, not unresolved release blockers. A negative result and
  incomplete coverage are truthful outcomes and must not be reframed as
  software release failures.
