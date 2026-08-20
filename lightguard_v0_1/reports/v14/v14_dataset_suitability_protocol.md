# v0.14 Dataset Suitability Protocol

## Purpose and frozen predecessor boundary

This protocol ranks external data by the ability to test a declared electrical
signal mechanism, not by detector performance. It preserves v0.13 MAD as
negative/non-evaluable predecessor evidence: `SC3` coverage `5400/5414`,
balanced accuracy `0.52004485`, z-score comparator `0.66598258`, primary gate
`NOT_EVALUABLE_INCOMPLETE_COVERAGE`, and external empirical grade
`NO_EV_GRADE_NOT_EVALUABLE`. No v0.14 source reopens, tunes against, replaces,
or deletes that result.

Status: `PRE_OUTCOME_FROZEN`.

Source checked at: `2026-08-21`.

Performance reviewed: `NO`. Suitability was frozen before any external outcome
or detector-performance value was inspected.

## Gate order

Each candidate is scored in this order before any label outcome, metric, model
selection, or benchmark comparison is viewed.

| Gate | PASS condition | PARTIAL condition | FAIL condition | UNKNOWN condition |
|---|---|---|---|---|
| Real measured electrical signal | Source documents physical acquisition | Measured but transformed/proprietary-origin data limits audit | Simulation or no measurement data | Source does not establish status |
| Explicit labels | Released labels have defined classes/events | Labels exist but class/interval detail is incomplete | No released labels | Label presence cannot be established |
| Label provenance | Observed, controlled, or human correction process is documented | Coarse process documented but class/event derivation incomplete | Labels are absent or generated without declared ground truth | No source statement |
| Timestamp/time order | Timestamps/order and continuity are documented | Ordered files but timestamp schema/coverage incomplete | No usable ordering | No evidence |
| Physical units | Units/calibration are explicit | Measurement quantity but units/schema must be checked | Normalized/abstract features only | No evidence |
| Phase/channel identity | Required channel identities are explicit | Some phase channels identified but incomplete for the intended mechanism | Intended phase claim lacks channels | No evidence |
| Independent or sealable split | Author split is auditable or an entity/run/time split can be sealed before labels | Named partitions exist but construction is not auditable | No partition unit/no future sealing possible | No evidence |
| Licence | Explicit licence permits the intended use | Licence restricts intended derived sharing but use can be scoped | Licence forbids intended use | No explicit licence evidence |
| Access evidence | Official access route and dataset identity are public | Partial access evidence | No accessible required artefact | Not documented |

## Suitability grades

| Grade | Meaning | Execution decision |
|---|---|---|
| `SG-A` | All required gates pass for the declared mechanism, including explicit label and licence evidence. | Eligible after split/configuration sealing. |
| `SG-B` | Strong labelled and physical provenance but a declared mechanism limitation remains. | Eligible only for the narrow registered mechanism. |
| `SG-C` | Useful evidence exists, but one or more gate is partial/unknown and blocks confirmatory execution. | Hold until the named gate is resolved. |
| `SG-X` | A fundamental requirement fails, such as no released labels/data or no benchmarkable artefact. | Exclude from benchmark execution. |

`SG` means suitability, never quality of a model result. A high metric cannot
promote a grade. A poor metric cannot demote a provenance grade.

## Candidate decisions

| Dataset | Grade | Before-performance decision | Allowed mechanism if later released |
|---|---|---|---|
| London Met 11442 | `SG-C` | `PRIMARY_BLOCKED_PROVENANCE`: explicit licence and label provenance are absent; phase identity is insufficient. | Voltage/THD disturbance only, after gates resolve. |
| CoDEx-VFD | `SG-B` | Eligible after a pre-outcome run-disjoint seal. README confirms `Time(s)`, `Phase_A(A)`, `Phase_B(A)`, `Label`, 2.5 MHz, `NC`, A/B/C severity, and 1/2/3 frequency conditions. | Injected EMD/current-change discrimination and persistence. |
| SustDataED2 | `SG-B` | Eligible as a limited positive control after a pre-outcome chronological seal; official IEEE PES registry confirms CC BY 4.0. | Aggregate real-load transition/change, time-forward only. |
| 3PhaseInsight 21071610 | `SG-X` | Exclude: specification report has no public raw labelled benchmark. | None; contextual schema documentation only. |

## Prohibited transfers

- Do not turn a CoDEx injected-disturbance result into field fault accuracy.
- Do not treat SustDataED2 appliance transitions as cabinet or lighting failures; they are non-fault positive-control labels.
- Do not infer London Met label classes, licence, phase identity, or split construction from file names or availability.
- Do not treat the 3PhaseInsight report as access to Radius data.
- Do not use performance to choose between London Met and CoDEx. London Met may transfer to CoDEx only if the relevant provenance gate independently permits CoDEx execution.
- Do not report external evidence as Suyeong streetlight accuracy, municipal FPR/recall, production readiness, or actual fault probability.

## Required seal before any future execution

1. Freeze the exact public metadata page, source version, licence text, and applicable README identifier without recording raw-data manifests in this protocol.
2. Record the intended mechanism and every unavailable mechanism.
3. Freeze the partition at a physical unit appropriate to the source: run-disjoint for CoDEx; chronological within-house for SustDataED2 if it is released; no assumed partition for London Met.
4. Freeze transformations using training/fit data only, before confirmatory labels are read.
5. Preserve all null/blocked outcomes and publish no aggregate cross-domain score.

## Evidence basis

- [London Met record 11442](https://repository.londonmet.ac.uk/11442/)
- [CoDEx-VFD official RDR record](https://rdr.kuleuven.be/dataset.xhtml?persistentId=doi%3A10.48804%2FN4H9HP)
- [SustDataED2 data descriptor](https://www.nature.com/articles/s41597-022-01252-2)
- [IEEE PES SustDataED2 registry](https://ieee-pes-data-sharing.org/datasets/detail/46dc8c55-1836-46c0-8dfb-efded3c2c498)
- [3PhaseInsight specification report](https://zenodo.org/records/21071610)
- [3PhaseInsight project record](https://orbit.dtu.dk/en/projects/3phaseinsight/)
- [IEEE 1459-2025](https://standards.ieee.org/ieee/1459/7578/)
- [IEC 61000-4-30](https://webstore.iec.ch/en/publication/21844)
- [OSF licensing guidance](https://help.osf.io/article/148-licensing)
