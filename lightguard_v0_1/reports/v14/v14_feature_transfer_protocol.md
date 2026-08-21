# LightGuard v0.14 Physical Feature Transfer Protocol

**Owner:** TERRA B Physical Feature Transfer Methodologist  
**Status:** PRE_OUTCOME_FROZEN_PROVISIONAL_PROVENANCE  
**Date:** 2026-08-21  
**Protocol ID:** `LG-V14-PMC-1`

## Purpose and immovable boundary

This protocol asks whether pre-specified, physically interpretable electrical signals reproduce in external data whose provenance is retained. It preserves the v0.13 MAD result as negative/non-evaluable predecessor evidence: SC3 coverage `5400/5414`, SC3 balanced accuracy `0.52004485`, z-score `0.66598258`, `NOT_EVALUABLE_INCOMPLETE_COVERAGE`, `NO_EV_GRADE_NOT_EVALUABLE`, LG-S1 record-relative surrogate only, LG-S3 unavailable, and meter/temporal Track B not assessable.

No v0.14 result may erase, tune on, or replace that evidence. External electrical mechanism evidence is not streetlight field accuracy, Suyeong fault recall, field specificity, asset condition, production readiness, or actual fault probability.

## Activation and fail-closed provenance gates

Before any raw data access or outcome computation, TERRA A must set each dataset field in its registry to PASS, PARTIAL, FAIL, or UNKNOWN. A track activates only if its required gates PASS:

| Track | Required gates | Failure state |
| --- | --- | --- |
| A: London distribution | permitted licence; documented disturbance-label construction/classes; retained ordering or source-defined time blocks; physical-unit interpretation; immutable Train/Test relationship | `PRIMARY_BLOCKED_PROVENANCE` |
| B: CoDEx-VFD | CC BY 4.0 reconfirmed at download; manifest/README identifies run, current channels, time basis, injection intervals, and exposure metadata | `BLOCKED_PROVENANCE_OR_MANIFEST` |
| C: SustDataED2 | OSF and IEEE licence/version agreement; documented timestamps, waveform/power channel mapping, transition labels, and appliance/day keys | `BLOCKED_PROVENANCE_OR_MANIFEST` |

Suitability is decided before scores or confirmatory labels are inspected. A blocked track is reported as blocked; it is never replaced because another dataset looks more favourable.

## Physical Mechanism Core v2

| ID | Pre-registered score family | Direct-evidence requirement | Ceiling |
| --- | --- | --- | --- |
| PMC-1 | Historical/contextual baseline deviation: robust residual from an entity-linked, earlier reference | Stable entity, ordered history, compatible physical scale | Without those, `SURROGATE_ONLY`; do not call it meter-relative. |
| PMC-2 | Persistence: run length and cumulative duration above the pre-specified robust-residual threshold | Ordered, contiguous samples and a valid sampling basis | Persistence sign only, not cause. |
| PMC-3 | Phase/channel asymmetry: robust contrast among documented, aligned current channels on a common physical scale | Named channels, shared timing, comparable units; A/B/C required for a three-phase statement | Channel contrast only. No symmetrical-component or fault-type claim. |
| PMC-4 | Abrupt/structural change: two-sided CUSUM and predeclared change window | Ordered reference process and calibration-derived scale | Change observation only, not root cause. |
| PMC-5 | Multivariate consistency: rank aggregation across at least two available, non-duplicated PMC scores | At least two components whose source fields are not algebraic duplicates | Transparent evidence combination only. |

Robust location is the calibration median. Robust scale is `max(1.4826 * MAD, epsilon)`, where `epsilon` is the fit-partition fifth percentile of strictly positive scales for that source channel. A channel with no positive scale is unavailable. Residuals are clipped to `[-8, 8]`; no missing value is imputed. CUSUM uses the standardized residual with frozen `k=0.5` and `h=5.0`; its threshold is selected only from the declared calibration grid.

## Candidate and comparator contract

All track scores are computed from source-native fields only. Solar, municipal schedules, streetlight/asset fields, rated load, fixture count, cabinet identity, H1, Proxy, synthetic features, class-derived fields, and confirmatory labels are prohibited.

| Candidate | Contents | Eligibility |
| --- | --- | --- |
| `PMC-C1` | PMC-1 only | PMC-1 direct or explicitly surrogate, with status retained |
| `PMC-C2` | Equal-weight percentile ranks of PMC-2 and PMC-4 | Both components available |
| `PMC-C3` | Equal-weight percentile ranks of all available PMC-1..PMC-5 | At least two non-duplicate components; a PMC-3-specific conclusion additionally requires direct PMC-3 |
| Comparator | Maximum absolute ordinary z-score across the same eligible source-native channels | Mean/SD fit only; the same partition, time window, and unit are used |

Candidate selection and threshold selection occur on calibration data only. The frozen threshold grid is the calibration score quantiles `0.80, 0.85, 0.90, 0.95, 0.975, 0.99`. Ties select the higher threshold; candidate ties select `PMC-C3`, `PMC-C2`, then `PMC-C1`. No deep model, learned representation, post-test feature change, source-specific score addition, or post-outcome reweighting is allowed.

## Track separation, independent units, uncertainty, and controls

Each track config fixes a deterministic seed and label-blind split. Fit may estimate robust reference parameters; calibration may select only the frozen candidate/threshold grid; confirmatory data are touched once for locked reporting. Split membership must be derived from immutable source identifiers. If no immutable identifier or eligible independent-unit key exists, the relevant track is not evaluable.

Confidence intervals use `2,000` stratified cluster bootstrap draws, seeded per track, with clusters sampled at the independent unit. Row-level naive bootstrap is prohibited. Fewer than 20 eligible independent clusters returns `INSUFFICIENT_CLUSTER_COUNT` rather than a precision claim.

Matched controls must be score-independent, carry no labelled event/injection in the declared exclusion window, and match the declared contextual keys. Controls are fixed before score calculation. CoDEx uses run/episode controls; SustData uses matched no-transition windows. London does not create pseudo-controls if source time-block provenance is absent.

## Metrics and pre-registered gates

| Track | Primary unit and primary question | Confirmatory metrics | Gate |
| --- | --- | --- | --- |
| A | Source-defined independent distribution sample/time block; do pre-specified signals discriminate documented disturbance labels? | Balanced accuracy, macro recall, macro F1, AP only for valid binary/one-vs-rest label semantics; cluster CI | `NOT_EVALUABLE` unless provenance gates and independent-unit definition pass. No numerical success threshold is set before verified label semantics. |
| B | Measurement run and labelled disturbance episode; do PMC-2/4/5 increase in injection intervals relative to matched control? | Episode recall at IoU >= 0.10, onset time-to-detection, benign/control escalation, severity response, run-cluster CI | At least 20 confirmatory runs and >= 80% eligible episode/control pairing. Row accuracy is descriptive only. |
| C | Known transition, with day/appliance clustering; do scores rise around documented transitions versus matched no-transition windows? | Median paired score uplift, transition coverage, onset time-to-detection, matched contrast, cluster CI | At least 20 confirmatory transition clusters and >= 80% valid matched controls. This is a positive-control gate, never a fault gate. |

Support means only that a pre-registered named mechanism passes its own track gate with its cluster-respecting uncertainty. `MR-A` requires support in two or more physically relevant external datasets, `MR-B` one physically relevant labelled dataset, `MR-C` positive-control-only support, and `MR-X` no replication or not evaluable. These grades are separate from literature grades and are not fault probabilities.

## Dataset-specific availability

The mapping and three track configs are frozen now, but every dataset-specific field is provisional pending the independent TERRA A provenance gate. `AVAILABLE`, `PARTIAL`, `N/A`, and `SURROGATE_ONLY` describe possible mechanism availability, not a performance forecast. Missing phase identity, physical unit scale, timestamp continuity, or entity linkage remains missing.

## Reporting rules

Report blocked, negative, lower-than-comparator, and non-evaluable findings beside any positive result. Retain domain distance: London is distribution-derived but preprocessed; CoDEx is VFD/EMI at 2.5 MHz; SustData is residential state-change data. No result is converted into a streetlight claim.
