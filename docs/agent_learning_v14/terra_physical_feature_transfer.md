# TERRA B Physical Feature Transfer Methodology Record

**Role:** TERRA B Physical Feature Transfer Methodologist  
**Actual Model:** terra  
**Date:** 2026-08-21  
**Scope:** Pre-outcome physical-mechanism transfer design for external electrical data. This record does not report a benchmark result and does not establish streetlight field accuracy, fault recall, or fault probability.

## Sources Reviewed

| Source | Type | What was adopted |
| --- | --- | --- |
| [London Met distribution dataset](https://repository.londonmet.ac.uk/11442/) | Official dataset record | It reports minute-level upstream/downstream voltage statistics, voltage THD, an assigned disturbance class, and preprocessed proprietary source measurements. Physical-unit, timestamp, label-generation, and licence details remain a gate rather than an assumption. |
| [CoDEx-VFD](https://doi.org/10.48804/N4H9HP) | Official KU Leuven dataset DOI | The data are 100 measurement runs from a controlled three-phase VFD disturbance experiment, with two measured current channels, point labels, metadata, and CC BY 4.0. The run, not the 2.5 MHz row, is the independent unit. |
| [SustDataED2 paper](https://doi.org/10.1038/s41597-022-01252-2) | Primary dataset paper | Real residential voltage/current waveforms, power signals, timestamps, and human-corrected appliance transitions can serve only as a change/persistence positive control. A transition is not a fault. |
| [SustDataED2 OSF record](https://doi.org/10.17605/OSF.IO/JCN2Q) | Official dataset record | Reuse, version, and licence must be reconciled with the IEEE registry before activation. |
| [NIST CUSUM control charts](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm) | Official methodology | CUSUM accumulates departures from an in-control reference. Its reference and decision parameters are calibration-only. |
| [Page, 1954](https://doi.org/10.1093/biomet/41.1-2.100) | Primary methodology | Sequential change evidence is an episode/process signal, not independent evidence at every raw row. |
| [Rousseeuw and Croux, 1993](https://doi.org/10.1080/01621459.1993.10476408) | Primary methodology | Median/MAD robust scale is a transparent baseline estimator; a zero or unsupported scale makes a component unavailable rather than imputed. |
| [Bai and Perron, 2003](https://doi.org/10.1002/jae.659) | Primary methodology | Structural change is a change-point observation that requires a defined ordered series; a detected break does not identify its physical cause. |
| [IEEE 1459-2025](https://standards.ieee.org/ieee/1459/7578/) | Official electrical-measurement standard | Balanced/unbalanced measurement terminology is constrained by documented quantities and observation periods. |
| [Fortescue, 1918](https://doi.org/10.1109/paiee.1918.6594104) | Primary electrical method | Symmetrical components require complex phasor information. Two channels or RMS magnitudes alone cannot be described as negative sequence. |
| [Cameron and Miller, 2015](https://doi.org/10.3368/jhr.50.2.317) | Primary methodology | Uncertainty must respect run/event/day/appliance clustering; row-level naive bootstrap is prohibited. |

## Dataset Type, Label, and Physical Provenance

| Dataset | Type | Licence | Label provenance | Physical provenance | Main risk |
| --- | --- | --- | --- | --- | --- |
| London | Real distribution-derived, preprocessed time series | Provisional: official record did not expose a licence in reviewed metadata | Disturbance-class method and class meanings provisional | Voltage min/mean/max and THD are publicly described in V/kV and percent; timestamp retention and transformations are provisional | Preprocessing can remove time, unit, and causal meaning. |
| CoDEx-VFD | Controlled real-current laboratory experiment | CC BY 4.0 reported by the official record | Binary injected-disturbance interval label; injection metadata documented in README | Two directly measured current channels at 2.5 MHz; three-phase completeness is absent | VFD/EMI and high-rate waveforms are not AMI or streetlight faults. |
| SustDataED2 | Real residential electricity with labelled transitions | Provisional until OSF and IEEE records agree | Human-corrected appliance ON/OFF transitions | Timestamped voltage/current waveform and derived power measurements; phase identity is not assumed | Natural appliance transitions are positive controls, not anomalies or faults. |

## Adopted Rules

1. Suitability is determined by licence, label provenance, physical provenance, temporal ordering, and independent-unit feasibility before any confirmatory outcome. Performance never changes suitability.
2. Each Physical Mechanism Core (PMC) component must be `AVAILABLE`, `PARTIAL`, `N/A`, or `SURROGATE_ONLY`. No absent meter, phase, timestamp, unit, or channel is synthesized.
3. Historical baseline means an entity- and time-linked prior reference. A run-local or record-local baseline is explicitly `SURROGATE_ONLY`, not direct historical-baseline evidence.
4. PMC-3 is a documented channel contrast only when named, aligned current channels have compatible physical scale. It is never negative/zero sequence or a fault type without complex A/B/C phasors and the required electrical context.
5. CoDEx point rows inherit the measurement-run/episode cluster. SustData observations inherit event, day, and appliance clusters. London uses only a source-defined independent sample/time block; otherwise inferential metrics are not evaluable.
6. All feature definitions, unit requirements, split functions, comparator definitions, threshold grids, metrics, primary gates, and seeds are frozen before confirmatory labels are read. Calibration is the only stage allowed to choose from the frozen grid.
7. SustData transition labels test response to known physical state changes. They are neither fault labels nor an accuracy proxy for a municipal lighting system.
8. A simple transparent comparator is evaluated in every activated track. A better comparator result is retained as negative or limiting evidence.

## Methodological Suitability Decision

The protocol is scientifically suitable for a constrained question: whether named electrical mechanisms respond to external distribution disturbances, controlled current injections, or known residential state changes when their physical provenance is retained. It is not suitable for estimating streetlight field accuracy, municipal false-positive rates, causal fault mechanism, or actual fault probability. Dataset-specific activation remains provisional until TERRA A completes the provenance gate.
