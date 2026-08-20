# LightGuard v0.14 Domain Provenance Review - LUNA C

Date: 2026-08-21

## Review scope

This is a pre-outcome physical-provenance and dataset-suitability review of the four assigned original sources. It audits RMS versus instantaneous values, normalized versus SI units, phase/channel identity, current/voltage/power/THD semantics, sampling and timestamps, disturbance injection, label provenance, and domain distance.

No performance result was inspected or used. No raw external dataset was downloaded. No dataset was selected because it produced a favorable number. The review preserves the v0.13 negative/non-evaluable predecessor boundary and does not convert external electrical evidence into streetlight field accuracy or fault probability.

## Executive decision

| Candidate | Current role | Physical-provenance decision | PMC-3 decision |
|---|---|---|---|
| London Met 11442 | Candidate real-distribution voltage disturbance track | `PRIMARY_BLOCKED_PROVENANCE` until license, label construction, timestamp, preprocessing, and measurement-window metadata are supplied | `N/A` from reviewed source: no phase-current or three-phase channel set |
| CoDEx-VFD | Controlled physical current-disturbance benchmark | `CONDITIONALLY_ELIGIBLE` for run/episode-level injected-current mechanisms after README/schema verification | `INELIGIBLE_PENDING_PROVENANCE`: two directly measured phase currents and incomplete phase/representation metadata |
| SustDataED2 | Real-world change/persistence positive control | `ELIGIBLE_POSITIVE_CONTROL` for known appliance transitions, not faults | `N/A`: aggregate single-household V/I, no A/B/C phase set |
| 3PhaseInsight | Physical-provenance reference and conditional future AMI track | `REFERENCE_ONLY` until raw data access, license, labels, units, channels, and timestamps are verified | `CONDITIONAL`: eligible only after every PMC-3 gate passes |

The review does not authorize a v0.14 confirmatory run. It defines the evidence needed before the suitability freeze can authorize one.

## Source and provenance findings

### London Met distribution dataset

The official London Met record describes a minute-level dataset derived from proprietary industrial measurements supplied by Neuville Grid Data. It names upstream/downstream voltage statistics, minimum/average/maximum voltage in kV/V, THD-V in percent, and a disturbance classification label. It provides separate Train_Data.csv and Test_Data.csv files.

The record does not state:

- whether voltage values are instantaneous, RMS, or window statistics beyond the min/average/max labels;
- the voltage measurement topology, such as phase-to-neutral or line-to-line;
- phase/channel identity or current channels;
- active/reactive/apparent power semantics;
- THD calculation window, harmonic range, reference, or instrument class;
- calibration constants, transducer chain, uncertainty, or quality flags;
- timestamp columns, timezone, missingness, or exact time split construction;
- how disturbance classes were created or independently verified;
- a dataset license or explicit reuse terms.

The record explicitly says that the files are pre-processed and derived from proprietary industrial measurements with transformations for research. That makes the source useful as a possible voltage-power-quality reference but insufficient for a direct mechanism claim until the missing provenance is documented. The branch rule is therefore `PRIMARY_BLOCKED_PROVENANCE`, decided before any test-label or metric inspection.

### CoDEx-VFD

The KU Leuven RDR record identifies a versioned public experimental dataset from a three-phase VFD system under controlled electromagnetic disturbances. It declares 100 CSV measurement runs, two directly measured phase currents, binary labels for injected-disturbance presence at each time point, 2.5 MHz sampling, severity/frequency tags, and normal/no-perturbation files. The record states CC BY 4.0 and indicates that the full package is about 20.2 GB, so the repository's no-large-download rule is respected here.

The record is strong evidence for a controlled disturbance injection mechanism. It is not evidence of a natural distribution fault, an AMI event, or a streetlight failure. The landing metadata does not establish whether the CSV values are instantaneous samples or already reduced quantities, and it does not provide the exact phase/channel names, phase order, sensor calibration, SI units, clock/trigger semantics, or wall-clock timestamp behavior. The associated README is a required provenance input before implementation.

The correct experimental unit is a measurement run or disturbance episode. The 2.5 MHz rows inside one run are not independent observations. A future track may test persistence, abrupt/structural change, and multi-current consistency if those signal semantics and event boundaries are verified before labels are used for confirmatory selection.

### SustDataED2

The original Scientific Data descriptor documents 96 days of real residential electricity measurements from one Portuguese household. Raw voltage/current waveforms were sampled at 12.8 kHz. Processed data is available at 50 Hz W64 and 1 Hz CSV and contains voltage RMS, current RMS, active power, and reactive power. Calibration constants are used to scale processed measurements to original values.

The data descriptor documents that raw file names encode the first sample Unix timestamp and remaining sample times are reconstructed from the sampling rate. Appliance measurements and labels are in UTC but are not perfectly simultaneous across plugs. The labels are generated by event-detection algorithms and then visually inspected and corrected by a human; an absolute power change of at least 10 percent of the appliance consumption mode is the event criterion.

This is adequate for a known-transition positive control for persistence, baseline departure, and structural change. It is not a fault dataset: the labels identify appliance ON/OFF transitions. The aggregate main-breaker measurement is not a three-phase A/B/C measurement, so PMC-3 is not applicable. A transition score must remain a transition score and cannot be described as fault detection or streetlight evidence.

The article is CC BY 4.0 and points to the OSF record. File-level OSF terms and exact release metadata must be captured before any later import.

### 3PhaseInsight reference

The public Zenodo record is a report titled Data Specifications. It defines a data model for the three-phase smart-meter dataset delivered by Radius and names topology entities, per-phase voltage, active/reactive power, harmonic distortion, raw CSV integration, metadata, and data lineage. The DTU project page describes real customer data from Zealand and a large campaign that reconfigured existing smart meters to record three-phase measurements.

This is the most conceptually similar candidate to AMI, but the public record reviewed here is not a raw labeled-data release. The reviewed record does not establish a license for the underlying customer data, public access to the raw files, field-fault labels, exact per-channel identity, SI calibration, RMS/window semantics, sampling interval, timestamps, or an event/injection source. The report's semantic definitions are therefore physical-reference evidence, not direct confirmatory evidence.

3PhaseInsight can become a conditional PMC-3 source only if an authorized or public raw release proves all gates below. Until then its status is `REFERENCE_ONLY` and no metric or label may be produced from it.

## Measurement-semantic audit

| Audit item | London | CoDEx-VFD | SustDataED2 | 3PhaseInsight |
|---|---|---|---|---|
| RMS versus instantaneous | Not specified; min/average/max and THD-V are reported as derived/statistical fields | 2.5 MHz current time series declared, but representation is not stated on landing page | Raw instantaneous V/I is separated from processed V RMS/I RMS/P/Q | Report names per-phase metrics but does not expose raw signal representation |
| Normalized versus SI | Voltage kV/V and THD percent are stated; transformation/calibration provenance is incomplete | SI scale, sensor gain, and calibration are not stated in reviewed metadata | Calibration constants and physical derived quantities are documented | Units and calibration are not established for underlying raw data |
| Phase/channel identity | No phase channels declared | Two directly measured phase currents; exact phase names/order are not given | Aggregate V/I; no A/B/C phase identity | Per-phase semantic model, but raw channel mapping is unverified |
| Current | Not declared | Two measured phase-current channels | Raw aggregate current and current RMS | Underlying model may contain per-phase measurements; field-level access not verified |
| Voltage | Upstream/downstream voltage statistics | Not declared in landing metadata | Raw voltage and voltage RMS | Per-phase voltage is named in specification |
| Active/reactive power | Not declared | Not declared | Explicit active power and reactive power; VAR semantics in descriptor | Active/reactive power fields named, exact definitions pending |
| THD | THD-V in percent, calculation/window undefined | Not declared | Not a documented target feature in reviewed descriptor | Harmonic distortion per phase named, exact computation/window pending |
| Sampling | Minute-level | 2.5 MHz | Raw 12.8 kHz; processed 50 Hz and 1 Hz | Not established in reviewed public report |
| Timestamp | Retention and timezone unknown | Time-point labels and rate declared; wall-clock/trigger semantics unknown | First-sample Unix timestamp; appliance labels UTC; cross-plug offsets documented | Versioned lineage described; sample timestamp contract unknown |
| Disturbance origin | Unknown: natural, injected, or transformed source not stated | Controlled EMD injection with severity/frequency factors | Natural appliance state changes; no injection claimed | Natural customer/grid operation described; no injection protocol |
| Label source | Classification label declared; generator and class meaning unknown | Source injection state at each time point | Algorithm proposal plus human visual correction and 10 percent change rule | No public field label source established |

## Physical-mechanism mapping

The following statuses use `AVAILABLE`, `PARTIAL`, `N/A`, and `SURROGATE_ONLY`. `SURROGATE_ONLY` is not direct physical evidence.

| Mechanism | London | CoDEx-VFD | SustDataED2 | 3PhaseInsight |
|---|---|---|---|---|
| PMC-1 historical/contextual baseline deviation | `PARTIAL`: voltage statistics but no documented longitudinal baseline contract | `SURROGATE_ONLY`: at most run-relative normal/control reference | `AVAILABLE` for household/appliance transition context, not feeder fault context | `PARTIAL`: conceptually AMI-compatible, raw longitudinal metadata unavailable |
| PMC-2 persistence/temporal accumulation | `PARTIAL`: minute-level data, event windows unknown | `AVAILABLE` conditionally at run/episode level after schema verification | `AVAILABLE` for known natural appliance transitions | `PARTIAL` pending timestamp and event definitions |
| PMC-3 phase/channel asymmetry | `N/A` from reviewed source | `N/A` pending a complete, named, synchronized three-channel release | `N/A` | `PARTIAL` at specification level; direct use conditional on all gates |
| PMC-4 abrupt/structural change | `PARTIAL`: disturbance label and voltage statistics, source mechanism unknown | `AVAILABLE` conditionally for injected disturbance intervals | `AVAILABLE` for labeled appliance transitions | `PARTIAL` pending raw temporal data and labels |
| PMC-5 multivariate evidence consistency | `PARTIAL`: multiple voltage/THD statistics, semantics incomplete | `AVAILABLE` conditionally for verified current channels and run-level labels | `PARTIAL`: aggregate V/I/P/Q are multivariate, but not three-phase | `PARTIAL`: model names multiple physical fields, raw availability unknown |

## Exact PMC-3 eligibility rule

PMC-3 is a phase/channel asymmetry mechanism. It is not a label for any uneven scalar load, and it is not synonymous with negative-sequence current.

### All gates are mandatory

1. **At least three same-quantity channels:** the source must expose three simultaneous channels such as `I_A`, `I_B`, `I_C` or `V_A`, `V_B`, `V_C`. A three-phase apparatus with two measured currents does not satisfy this gate.
2. **Named identity and phase order:** the source documentation must identify the physical phase/channel mapping and order and must rule out unknown swaps.
3. **Common time base:** the three channels must share a documented clock or trigger, sampling interval, and observation window. Any alignment operation must be explicit and auditable.
4. **Physical scale:** SI units or raw instrument units plus calibration constants, sensor/gain metadata, and quality/uncertainty information must be available. Unknown per-channel normalization fails the direct gate.
5. **Correct signal representation:** a magnitude-asymmetry feature requires a documented common RMS window or equivalent aggregation. A negative-sequence feature additionally requires synchronized complex phasors or instantaneous waveforms, phase reference/order, fundamental extraction, and a validated Fortescue calculation. RMS magnitudes alone can never establish negative sequence.
6. **Independent label alignment:** event labels must share the same time base and their provenance must be independent of feature construction. A controlled injection label can validate an injected disturbance only; it cannot be promoted to field-fault truth.
7. **Pre-outcome split:** meter/run/episode splits and preprocessing must be frozen before confirmatory labels are inspected. Rows from a single high-rate run are not independent units.

### Operational decision

- London fails Gate 1 because no phase current or three-channel phase quantity is declared.
- CoDEx-VFD fails Gate 1 under the reviewed metadata because only two directly measured phase currents are declared; it also leaves Gates 2, 4, and 5 unresolved until the README/schema is reviewed.
- SustDataED2 fails Gate 1 because the reviewed setup is an aggregate single-household V/I stream, not an A/B/C measurement.
- 3PhaseInsight is the only conditional candidate. It must provide an underlying raw release that passes all seven gates. The public report alone is insufficient.

Until the gates pass, the only permitted wording is `phase-current magnitude asymmetry observation` or `phase/channel asymmetry observation`. The terms `negative sequence`, `negative-sequence current`, and `negative-sequence fault` are prohibited.

## Domain-distance matrix

| Dataset | AMI similarity | Streetlight similarity | Phase/current similarity | Time-scale similarity | Label similarity | Interpretation |
|---|---|---|---|---|---|---|
| London | Moderate | Weak | Weak for current/phase; moderate for voltage PQ | Moderate at minute scale | Partial/unknown | Potential voltage disturbance analogue, not a cabinet/lamp fault source |
| CoDEx-VFD | Weak | Very weak | Moderate for injected current; incomplete for phase-complete asymmetry | Very weak versus AMI cadence | Partial for injection only | Controlled mechanism evidence, not natural distribution or streetlight evidence |
| SustDataED2 | Moderate for real electricity measurement | Weak | None for three-phase asymmetry | Weak for AMI cadence; strong for transition timing | Weak for faults, strong for appliance transitions | Positive control for temporal mechanisms only |
| 3PhaseInsight | Strongest conceptual AMI similarity | Weak to moderate at network context only | Potentially strong, pending raw proof | Unknown | None established | Reference/conditional candidate, not current labeled validation |

Distance is not a performance metric. A favorable result on a distant domain would not upgrade its suitability or LightGuard's streetlight claim.

## License and label gates

| Dataset | Reviewed license status | Label gate |
|---|---|---|
| London | `UNKNOWN` on the official record | Block until generator, class semantics, event windows, and source-to-label relation are documented |
| CoDEx-VFD | `CC BY 4.0` on KU Leuven RDR | Injection labels are acceptable for controlled mechanism validation after split/schema freeze; not field fault labels |
| SustDataED2 | Article `CC BY 4.0`; verify OSF file-level terms | Human-corrected appliance transition labels only |
| 3PhaseInsight | Underlying raw-data license/access `UNKNOWN` in reviewed report record | No labeled primary use until a public/authorized label source is identified |

## Adopted controls for v0.14

1. Suitability is frozen from provenance before test labels or performance are viewed.
2. London remains `PRIMARY_BLOCKED_PROVENANCE` unless the missing license and physical/label metadata are resolved.
3. CoDEx-VFD is evaluated, if later authorized, at run/episode level with a pre-frozen representative file selection. No row-level pseudoreplication.
4. SustDataED2 is a known-transition positive control, never a fault benchmark.
5. 3PhaseInsight is not treated as an open raw benchmark merely because its public specification report is open.
6. `PMC-3` requires all seven gates. Missing provenance yields `PARTIAL`, `N/A`, or `INELIGIBLE_PENDING_PROVENANCE`, never an imputed feature.
7. External evidence remains separate from Suyeong cabinet assets, AMI, controller state, lamp state, maintenance outcomes, human review, and field truth.
8. External metrics, if later produced under a separate frozen protocol, must remain dataset-qualified and cannot become streetlight accuracy, field FPR/specificity, or actual fault probability.

## Claim boundary

The strongest claim permitted by this review is:

> A physically documented external dataset may be used to test whether a bounded LightGuard signal responds to a related electrical or temporal mechanism under that dataset's own measurement and label process.

The following claims remain unsupported:

- actual Suyeong-gu streetlight fault accuracy;
- municipal field recall, specificity, or FPR;
- probability that a cabinet or lamp is faulty;
- transfer of a controlled VFD/EMI disturbance label to a streetlight fault;
- negative-sequence current from RMS-only or incomplete phase data;
- production readiness.

## Primary and official sources

- [London Met Repository record 11442](https://repository.londonmet.ac.uk/11442/)
- [CoDEx-VFD KU Leuven RDR, DOI 10.48804/N4H9HP](https://doi.org/10.48804/N4H9HP)
- [SustDataED2, Scientific Data, DOI 10.1038/s41597-022-01252-2](https://doi.org/10.1038/s41597-022-01252-2)
- [SustDataED2 OSF record](https://doi.org/10.17605/OSF.IO/JCN2Q)
- [3PhaseInsight Data Specifications, Zenodo 21071610](https://doi.org/10.5281/zenodo.21071610)
- [DTU 3PhaseInsight project](https://wind.dtu.dk/3PhaseInsight)
- [IEEE 1459-2025](https://standards.ieee.org/ieee/1459/7578/)
- [IEC 61000-4-30:2015](https://webstore.iec.ch/en/publication/21844)
- [IEEE 1159-2019](https://standards.ieee.org/ieee/1159/6124/)
- [Fortescue 1918](https://doi.org/10.1109/T-AIEE.1918.4765570)
- [NIST CUSUM reference](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm)

## Audit conclusion

The physical-provenance gate is doing useful work: it prevents a two-channel VFD experiment, a single-household appliance transition corpus, a voltage-only derived dataset, or an open specification report from being mislabeled as direct three-phase streetlight-fault evidence. v0.14 may proceed only with the narrow roles and conditional gates above. The absence of direct PMC-3 eligibility in the current public evidence is a valid provenance conclusion, not a missing performance result.
