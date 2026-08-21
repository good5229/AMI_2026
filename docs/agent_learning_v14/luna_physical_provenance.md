# LUNA C v0.14 Physical-Provenance Learning Record

Date: 2026-08-21

## Role

- Role: LUNA C, Physical-Provenance Reviewer.
- Task: independently audit the original London Met, CoDEx-VFD, SustDataED2, and 3PhaseInsight sources for measurement semantics, physical provenance, label provenance, and domain distance.
- Work boundary: literature and official-metadata review only. No Git operation, test, build, benchmark, performance analysis, raw-data download, or detector change was performed.
- Claim boundary: this record can support dataset suitability and external physical-mechanism replication design. It cannot support streetlight field accuracy, municipal performance, or fault probability.

## Actual Model

GPT-5, Codex runtime, acting in the LUNA C role.

## Decision

The four candidates do not currently provide an unconditional direct `PMC-3` path. CoDEx-VFD has controlled, directly measured current channels, but the official landing metadata describes two directly measured phase currents rather than a complete, phase-identified A/B/C set. London exposes voltage statistics and THD-V, not phase currents. SustDataED2 exposes single-household aggregate voltage/current waveforms and derived RMS/P/Q, not three-phase channels. 3PhaseInsight is the closest physical-provenance reference for per-phase smart-meter data, but the reviewed public Zenodo record is a data-specification report, not a labeled raw-data release; the raw channel, unit, timestamp, and label access contract remains unverified.

The safe v0.14 interpretation is therefore:

- London: possible voltage-disturbance reference, blocked as a primary validation candidate until license, label-generation, timestamp, and preprocessing provenance are documented.
- CoDEx-VFD: eligible only for controlled current-disturbance mechanisms, using run or disturbance episode as the unit. `PMC-3` is not eligible from the reviewed metadata.
- SustDataED2: eligible as a real-world state-change and persistence positive control. Appliance transition labels are not fault labels, and `PMC-3` is not applicable.
- 3PhaseInsight: physical-provenance reference or conditional future candidate. It is not a current confirmatory labeled benchmark.

## Sources Reviewed

### Assigned original sources

| Source | Evidence reviewed | Provenance conclusion |
|---|---|---|
| [London Met Repository record 11442](https://repository.londonmet.ac.uk/11442/) | Minute-level electrical-distribution time series; upstream/downstream voltage statistics; minimum, average, and maximum voltage in kV/V; THD-V in percent; disturbance classification label; Train_Data.csv and Test_Data.csv; derived from proprietary Neuville Grid Data measurements with research transformations | Real distribution-system-derived material is claimed, but the public record does not specify label construction, measurement window, timestamp fields, channel identity, calibration, or a reuse license. Treat as `PRIMARY_BLOCKED_PROVENANCE` until those are supplied. |
| [CoDEx-VFD, KU Leuven RDR, DOI 10.48804/N4H9HP](https://doi.org/10.48804/N4H9HP) | Version 1.0; 100 CSV measurement runs; three-phase VFD system; controlled electromagnetic disturbances; two directly measured phase currents; binary injected-disturbance label at each time point; 2.5 MHz sampling; severity/frequency tags; public file metadata; 20.2 GB Globus package | Strong controlled-experiment provenance for injected current disturbance. The landing metadata does not establish RMS versus instantaneous representation, SI calibration, exact phase names/order, wall-clock timestamps, or a three-channel phase set. |
| [SustDataED2, Pereira et al., Scientific Data, DOI 10.1038/s41597-022-01252-2](https://doi.org/10.1038/s41597-022-01252-2) and [OSF record](https://doi.org/10.17605/OSF.IO/JCN2Q) | One Portuguese household over 96 days; raw V/I at 12.8 kHz; processed 50 Hz W64 and 1 Hz CSV; voltage RMS, current RMS, active power, and reactive power; first-sample Unix timestamps; UTC appliance labels; semi-automatic labels corrected by visual inspection; 10 percent appliance-event rule | Strong real-world measurement and transition provenance for one household. It is single-phase aggregate/appliance data, not a three-phase feeder or streetlight-fault dataset. The article is CC BY 4.0; file-level OSF terms must still be recorded before import. |
| [3PhaseInsight Data Specifications, Zenodo 21071610](https://doi.org/10.5281/zenodo.21071610) and [DTU project page](https://wind.dtu.dk/3PhaseInsight) | Public report defining a model for Radius three-phase smart-meter data; topology relationships; per-phase voltage, active/reactive power, and harmonic-distortion fields; raw CSV and metadata lineage concepts; DTU description of real customer data from Zealand and a large reconfigured three-phase meter campaign | The report provides semantic and topology context. It does not itself prove public raw-data access, labeled events, license for raw customer data, exact sampling/timestamp contract, or measurement calibration. Keep as `REFERENCE_ONLY` until the underlying release is independently accessible and its terms are verified. |

### Additional authoritative standards and primary methods

| Source | Adopted methodological point |
|---|---|
| [IEEE 1459-2025](https://standards.ieee.org/ieee/1459/7578/) | Electric-power quantities under sinusoidal, nonsinusoidal, balanced, and unbalanced conditions require defined quantities, notation, observation periods, filtering, and phase-sequence treatment. A scalar RMS spread is not automatically a sequence component. |
| [IEC 61000-4-30:2015](https://webstore.iec.ch/en/publication/21844) | Power-quality measurement and interpretation are method-dependent and intended to be repeatable. The scope includes voltage magnitude, unbalance, harmonics, and current measurements in 50/60 Hz AC systems; a dataset must preserve the measurement class/window semantics before a standard PQ interpretation is assigned. |
| [IEEE 1159-2019](https://standards.ieee.org/ieee/1159/6124/) | Monitoring a polyphase AC system requires consistent descriptions of nominal conditions and deviations, including source/load interactions and interpretation of monitoring results. A disturbance label is not automatically a component fault label. |
| [Fortescue, 1918, Method of Symmetrical Co-Ordinates](https://doi.org/10.1109/T-AIEE.1918.4765570) | Symmetrical components are formed from phase-referenced rotating vectors. Three unlabelled RMS magnitudes do not contain the relative phase information needed to calculate negative-sequence current. |
| [NIST/SEMATECH CUSUM control charts](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm) | Persistence or change detection requires an in-control reference and a defined time order. It does not supply a universal electrical threshold or a fault interpretation. |

The additional sources are methodological controls, not performance evidence. No external performance number was used to decide suitability.

## Dataset Type, License, Label Provenance, and Physical Provenance

### London Met

- Dataset type: processed and derived minute-level power-quality dataset from proprietary industrial distribution measurements.
- License: `UNKNOWN` in the reviewed public record. The page provides download links and provenance language but no dataset license or explicit reuse terms.
- Label provenance: a disturbance classification label is declared, but the label-generation method, class definitions, annotation authority, event window, and relation to the proprietary source are not documented on the reviewed record.
- Physical provenance: voltage statistics and THD-V are described in kV/V and percent. The record does not identify RMS or instantaneous voltage, voltage-to-neutral versus line-to-line semantics, phase channels, current, active/reactive power, calibration, transducer class, or observation window.
- Time provenance: minute-level sampling is declared. Timestamp retention, timezone, missingness, and train/test time relationship are not established by the public abstract.
- Disturbance provenance: the record calls the data disturbance-classified, but does not say whether disturbances are naturally observed, injected, simulated from proprietary data, or labeled after an event review.
- Suitability consequence: block primary physical validation until license and label/measurement provenance are supplied. If resolved, it can test voltage-statistic/THD deviation and structural disturbance only; `PMC-3` is not applicable without current or voltage phase channels.

### CoDEx-VFD

- Dataset type: controlled laboratory electromagnetic-disturbance experiment on a three-phase variable-frequency drive.
- License: `CC BY 4.0` on the KU Leuven RDR record; cite the dataset and preserve attribution.
- Label provenance: binary labels mark the presence or absence of an injected disturbance at each time point. This is a controlled injection label, not a field-fault or streetlight label.
- Physical provenance: the record declares two directly measured phase currents and a 2.5 MHz sampling rate. It does not, on the landing page, declare whether CSV values are instantaneous samples or windowed RMS/features, SI calibration/gain, exact channel names, phase order, current-sensor type, or a common trigger timestamp. The README is required before those fields can be promoted from `UNKNOWN`.
- Time provenance: sample rate and time-point labels are declared, but a wall-clock timestamp, time zone, clock synchronization, and event-window construction are not. The safe unit is a measurement run or injected disturbance episode, not an individual row.
- Disturbance provenance: controlled EMD injection with documented severity/frequency categories and normal/no-perturbation runs. Severity/frequency tags are experimental factors, not fault mechanisms.
- Suitability consequence: eligible for `PMC-2` persistence, `PMC-4` abrupt/structural change, and `PMC-5` multichannel consistency only after the README and file schema verify the signal representation and label alignment. `PMC-1` is at most a run-relative control baseline, not a meter-relative historical baseline. `PMC-3` is not eligible from two channels or unverified phase identity.

### SustDataED2

- Dataset type: real-world single-household aggregate and appliance-level electricity monitoring with high-frequency waveforms and derived low-rate features.
- License: article rights are `CC BY 4.0`; verify the OSF file-level terms and attribution requirements before any import.
- Label provenance: event detection algorithms locate appliance power events, then a human visually inspects and corrects false positives and false negatives. A change of at least 10 percent of an appliance consumption mode is the labeling criterion. These are appliance ON/OFF transition labels, not faults.
- Physical provenance: raw voltage/current waveforms are sampled at 12.8 kHz. Processed data explicitly contains voltage RMS, current RMS, active power, and reactive power at 50 Hz W64 and 1 Hz CSV. Calibration constants are provided for scaling to original values. The monitored aggregate is at the main breaker of one household; no A/B/C phase identity is supplied.
- Time provenance: raw file names encode the first sample Unix timestamp, and subsequent samples are reconstructed from the sampling rate. Appliance measurements are UTC but not simultaneous across plugs; alignment is required. Appliance labels can map to aggregate samples with up to about two seconds delay.
- Disturbance provenance: no injected electrical disturbance is claimed. The transition is a natural appliance state change observed during deployment.
- Suitability consequence: positive control for persistence, change, and baseline response around known transitions. `PMC-3` is `N/A`, and transition uplift must not be interpreted as fault detection.

### 3PhaseInsight

- Dataset type: data specification and model for real three-phase smart-meter data from Radius, with topology and per-phase measurement semantics.
- License: the reviewed Zenodo report record shows no usable license value for the underlying customer data. Treat raw-data license/access as `UNKNOWN`; do not infer that an open report makes the raw dataset open.
- Label provenance: no public fault/event label source is established in the reviewed report or project page. The project describes analytics and use cases, not a released field-outcome label table.
- Physical provenance: the specification names per-phase voltage, active/reactive power, and harmonic-distortion fields and topology relationships. Exact phase-to-channel mapping, current versus voltage sensor semantics, SI units, calibration, RMS/window definitions, sampling rate, timestamps, missingness, and raw-file access remain to be verified against the underlying release.
- Time provenance: versioned topology and data-lineage concepts are described, but the public report page does not establish a usable sample timestamp contract for confirmatory analysis.
- Disturbance provenance: natural customer/grid operation is described; no controlled injection protocol is documented.
- Suitability consequence: useful physical-reference material and a conditional future candidate. It is not a current labeled primary benchmark. `PMC-3` is `PARTIAL` at the specification level and becomes eligible only if the underlying data satisfies all conditions below.

## Audit by Measurement Semantic

| Semantic | Required interpretation | London | CoDEx-VFD | SustDataED2 | 3PhaseInsight |
|---|---|---|---|---|---|
| RMS vs instantaneous | Preserve the actual representation and window; never infer one from a column name or sampling rate | Voltage min/avg/max and THD-V are described; RMS/window is not stated | Current time series at 2.5 MHz; instantaneous versus RMS/windowed is not stated on the landing page | Raw V/I waveform versus explicit processed V RMS/I RMS/P/Q | Report names measurement concepts but does not expose the raw representation |
| Normalized vs SI | Unit, scale, calibration, and per-channel gain must be documented | Voltage kV/V and THD percent are stated; preprocessing and calibration are not | SI units and sensor calibration are not stated in the landing metadata | Calibration constants and original-value scaling are documented; processed physical quantities are explicit | Unit/calibration contract is not established in the reviewed report |
| Phase/channel identity | Named channels, phase order, common time base, and channel mapping are required | No phase current/channel identity | Two directly measured phase currents; exact phase identity/order is not established | Aggregate single-household V/I; no A/B/C set | Per-phase semantics are described; raw channel mapping is not yet verified |
| Current/voltage/power/THD | Do not derive a missing physical quantity or rename a ratio | Voltage statistics and THD-V only | Current only in the public description; no P/Q/THD semantics | Raw V/I and derived active/reactive power plus V/I RMS | Per-phase voltage, active/reactive power, harmonic distortion in the model; exact field definitions pending |
| Sampling/timestamps | Retain sample interval, clock/time zone, missingness, and event alignment | Minute-level declared; timestamp contract unknown | 2.5 MHz and time-point labels declared; wall-clock/trigger contract unknown | 12.8 kHz raw, 50 Hz W64, 1 Hz CSV; first-sample Unix timestamp and UTC label semantics documented | Project-level data lineage described; sample timestamp contract unknown |
| Disturbance injection | Separate controlled injection labels from natural events and faults | Injection/natural origin unknown | Controlled EMD injection; binary time-point labels | No injection; natural appliance transitions | No injection protocol established |
| Label source | Record who/what created labels and what they mean | Method and class semantics unknown | Experimental injection state | Semi-automatic detection plus human correction, appliance transition rule | No released field label source established |

## Domain Distance

Qualitative distance is a suitability descriptor, not a performance result.

| Dataset | AMI similarity | Streetlight similarity | Phase/current similarity | Time-scale similarity | Label similarity | Main distance |
|---|---|---|---|---|---|---|
| London | Moderate for distribution measurement | Weak | Weak for current/phase; moderate for voltage PQ | Moderate at minute scale | Partial/unknown | Proprietary-derived voltage-only semantics and unverified labels/license |
| CoDEx-VFD | Weak | Very weak | Moderate for controlled current disturbance, weak for three-phase phase-complete analysis | Very weak versus 15/30-minute AMI | Partial for injected disturbance only | VFD/EMI laboratory domain and 2.5 MHz scale |
| SustDataED2 | Moderate for real electrical measurement | Weak | None for three-phase phase asymmetry | Weak for AMI cadence, strong for high-rate transition timing | Weak for faults; strong for appliance transitions | Single Portuguese household and appliance labels |
| 3PhaseInsight | Strongest conceptual AMI similarity | Weak to moderate at network context only | Potentially strong, pending raw channel proof | Unknown pending sample metadata | None established | Raw access, license, labels, units, and timestamps not public in reviewed record |

## Exact PMC-3 Eligibility Rule

`PMC-3` means phase/channel asymmetry. It is not a synonym for negative-sequence current.

### Direct PMC-3 eligibility: every gate must pass

1. **Three channels:** at least three simultaneous channels of the same physical quantity are present and named, such as `I_A`, `I_B`, and `I_C` or `V_A`, `V_B`, and `V_C`. A three-phase device with only two measured channels is insufficient.
2. **Identity and order:** the source documentation identifies phase/channel mapping and phase order, and rules out channel swaps or unknown per-channel wiring.
3. **Common time base:** channels share a documented clock, trigger, sampling interval, and observation window. Independent channel timestamps must be aligned with an auditable method before scoring.
4. **Physical scale:** values are in SI units or raw instrument units with calibration constants, sensor/gain metadata, and uncertainty/quality information. Unknown or per-channel normalized values are not direct physical evidence.
5. **Signal semantics:** if the feature is RMS asymmetry, the common RMS window and aggregation method are documented. If the feature is negative sequence, synchronized complex phasors or instantaneous waveforms with phase reference, fundamental extraction, and a validated Fortescue calculation are mandatory. Three scalar RMS magnitudes never satisfy the negative-sequence gate.
6. **Label alignment:** any event label is on the same time base and its provenance is independent of the feature calculation. Injection labels may validate an injected disturbance mechanism, but they do not become field-fault labels.
7. **Split integrity:** calibration and confirmatory runs/meters/episodes are frozen before confirmatory labels are inspected. Rows from one run or episode are not independent units.

### Dataset-specific PMC-3 status

| Dataset | PMC-3 status | Reason |
|---|---|---|
| London | `N/A` under reviewed source | No phase-current or phase-channel measurement is declared; voltage statistics and THD-V do not establish three-phase channels. |
| CoDEx-VFD | `INELIGIBLE_PENDING_PROVENANCE` | The record declares two directly measured phase currents, not three named synchronized channels; RMS/instantaneous, phase identity/order, units, and trigger semantics require README/file verification. |
| SustDataED2 | `N/A` | The reviewed setup is an aggregate single-household V/I measurement and processed RMS/P/Q, with no A/B/C phase set. |
| 3PhaseInsight | `CONDITIONAL` | Project semantics describe three-phase per-phase data, but raw channel identity, units, time base, and license/access must be verified in the underlying data before any direct PMC-3 analysis. |

### Prohibited terminology

Until all direct gates pass, use `phase-current magnitude asymmetry observation` or `phase/channel asymmetry observation`. Do not use `negative sequence`, `negative-sequence current`, or `negative-sequence fault` for RMS-only or incomplete phase data.

## Adopted Rules

1. Dataset suitability is decided from license, label provenance, and physical provenance before any result is viewed. Performance cannot upgrade a dataset.
2. Preserve source semantics. Do not turn voltage statistics into current, current RMS into instantaneous current, THD-V into a generic harmonic fault, or normalized values into SI units.
3. Treat London as `PRIMARY_BLOCKED_PROVENANCE` until the license, label-generation method, timestamps, preprocessing, measurement windows, and channel metadata are documented.
4. Treat CoDEx-VFD as a controlled VFD/EMI mechanism dataset. Use runs or disturbance episodes as experimental units, never independent rows.
5. Treat SustDataED2 labels as human-corrected appliance transitions. It is a positive control for temporal change/persistence, never a fault benchmark.
6. Treat 3PhaseInsight's public specification as a physical-reference document, not proof of an open labeled raw dataset.
7. Permit direct PMC-3 only when all seven eligibility gates pass. RMS-only data may support magnitude asymmetry only; negative-sequence language requires phasors or synchronized waveforms and a validated sequence calculation.
8. Keep external mechanism evidence separate from LightGuard's Suyeong cabinet, lamp, controller, AMI, maintenance, and field-truth layers.
9. Do not use external labels to estimate actual fault probability, municipal recall, field specificity, or production readiness.
10. Keep unresolved metadata as `UNKNOWN`, `PARTIAL`, or `N/A`; do not impute physical provenance.

## Risks

| Risk | Severity | Mitigation |
|---|---|---|
| London proprietary-derived transformations can hide sensor, window, and label semantics | High | Block primary use until provenance and license are documented; do not infer from CSV names or voltage units alone. |
| CoDEx row-level labels and 2.5 MHz sampling invite pseudoreplication | High | Freeze run/episode splits and cluster all uncertainty and summaries at run/episode level. |
| CoDEx's two current channels may be mistaken for a complete three-phase measurement | High | Require three named simultaneous channels for PMC-3; otherwise use PMC-2/4/5 only if signal semantics are verified. |
| SustDataED2 transition labels may be promoted to fault labels | High | Name the endpoint `known appliance transition`; prohibit fault language. |
| 3PhaseInsight report availability may be confused with raw customer-data availability | High | Separate report license/access from underlying raw-data terms; require a source-level raw manifest before import. |
| RMS, P/Q, and THD quantities may be compared across incompatible windows or calibration classes | Medium | Record window, sampling, calibration, unit, and method metadata for every derived feature. |
| Phase identity or time alignment errors can create false asymmetry | High | Require channel mapping, phase order, synchronized clock/trigger, and quality flags before PMC-3. |

## Final Learning Conclusion

Physical provenance is a prerequisite for mechanism replication, not a cosmetic metadata field. The v0.13 MAD limitation is therefore not repaired by finding a better score on a new dataset. The defensible v0.14 path is to use CoDEx-VFD for controlled injected-current mechanisms, SustDataED2 for real state-change/persistence positive control, London only after its provenance gate is cleared, and 3PhaseInsight only after the underlying per-phase raw-data and label/access contract is proven. None of these reviewed sources currently supplies direct evidence of Suyeong streetlight field accuracy or actual cabinet fault probability.
