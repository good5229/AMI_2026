# LUNA C v0.13 Domain Transfer Review

Date: 2026-08-21

## Role and model provenance

- Role: LUNA C, Electrical Domain Transfer Reviewer.
- Requested task: review MAD, REFIT annotated load anomalies, and the UCR Time Series Anomaly Archive `Italianpowerdemand` entries 210, 211, and 212 from their original sources; review at least three additional authoritative primary or official sources; assess measurement, phase, sampling, operations, anomaly mechanism, and streetlight similarity.
- Actual model: GPT-5, Codex runtime.
- Work boundary: this is a literature and provenance review only. No Git operation, test, build, detector edit, data edit, or external dataset import was performed.
- Claim boundary: external evidence may validate the plausibility of an electrical or temporal anomaly mechanism. It cannot establish municipal streetlight field accuracy, fault probability, or LightGuard field truth.

## Decision

Overall decision: **CONDITIONAL PASS for mechanism-level external validation; FAIL for streetlight field accuracy or fault-probability transfer**.

The reviewed material can support a controlled experiment asking whether a LightGuard feature reacts to a related observable mechanism under a separately defined external benchmark. It cannot support the claim that a score transfers to Suyeong-gu cabinets, that a cabinet is faulty, or that a ranked candidate has a calibrated fault probability.

The most important boundary is measurement semantics. A three-phase RMS magnitude pattern is an observation of phase-current magnitude asymmetry. It is not a negative-sequence current measurement. A negative-sequence quantity requires phase-referenced complex quantities, phase order, an observation window, and a validated sequence calculation. An RMS-only triplet does not contain the relative phase angles needed by the Fortescue transform.

## Sources reviewed

### Assigned primary dataset sources

| Source | Primary evidence reviewed | Method or data relevance | Limitation for LightGuard |
|---|---|---|---|
| [MAD Metering Anomaly Diagnosis repository](https://github.com/IISGLab/MeteringAnomalyDiagnosis) | Repository README and dataset description | 504 deployed three-phase four-wire smart meters; 382 normal and 122 manually inspected or professionally labelled abnormal meters; 14 variables; 30-minute sampling; 48 points per daily sample; six abnormal categories | Values are normalized; unit, instrument uncertainty, feeder topology, phase-angle availability, and detailed class mechanisms are not supplied in the README. It is smart-meter anomaly evidence, not streetlight-cabinet evidence. |
| [REFIT Electrical Load Measurements](https://pureportal.strath.ac.uk/en/datasets/refit-electrical-load-measurements/) and [Murray et al., Scientific Data](https://doi.org/10.1038/sdata.2016.122) | Original dataset record and source-paper description | 20 UK households; aggregate and appliance active power in watts; timestamped at 8-second intervals; roughly two years; real domestic operation | Single-phase household active-power context, no feeder phase quantities, no cabinet topology, no lamp/controller state, and no streetlight maintenance outcome. |
| [Annotated load anomalies from the REFIT Dataset](https://doi.org/10.15129/9729a2a0-11ce-4cce-b0d0-144c483fcb33) and [Rashid et al., ICASSP 2019](https://pureportal.strath.ac.uk/en/publications/evaluation-of-non-intrusive-load-monitoring-algorithms-for-applia/) | Dataset record, annotation scope, and accompanying method abstract | Real, non-simulated appliance anomalies; five selected houses; eight appliance types; the paper learns normal appliance operation and compares aggregate versus submetered/NILM detection | The labels describe anomalous appliance behaviour, not electrical faults in a distribution feeder. The paper explicitly shows that aggregate/NILM performance is worse than submetered performance, which is a direct warning against treating a feeder aggregate as a lamp-level diagnosis. |
| [UCR Time Series Anomaly Archive, official UCR_TimeSeriesAnomalyDatasets2021.zip](https://www.cs.ucr.edu/~eamonn/time_series_data_2018/UCR_TimeSeriesAnomalyDatasets2021.zip) | Entries 210, 211, and 212 in the `Italianpowerdemand` family; official filename encodings identify train end and anomaly intervals: `...36123_74900_74996` (119819 rows), `...38113_39240_39336` (119580 rows), and `...8913_29480_29504` (29931 rows). Archive SHA-256: `ac4b991c701e620ae9cc5ebd57ae45593a36cc9c0b6ed5e3c4b7e466cf4783d4` | A generic labelled time-series anomaly benchmark for temporal robustness and interval handling; source archive caveats classify it as DG-C, with synthetic/composed construction concerns and unknown explicit license | No phase/current/voltage, cabinet/lamp state, electrical mechanism, or municipal outcome. It must not be treated as seasonal classification or electrical anomaly truth. |

### Additional authoritative primary or official sources

| Source | Adopted evidence | Why it matters |
|---|---|---|
| [IEC 61000-4-30:2025](https://webstore.iec.ch/en/publication/71611) | In-situ power-quality measurement and interpretation require defined methods; the scope includes current magnitude, current unbalance, voltage unbalance, harmonics, and the effects of transducers | Supports retaining measurement class, sensor/transducer provenance, observation window, and parameter semantics rather than treating any phase spread as a standardized power-quality quantity. |
| [IEEE 1459-2025](https://standards.ieee.org/ieee/1459/7578/) | Electric-power quantities under balanced/unbalanced and sinusoidal/non-sinusoidal conditions have defined formulas and notation; the standard discusses observation period, filtering, and phase-sequence components | Supports the distinction between a magnitude-only descriptive statistic and a phase-sequence quantity. A label must follow the measurement actually available. |
| [NIST/SEMATECH CUSUM control charts](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm) | CUSUM uses an in-control mean and scale and detects persistent mean shifts relative to that reference | Supports meter-local, time-aligned baselines and persistence rules. It does not justify a universal threshold or a fault interpretation. |
| [Wu and Keogh, Current Time Series Anomaly Detection Benchmarks Are Flawed](https://doi.org/10.1109/TKDE.2021.3112126) | Benchmark results can be inflated by trivial signals, unrealistic anomaly density, subjective or incorrect labels, and run-to-failure bias | Supports reporting UCR archive results only as generic temporal robustness evidence with source split and interval provenance. Cross-domain F1, recall, or FPR cannot become municipal performance. |
| [Sun et al., negative-sequence current compensation](https://www.mdpi.com/1996-1073/15/9/3100) | Negative-sequence analysis uses unbalanced three-phase current phasors and discusses angle error and measurement asymmetry | Supports the electrical warning: even phasor-derived negative sequence is affected by measurement asymmetry, supply unbalance, and equipment effects. RMS magnitudes alone are insufficient. |

## Dataset and method assessment

Rating scale: **Strong** means the source directly observes the relevant quantity and mechanism; **Moderate** means a useful analogue exists but an important measurement or operational condition differs; **Weak** means only a generic shape or workflow transfers; **None** means the source does not contain the required evidence.

### MAD

- Measurement: **Moderate**. The source is directly from deployed AMI and includes voltage, current, active power, and power factor for three phases. However, all variables are normalized in the released representation. That prevents watt/ampere threshold transfer and prevents uncertainty analysis in the original units.
- Phase: **Moderate for phase-labelled channels; Weak for sequence analysis**. The dataset has per-phase variables, but the public description does not establish synchronized phase angles, phase order, waveform capture, or a validated Fortescue calculation. It can support a phase-magnitude feature experiment, not a negative-sequence experiment.
- Sampling: **Moderate**. Thirty-minute intervals resemble a possible AMI profile cadence and support persistent load-shape studies. They cannot validate sub-cycle, switching, flicker, transient, or controller-edge behaviour.
- Operational context: **Weak**. Smart-grid substation meters are closer to a feeder measurement than REFIT, but the public record does not establish streetlight cabinet topology, lamp count, controller schedule, or municipal maintenance workflow.
- Anomaly mechanism: **Moderate**. The dataset includes manually inspected or professionally labelled abnormal meters and six abnormal categories. The public README does not expose enough mechanism detail to map each category to a streetlight fault without an additional label dictionary and provenance audit.
- Streetlight similarity: **Weak to Moderate** for the abstract idea of polyphase AMI anomaly screening; **Weak** for a cabinet-level physical fault claim.

### REFIT annotated load anomalies

- Measurement: **Strong** for real active-power observation at aggregate and appliance levels; **None** for phase voltage/current or sequence components.
- Phase: **None**. No three-phase electrical phase information is available in the reviewed source.
- Sampling: **Strong** for appliance transitions and normal-operation modelling at 8-second intervals; **Weak** for municipal AMI at 15/30-minute intervals unless explicitly resampled and treated as a new experiment.
- Operational context: **Weak**. The operating population is domestic households in Loughborough, UK, with ordinary appliance use.
- Anomaly mechanism: **Moderate to Strong** for real appliance-behaviour anomalies as labelled by the accompanying method; **Weak** for electrical fault mechanisms. The labels are not Gold labels for a feeder or streetlight physical fault.
- Streetlight similarity: **Weak**. The useful transfer is the method principle that aggregate measurements can hide the source appliance and that submetered evidence is more informative. The appliance mechanism itself does not transfer.

### UCR Time Series Anomaly Archive: Italianpowerdemand 210, 211, and 212

- Measurement: **Weak** for LightGuard electrical measurement; the entries are generic univariate time-series benchmark representations, not phase-aware metering records. The archive records 119819, 119580, and 29931 rows for entries 210, 211, and 212 respectively.
- Phase: **None**.
- Sampling: **Moderate** only for generic temporal robustness, interval localization, and train/anomaly-boundary handling; **None** for electrical sampling, controller edges, or transients unless a separate source specification establishes those semantics.
- Operational context: **None** for municipal streetlight operations. The archive is a generic benchmark and must not be interpreted as an Italian city operational-demand source for this task.
- Anomaly mechanism: **Weak** as a generic labelled anomaly interval benchmark, with DG-C synthetic/composed archive caveats; **None** for electrical mechanisms. The official filename encodings provide train-end and anomaly-interval metadata, not a physical fault cause.
- Streetlight similarity: **None** for physical or operational similarity; **Weak** only for generic temporal robustness and interval-processing checks.
- Provenance/license risk: the archive SHA-256 is frozen as `ac4b991c701e620ae9cc5ebd57ae45593a36cc9c0b6ed5e3c4b7e466cf4783d4`; an explicit license was not established in the reviewed source and must remain unknown.

## Why RMS phase-current asymmetry is not negative-sequence current

For a three-phase system, a sequence component is formed from complex phase phasors, not just three scalar RMS magnitudes. With (a=e^{j2\pi/3}), the Fortescue form is:

```text
I0 = (Ia + Ib + Ic) / 3
I1 = (Ia + a*Ib + a^2*Ic) / 3
I2 = (Ia + a^2*Ib + a*Ic) / 3
```

The calculation depends on the relative phase angles of `Ia`, `Ib`, and `Ic`, as well as magnitude, phase order, time alignment, and the measurement window. A vector such as `(RMS Ia, RMS Ib, RMS Ic)` does not identify those angles. Different phasor triples can have identical RMS magnitudes but different `I2` values. Therefore:

- `max(Ia, Ib, Ic) - min(Ia, Ib, Ic)` or a related RMS spread is a magnitude-dispersion statistic.
- It is invariant to phase-angle changes that can alter the negative-sequence component.
- It does not separate supply unbalance, load composition, CT/transducer error, phase mapping error, harmonics, or a fault.
- It must be named `phase-current magnitude asymmetry observation` or `phase-selective anomaly sign` in LightGuard.
- The term `negative-sequence current` is permitted only after synchronized phase voltage/current quantities, phase order, instrument provenance, a defined observation window, and a validated sequence calculation are available. Even then, the result is a diagnostic feature, not a confirmed streetlight fault.

## Cross-domain metric boundary

Accuracy, recall, precision, FPR, AUROC, F1, and ranking metrics are conditional on the source population, label definition, sampling, split, prevalence, and decision unit. MAD's meter/sample label, REFIT's appliance anomaly label, and UCR archive anomaly intervals are not interchangeable with a Suyeong cabinet inspection outcome.

The same numerical score can have different meaning under different prevalence, noise, aggregation, and label processes. A benchmark metric may therefore be reported as:

- within-dataset evidence for the external benchmark and its frozen split;
- a generic temporal-robustness result if the feature, interval semantics, and source split are explicitly aligned;
- a reproducibility check for the implementation.

It may not be reported as:

- Suyeong-gu streetlight accuracy, recall, specificity, or FPR;
- the probability that a cabinet or lamp is faulty;
- evidence that a municipality-wide ranked queue will reduce field dispatches;
- a Gold or Silver field label for LightGuard's unlabeled AMI.

## Unresolved risks

| Risk | Severity | Evidence status | Required response |
|---|---|---|---|
| MAD release has normalized values and incomplete public mechanism metadata | High | Directly observed in source README | Do not transfer units, thresholds, or class names; obtain the original label dictionary and instrument metadata before any mechanism mapping. |
| MAD phase channels may be interval statistics rather than synchronized phasors | High | Phase-angle and waveform provenance absent from reviewed source | Keep P3 as magnitude asymmetry; require phasor-capable validation before any sequence terminology. |
| REFIT anomalies are appliance behaviour anomalies | High | Dataset and paper explicitly scope appliance-level detection | Use only as an aggregate-versus-submetering and persistence-method analogue. Never call it feeder or streetlight fault truth. |
| UCR archive entries 210-212 are generic labelled anomaly benchmarks | High | Official filenames encode train end and anomaly interval; archive SHA-256 is frozen | DG-C synthetic/composed caveats and unknown explicit license limit interpretation; use only for generic temporal robustness and interval handling. |
| External prevalence and label process differ from municipal maintenance outcomes | High | Structural domain mismatch | Do not pool metrics or calibrate LightGuard probabilities from external labels. |
| Aggregation can hide a failing lamp or create a feeder-level pattern from unrelated loads | High | REFIT paper's aggregate versus submetered comparison and LightGuard topology gap | Require cabinet-to-lamp/controller mapping and field outcome joins for Gold claims. |
| Sampling and archive semantics suppress or obscure electrical mechanisms | Medium | MAD 30-minute intervals and UCR DG-C benchmark entries have no LightGuard electrical measurement semantics | Restrict UCR claims to generic temporal robustness and interval handling; acquire high-resolution waveform or event data for electrical transient claims. |
| Cross-domain benchmark simplicity or label artefacts can inflate results | Medium | Wu and Keogh benchmark critique | Freeze splits and report mechanism, prevalence, label provenance, and simple baselines. |

## Adopted rules

1. External datasets validate mechanism plausibility or implementation behaviour only; they do not validate streetlight field accuracy or fault probability.
2. Preserve source labels and source units. Never reinterpret normalized MAD values as watts, amperes, or cabinet load.
3. Treat MAD class IDs as external labels until a public mechanism dictionary and inspection provenance are available.
4. Treat REFIT annotated labels as appliance-level anomalous behaviour labels, not electrical fault labels.
5. Treat UCR archive entries 210-212 as generic labelled anomaly intervals for temporal robustness only; do not interpret them as electrical mechanisms, seasonal municipal context, or streetlight outcomes.
6. Call the current RMS phase feature `phase-current magnitude asymmetry observation` or `phase-selective anomaly sign`.
7. Prohibit `negative sequence`, `negative-sequence fault`, and `negative-sequence current` unless phasor prerequisites and a validated sequence calculation are documented.
8. Do not transfer thresholds, detector weights, prevalence, calibration, or ranking cutoffs across datasets.
9. Report external metrics only with the source dataset, source split, unit of analysis, label definition, prevalence, and sampling semantics.
10. Keep unmodified LightGuard AMI separate from external benchmark data. Do not call it normal truth and do not attach municipal context to external meters.
11. Require a cabinet-to-meter-to-controller-to-lamp join plus time-aligned maintenance or inspection outcome before promoting an anomaly sign to Silver or Gold field evidence.
12. When the required measurement or outcome is unavailable, abstain and record the missingness rather than imputing it.

## Required next evidence

To make a stronger claim, the project needs a public or authorized dataset with: per-cabinet and per-lamp mapping; rated load and lamp count; timestamped controller/schedule state; voltage and current per phase; phase order and synchronized angle or waveform provenance; meter quality flags and transducer details; and time-bounded field maintenance outcomes. The join must be frozen before scoring and must distinguish service disruption, controller state, lamp failure, wiring fault, and meter fault.

## Final audit conclusion

The external sources make a defensible case for testing whether LightGuard reacts to related electrical or temporal mechanisms. They do not justify a field-performance claim. The strict v0.13 statement is:

> External benchmark transfer can support electrical anomaly-mechanism validity and feature sanity checks. It cannot establish municipal streetlight field accuracy, fault probability, or confirmed fault status.
