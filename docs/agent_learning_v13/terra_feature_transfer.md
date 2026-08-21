# TERRA B Feature Transfer Methodology

**Role:** TERRA B Feature Transfer Methodologist  
**Actual Model:** GPT-5  
**Date:** 2026-08-21

## Scope and claim boundary

This pre-outcome contract evaluates transparent electrical anomaly signs on externally labeled electrical data. It does not measure a streetlight intervention, production H1 behavior, streetlight field accuracy, Suyeong-gu fault prevalence, or fault probability.

KASI solar fields, astronomical expected state, municipal policy, rated load, cabinet or asset mapping, lamp counts, and synthetic streetlight variables are excluded. A missing source feature is unavailable; it is not inferred from a label, class, test score, or domain prior.

## Sources Reviewed

- [MAD repository](https://github.com/IISGLab/MeteringAnomalyDiagnosis), dataset maintainer primary record: 504 deployed 3P4W AMI meters, 122 manually inspected or professionally labeled anomaly meters, author split, and 14 normalized variables. Adopted rule: use source-native AMI mechanisms only and block physical phase comparison until common-scale provenance is confirmed.
- [REFIT annotated anomalies](https://pureportal.strath.ac.uk/en/datasets/annotated-load-anomalies-from-the-refit-dataset/), university dataset record: real annotated household load anomalies. Adopted rule: secondary persistence/baseline check only; no phase or streetlight claim.
- [UCR archive](https://www.cs.ucr.edu/~eamonn/time_series_data_2018/), archive maintainer record: generic time-series benchmark. Adopted rule: stress test only; no electrical-mechanism or field-outcome claim.
- [Rousseeuw and Croux, 1993](https://doi.org/10.1080/01621459.1993.10476408), primary robust-statistics method: MAD has a 50% breakdown property. Adopted rule: use median/MAD with a calibration-only epsilon floor and expose insufficient variation.
- [Page, 1954](https://doi.org/10.1093/biomet/41.1-2.100), primary sequential-method paper: continuous inspection accumulates departures. Adopted rule: a sustained residual sequence is a shift candidate, not a causal label.
- [NIST CUSUM guidance](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm), official method: CUSUM uses an in-control reference and detects small shifts. Adopted rule: fit reference and decision values on calibration data only; call output a structural-change sign.
- [Zeileis et al., 2002](https://doi.org/10.18637/jss.v007.i02), primary structural-change method: CUSUM, MOSUM, and generalized fluctuation methods require a stable history. Adopted rule: retain a frozen stable-reference requirement and separate structural component.
- [Fortescue, 1918](https://doi.org/10.1109/T-AIEE.1918.4765570), primary electrical method: symmetrical components operate on phasors containing angle and magnitude. Adopted rule: RMS magnitudes alone are not negative/positive/zero sequence; use only `phase-current asymmetry observation`.

## Dataset/Method Relevance

MAD is relevant to external electrical mechanisms but is not a lighting system. Its repository says every variable is normalized. Unless a shared physical scale is documented, normalized phase-current differences are not an interpretable physical imbalance; LG-S3 is unavailable rather than imputed. REFIT supports temporal load behavior but cannot validate phase evidence. UCR does not establish electrical or streetlight mechanism validity.

The frozen mapping is: LG-S1 uses a temporal median/MAD residual with ordered numeric samples and at least 12 valid time points; LG-S2 uses the longest consecutive robust-departure run and needs LG-S1 plus intact ordering; LG-S3 uses A/B/C current magnitude asymmetry only with aligned documented phases and common physical scale; LG-S4 uses two-sided CUSUM from a stable calibration reference; LG-S5 is an equal-weight calibrated combination with an availability mask and at least two actual components. LG-S1 is meter-relative only if meter identity and prior history survive the adapter. Every component is an anomaly sign, not a cause.

## Pre-registered Candidates and Metric

Only three candidates exist. `SC1` is LG-S1. `SC2` is LG-S2 plus LG-S3 and requires both components. `SC3` is transparent LG-S5 using LG-S1 through LG-S4; it requires two available components and LG-S3 for a phase-specific statement. No deep model, learned representation, source-specific feature, class-specific transform, or fourth candidate is permitted.

The pre-registered primary metric is **External MAD Binary Balanced Accuracy** on the author test split: class `0` normal and classes `1` through `6` anomalous. The primary success criterion is eligible SC3 test balanced accuracy at least `0.70` and at least `0.05` absolute balanced-accuracy points above the calibration-selected ordinary z-score comparator. If SC3 is ineligible, report `NOT_EVALUABLE`; do not substitute another candidate after test access. Mapping, preprocessing, normalization, rank transforms, thresholds, and candidate selection are calibration-only. Any result remains external electrical anomaly discrimination, never streetlight field accuracy or fault probability.

## Risks

- MAD normalization may prevent physically valid cross-phase comparison.
- Daily samples may not retain meter identity, weakening strict history-based claims and meter-disjoint audit.
- CUSUM needs a stable reference; regime or preprocessing changes can look structural.
- REFIT and UCR mechanisms differ from feeder, cabinet, and streetlight mechanisms.
- Source labels validate source metering anomalies, not LightGuard asset causes.
- Combined scores can conceal data quality; component scores and missingness must remain visible.

## Adopted Rules

1. Freeze mappings before external test-label access.
2. Use only source-native measurements and ordering; create no solar, policy, rated-load, cabinet, or streetlight fields.
3. Fit all data-derived constants and decisions on calibration data only.
4. Never impute phase values, infer phase order, or compute sequence components from RMS magnitudes.
5. Retain unavailable components as unavailable and expose component-level evidence.
6. Keep the author test split immutable; do not tune after confirmation.
7. Prefix results with the external dataset name.
8. Keep the claim boundary at external electrical anomaly mechanism validity.
