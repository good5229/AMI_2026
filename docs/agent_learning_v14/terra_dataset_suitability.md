# v0.14 TERRA-A Dataset Suitability Methodology

## Role

TERRA A Dataset Suitability Methodologist.

## Actual Model

`terra`.

## Freeze Status

- Status: `PRE_OUTCOME_FROZEN`
- Source checked at: `2026-08-21`
- Performance reviewed: `NO`. No outcome, detector score, or benchmark result
  was read or used to decide suitability.

## Decision rule learned

Dataset suitability is decided before, and independently from, any detector
score. A dataset can be useful for a narrow electrical-signal mechanism while
being unsuitable for a municipal streetlight fault claim. A result may never
upgrade missing provenance, an unknown licence, or a non-auditable split.

## Sources Reviewed

| Source | Type | What it establishes |
|---|---|---|
| [London Met repository 11442](https://repository.londonmet.ac.uk/11442/) | Official dataset record | Minute-level upstream/downstream voltage statistics and THD-V, 16 MB train and 14 MB test files, proprietary-origin transformations, and a disturbance label. |
| [CoDEx-VFD, DOI 10.48804/N4H9HP](https://rdr.kuleuven.be/dataset.xhtml?persistentId=doi%3A10.48804%2FN4H9HP) | Official dataset record | Open CC BY 4.0 experimental data, 100 CSV runs, 2.5 MHz, two directly measured phase-current channels, and injected-disturbance binary labels. |
| [SustDataED2, Scientific Data](https://www.nature.com/articles/s41597-022-01252-2) | Peer-reviewed data descriptor | One real household, 96 days, raw voltage/current waveforms, physical calibration, timestamps, 18 appliance channels, and corrected transition labels. |
| [SustDataED2 OSF DOI](https://doi.org/10.17605/OSF.IO/JCN2Q) | Official repository identifier | The cited data location; licence must be read from the project/component metadata, not inferred from open access. |
| [IEEE PES SustDataED2 registry](https://ieee-pes-data-sharing.org/datasets/detail/46dc8c55-1836-46c0-8dfb-efded3c2c498) | Official dataset registry | Explicit `CC BY 4.0` dataset licence. |
| [3PhaseInsight data specifications, Zenodo 21071610](https://zenodo.org/records/21071610) | Official project report | A data model/specification for Radius three-phase smart-meter data, not a released labelled measurement dataset. |
| [3PhaseInsight project, DTU](https://orbit.dtu.dk/en/projects/3phaseinsight/) | Official project record | Radius/DSO context, sensitive realistic data setting, and per-phase measurement purpose. |
| [IEEE 1459-2025](https://standards.ieee.org/ieee/1459/7578/) | Authoritative standard | Unbalanced electrical quantities require defined measurements and notation; channel identity cannot be assumed from generic current fields. |
| [IEC 61000-4-30:2015](https://webstore.iec.ch/en/publication/21844) | Authoritative standard | Power-quality interpretation depends on documented, repeatable in-situ measurement methods. |
| [OSF licensing guidance](https://help.osf.io/article/148-licensing) | Official repository guidance | Public access does not establish reuse rights; missing explicit licence remains `UNKNOWN`. |
| [NIST CUSUM](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm) | Official methodology reference | A time-ordered baseline is necessary for a cumulative-deviation interpretation; CUSUM is not a substitute for a ground-truth label. |

## Dataset Type and Suitability Findings

### London Met repository 11442

- Dataset type: real, pre-processed industrial distribution-system power-quality measurements, derived from proprietary Neuville Grid Data.
- Licence: `UNKNOWN`. The record exposes downloads but does not state a data-use licence. Open download is not a licence.
- Label provenance: `UNKNOWN`. A disturbance classification label is stated, but class names, originating event source, labelling procedure, and whether labels are observed or derived are absent from the public record.
- Physical provenance: voltage statistics in `kV` and `V`, THD-V in percent, and upstream/downstream context are stated. The public description does not identify phase-resolved channels; it therefore cannot support phase-current mechanism claims.
- Split/seal: named train/test files exist, but partition unit, chronology, and construction are undocumented. They are sealable only after acquisition and manifest hashing, not yet an auditable independent split.
- Adopted grade: `SG-C` (`PARTIAL` suitability only). It is a possible voltage/THD disturbance candidate after licence and label-provenance resolution, never a phase-current or streetlight benchmark.

### CoDEx-VFD

- Dataset type: real, controlled laboratory VFD experiment; it is not simulated and is not a field failure dataset.
- Licence: `PASS`, CC BY 4.0, confirmed from the official KU Leuven API/record.
- Label provenance: `PASS`, binary label states the presence or absence of a deliberately injected electromagnetic disturbance at each time point. This is a known experimental intervention, not a maintenance outcome.
- Physical provenance: the released README identifies `Time(s)`, `Phase_A(A)`, `Phase_B(A)`, and `Label`, sampled at 2.5 MHz. These are two identified current channels, not a complete three-phase phasor record.
- Split/seal: 100 individual CSV measurement runs span normal condition (`NC`) and controlled A/B/C severity with 1/2/3 frequency conditions. A run-disjoint partition can be pre-registered; the repository does not prescribe a train/test split.
- Adopted grade: `SG-B`. It is eligible only for a pre-registered, run-disjoint replication of injected electrical-disturbance discrimination and current-change persistence. It cannot establish field-fault accuracy, fault probability, or full three-phase sequence quantities.

### SustDataED2

- Dataset type: real single-household electrical monitoring, not simulation and not a grid-fault experiment.
- Licence: `PASS`, CC BY 4.0, explicitly stated in the official IEEE PES SustDataED2 registry. The open-access article is supporting provenance, not the licence evidence.
- Label provenance: `PASS` for appliance ON/OFF transition ground truth. The Nature data descriptor states that human review corrected false positives and false negatives, applies the stated 10% change rule, and reports 12,252 labels. These are transitions, not faults.
- Physical provenance: actual 96-day household monitoring; 12.8 kHz voltage/current waveform acquisition; 1 Hz active/reactive power, voltage RMS, and current RMS; UTC transition timestamps; calibrated original scale. It is one aggregate single-phase household service, so per-phase identity is `FAIL`.
- Split/seal: timestamps permit a chronological split, but there is one household and no author train/test partition. Any holdout is a time-forward within-house split, not independent household transport.
- Adopted grade: `SG-B`. It is a limited positive-control candidate for real-world transition/change replication after a pre-outcome time-forward seal. It cannot test a three-phase mechanism or a streetlight field-fault outcome.

### 3PhaseInsight Zenodo 21071610

- Dataset type: public data-specification report, not the Radius raw measurement release.
- Licence: `UNKNOWN` for the report/data-specification record and no released raw-data licence is evidenced here.
- Label provenance: `FAIL`; no released outcome labels or event annotations.
- Physical provenance: the report documents semantic fields for per-phase voltage, active/reactive power, and harmonic distortion. It demonstrates that the underlying project context is physically three-phase, but provides no public rows, file manifest, sampling coverage, or accessible raw series.
- Split/seal: `FAIL`; no public labelled data artefact or partition exists to seal.
- Adopted grade: `SG-X`. It is contextual documentation only and is excluded from benchmark execution. No attempt is made to infer, request, or substitute sensitive Radius data.

## Risks

- A labelled controlled perturbation is valid for an intervention mechanism but not for real field-failure accuracy.
- A source can preserve physical units while still lack the phase channels needed for a phase-current claim.
- Public hosting, a DOI, or an open-access paper does not prove a reusable dataset licence.
- A nominal train/test filename does not prove temporal or entity disjointness.
- London Met results must not cause a performance-driven route change to CoDEx. CoDEx eligibility is decided only by its independent provenance gate.

## Adopted Rules

1. Apply `PASS`, `PARTIAL`, `FAIL`, or `UNKNOWN` to every gate before inspecting outcome performance.
2. Assign `SG-A` only when explicit labels and their provenance, physical and temporal provenance, phase/channel meaning as needed, a sealable independent split, and a usable licence are all verified.
3. Treat `UNKNOWN` licence or label provenance as a gating condition, not as a favourable assumption.
4. Permit CoDEx only under its own sealed run-disjoint protocol; London Met is `PRIMARY_BLOCKED_PROVENANCE` and may not route, replace, or justify CoDEx based on any measured performance.
5. Call an RMS-current observation a current-channel observation unless the required phase identity and measurement conditions are documented. Do not call it a negative-sequence measurement.
6. Report any external result as dataset-specific electrical mechanism evidence only. Never express it as Suyeong streetlight field accuracy, field FPR/recall, or actual fault probability.
