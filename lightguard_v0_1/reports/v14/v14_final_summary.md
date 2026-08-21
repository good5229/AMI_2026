# LightGuard v0.14 Physical-Provenance External Replication

## Release state
- v0.13 predecessor: FROZEN_NEGATIVE_NON_EVALUABLE
- London Met: PRIMARY_BLOCKED_PROVENANCE
- CoDEx-VFD: EVALUATED_PARTIAL_RUN_PREFIX
- SustDataED2: EVALUATED_POSITIVE_CONTROL
- 3PhaseInsight: REFERENCE_ONLY_NO_PUBLIC_LABELLED_RAW_DATA
- Evaluated physical-provenance tracks: 2

## Interpretation
CoDEx-VFD is a controlled injected-disturbance mechanism test and every downloaded run is a 16 MiB partial prefix. SustDataED2 transitions are positive controls only, not faults. Independent units are runs or day/appliance clusters; individual rows are never inference units.

## Frozen outcome interpretation
- CoDEx-VFD: 0 of 30 injection-positive partial-run prefixes escalated; the controlled disturbance mechanism was not replicated under the frozen composite threshold.
- SustDataED2: 2 of 18 appliance clusters escalated; this is inconsistent and inconclusive positive-control evidence, not fault evidence.
- PMC-2, PMC-4, and PMC-5 were not separately scored, so no component-specific transfer claim is permitted. PMC-3 remained unavailable.

## Claim boundary
External physical-mechanism replication only; not streetlight field accuracy, municipal performance, fault recall, false-positive rate, asset condition, or actual fault probability.
