# LightGuard v0.13 Domain Transfer Matrix

Date: 2026-08-21

## Scope and gate decision

This matrix reviews three external electrical/time-series sources and the transfer of their measurement and anomaly logic to LightGuard. It is an evidence boundary, not a performance report.

**Gate result:** mechanism-level external validation is permitted with explicit feature alignment and frozen source splits. Streetlight field accuracy, municipal recall/FPR/specificity, confirmed fault status, and fault probability remain unavailable and prohibited.

Rating scale:

- **Strong**: direct match to the required quantity and mechanism.
- **Moderate**: useful analogue, but one or more important conditions differ.
- **Weak**: generic shape or workflow relevance only.
- **None**: the source does not contain the required evidence.

## Dataset transfer matrix

| Dataset / original method | Measurement | Phase | Sampling | Operational context | Anomaly mechanism | Streetlight similarity | Transfer rating | Allowed use | Prohibited inference | Unresolved risk |
|---|---|---|---|---|---|---|---|---|---|---|
| MAD: Metering Anomaly Diagnosis; labelled multivariate classification of deployed AMI samples | Moderate: three-phase voltage/current, active power, and power factor; released variables are normalized | Moderate for phase-labelled channels; Weak for sequence analysis because phasor, angle, and phase-order provenance are not established | Moderate: 30-minute interval and 48-point daily windows; no transient evidence | Weak: substation smart meters, but public source does not establish streetlight topology or controller state | Moderate: 122 manually inspected/professionally labelled abnormal meters and six categories, but public mechanism dictionary is incomplete | Weak to Moderate for polyphase AMI screening; Weak for lamp/cabinet fault truth | Conditional mechanism analogue | Test whether a frozen feature reacts to a related multivariate meter pattern; retain external labels and units | Transfer MAD thresholds, class IDs, probabilities, or metrics as Suyeong results | Normalization and missing instrument/label details can conceal non-transferable effects |
| REFIT original; aggregate and appliance active-power measurement from 20 UK homes | Strong for active power in watts; None for per-phase voltage/current | None | Strong for appliance transitions at 8 seconds; Weak for 15/30-minute cabinet inference without a separately frozen resampling protocol | Weak: domestic household operation in Loughborough | None for the base dataset; the annotated companion provides real appliance-behaviour anomalies | Weak | Method analogue only | Compare aggregate versus submetered observability; test persistence/normal-operation modelling as a measurement lesson | Treat appliance labels as feeder/lamp fault labels or claim lamp-level localization | Household load mix, sensor placement, and annotation rules differ from municipal lighting |
| REFIT annotated companion and Rashid et al. AEM method; learn normal appliance operation and detect real anomalous appliance behaviour | Strong for appliance/aggregate active power; None for phase quantities | None | Strong for the source cadence; not a cabinet profile by itself | Weak: five selected UK homes and eight appliance groups | Moderate to Strong for real appliance anomaly behaviour; Weak for electrical fault mechanism | Weak | Conditional method analogue | Use the aggregate-versus-submetering limitation and normal-model logic as a design warning | Promote its labels to Gold/Silver streetlight outcomes or compare its F1 directly with municipal performance | The source paper reports degraded anomaly detection with aggregate/NILM data, which is precisely the source-to-cabinet observability risk |
| UCR Time Series Anomaly Archive `Italianpowerdemand` entries 210, 211, 212; official `UCR_TimeSeriesAnomalyDatasets2021.zip` | Weak for LightGuard electrical measurement; generic univariate benchmark rows with 119819, 119580, and 29931 rows | None | Moderate only for generic temporal robustness, train-end handling, and interval localization; None for electrical sampling or transients | None for municipal streetlight operations | Weak as DG-C generic labelled anomaly intervals, with synthetic/composed archive caveats; None for electrical mechanisms | None for physical/operational similarity; Weak only for temporal plumbing | Generic temporal robustness only | Test interval-aware scoring, train/anomaly boundary handling, and reproducibility against the frozen archive SHA-256 `ac4b991c701e620ae9cc5ebd57ae45593a36cc9c0b6ed5e3c4b7e466cf4783d4` | Call it seasonal classification, electrical anomaly truth, or streetlight evidence; transfer its metrics or thresholds to LightGuard | Explicit license is unknown; archive construction and anomaly semantics are not municipal/electrical field outcomes |

## Method transfer matrix

| External method or concept | What it actually establishes | LightGuard correspondence | Rating | Adopted boundary |
|---|---|---|---|---|
| MAD supervised classification | A model can separate the source's labelled smart-meter sample classes under its source representation and split | A related multivariate meter pattern can be used in an external mechanism check | Moderate | No cross-domain threshold, calibration, probability, or field metric transfer |
| REFIT normal-operation modelling / AEM | Normal appliance operation can be learned and deviations detected; aggregate measurements lose source specificity relative to submetered data | Supports meter-local baseline and the warning that aggregate cabinet data cannot localize a lamp | Moderate | Candidate or anomaly sign only; source labels remain appliance-level |
| UCR anomaly archive temporal benchmark | Source files provide train-end and labelled anomaly-interval encodings for generic time-series evaluation | Supports interval-aware scoring and temporal robustness checks | Moderate for temporal evaluation only | No electrical-mechanism or streetlight interpretation; no cross-domain metric transfer |
| NIST CUSUM | Persistent shifts are evaluated relative to an in-control mean and scale | Supports persistent meter-relative departure rather than a universal threshold | Moderate | Baseline must be source- and meter-local, time-aligned, and frozen before evaluation |
| IEC 61000-4-30 power-quality measurement | In-situ parameters such as current magnitude and current unbalance require defined measurement and interpretation methods; transducer effects matter | Supports explicit measurement semantic, class, window, and provenance fields | Strong for measurement governance | Do not label an unstandardized RMS spread as a standard unbalance or sequence quantity |
| IEEE 1459 power definitions | Balanced/unbalanced power quantities and phase-sequence components require defined formulas, notation, observation periods, and filtering | Supports separating magnitude features from phase-sequence calculations | Strong for terminology | Sequence terms require the necessary phasor inputs and validated computation |
| Wu and Keogh benchmark critique | Public benchmark metrics can be misleading because of triviality, density, label, and temporal biases | Supports frozen splits, simple baselines, prevalence reporting, and no metric transport | Strong for evaluation governance | External metric is conditional on its dataset and cannot become municipal accuracy |

## RMS phase-current audit

The present LightGuard phase feature is a scalar spread or share pattern across per-phase RMS/current interval values. That is a legitimate descriptive feature if named conservatively. It is not a negative-sequence current measurement.

For phase phasors `Ia`, `Ib`, and `Ic`, a Fortescue transform uses complex quantities and a phase-order operator `a = exp(j*2*pi/3)`:

```text
I0 = (Ia + Ib + Ic) / 3
I1 = (Ia + a*Ib + a^2*Ic) / 3
I2 = (Ia + a^2*Ib + a*Ic) / 3
```

RMS magnitudes provide `abs(Ia)`, `abs(Ib)`, and `abs(Ic)`, but not their relative angles. The missing angles can change `I2` while preserving all three RMS magnitudes. RMS-only spread also cannot distinguish supply unbalance, load composition, CT/transducer error, phase mapping error, harmonics, or a physical fault. Consequently:

- Allowed label: `phase-current magnitude asymmetry observation`.
- Allowed label: `phase-selective anomaly sign`.
- Prohibited label: `negative-sequence current`.
- Prohibited label: `negative-sequence fault`.
- Prohibited label: `phase-loss diagnosis` unless the meter/controller semantics and field outcome support it.

The negative-sequence label becomes eligible only after all of the following are available and documented: synchronized phase voltage/current phasors or waveforms; phase order; instrument and transducer provenance; a defined observation window; a validated sequence calculation; and a disturbance/control analysis. Eligibility still means diagnostic feature, not confirmed fault.

## Cross-domain metric audit

The benchmark unit is different in each source:

- MAD: labelled smart-meter samples and source-specific abnormal categories.
- REFIT: appliance or household power observations and appliance anomaly labels.
- UCR anomaly archive: univariate sequences with source-encoded train ends and labelled anomaly intervals.
- LightGuard: a municipal cabinet candidate joined to an asset, expected state, AMI interval, anomaly signs, and eventually a field outcome.

These are not exchangeable decision units. A metric is conditional on the population, prevalence, label process, sampling, aggregation, split, and decision unit. Therefore the following rule is frozen:

```text
external metric = within-source mechanism/implementation evidence
external metric != Suyeong streetlight accuracy
external metric != municipal fault probability
external metric != confirmed cabinet fault
```

No external result may be used to calibrate LightGuard probability, select a municipal queue threshold, or claim recall/FPR on the 204 Suyeong cabinets. If an external result is shown in a report or UI, it must carry the dataset name, source split, label definition, prevalence, sampling semantics, and the phrase `external mechanism validation only`.

## Evidence and risk ledger

| Item | Evidence | Risk | Status |
|---|---|---|---|
| MAD is actual deployed AMI | Source README states 504 three-phase four-wire meters and manual/professional labels | Actual AMI does not equal same topology, load, schedule, or field outcome as streetlights | Use as AMI mechanism analogue only |
| MAD phase channels exist | Source README lists phase voltage/current/power/power factor | Channel existence does not establish synchronized phasors or sequence validity | RMS magnitude feature only |
| REFIT annotations are real | University source calls them real, non-simulated appliance anomalies | Real appliance anomaly is not a feeder or lamp fault | Keep appliance label namespace separate |
| Aggregate monitoring loses specificity | Rashid et al. compare aggregate/NILM with submetered detection and report worse performance with NILM | Cabinet aggregate can mix lamps, circuits, schedules, and unrelated effects | Require controller/lamp mapping for field claims |
| UCR archive contains labelled anomaly intervals | Official archive entries 210-212 encode train end and anomaly intervals; archive SHA-256 is frozen | DG-C synthetic/composed caveats and unknown explicit license limit interpretation | Use only for generic temporal robustness and interval handling |
| Phase sequence requires richer measurement | IEEE 1459, IEC 61000-4-30, and primary negative-sequence work define measurement/sequence context | Incorrect terminology can imply a fault mechanism not observed | Enforce terminology gate |
| Benchmarks may be biased | Wu and Keogh identify triviality, label, density, and run-to-failure problems | Cross-domain metrics can overstate usefulness | Freeze splits and report simple baselines |

## v0.13 adopted rules

1. The release claim is limited to external electrical anomaly mechanism validity and feature sanity checks.
2. No external dataset is a substitute for municipal streetlight field truth.
3. No external label is imported as a LightGuard Gold, Silver, or proxy label.
4. MAD values remain normalized source values; no physical unit or threshold is inferred.
5. REFIT labels remain appliance-level anomalous-behaviour labels.
6. UCR archive entries 210-212 remain generic labelled anomaly-interval benchmarks for temporal robustness only; they do not support electrical-mechanism or streetlight claims.
7. RMS phase asymmetry is never renamed negative sequence.
8. A sequence claim requires phasor-capable measurement and a validated Fortescue calculation.
9. External accuracy, recall, precision, FPR, AUROC, F1, and ranking values are source-conditional and cannot become municipal metrics.
10. External and LightGuard data remain separate namespaces with explicit provenance.
11. A cabinet fault claim requires time-aligned cabinet-meter-controller-lamp mapping and a maintenance/inspection outcome.
12. Missing measurement semantics, topology, or outcome labels produce abstention, not imputation.

## Required evidence to exit the gate

The gate can be revisited only with a frozen external experiment specification and a dataset containing a documented mechanism, compatible measured quantity, compatible sampling semantics, and an independent outcome. For municipal field claims, the minimum join is:

```text
cabinet -> meter -> phase/channel -> controller state -> lamp/asset -> field inspection outcome
```

The join must include timestamps, measurement quality flags, rated-load provenance, phase order, and the outcome definition. Without it, the result remains a mechanism-level external validation and nothing more.
