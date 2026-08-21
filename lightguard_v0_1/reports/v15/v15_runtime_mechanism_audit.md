# LightGuard v0.15 LUNA C Runtime Mechanism Audit

## Decision

The audited v0.10 runtime activates current-derived mechanisms and the H1
decision gate. It does not activate municipal rated load, policy, solar or
geographic context, or cabinet mapping. Those unavailable fields remain
unavailable; they must not be inferred from the anonymized meter profile or
from a field existing in an earlier schema.

The machine-readable result is
`lightguard_v0_1/data/validation/v15/v15_active_mechanism_registry.json`.

## Runtime Path

```text
run_v10_shadow_replay.py
  -> v10_ami.load_rows / measured_phases
  -> v10_shadow_engine.replay_meter
  -> v10_counterfactual.baseline
  -> v10_counterfactual.activation
  -> v10_counterfactual.feature_case
  -> v09_detector.decide(case, "H1", selected_config)
```

The frozen H1 configuration is read from
`lightguard_v0_1/data/validation/v09/v09_candidate_config.json` and sealed by
`lightguard_v0_1/data/validation/v10/v09_freeze_manifest.json`. No
configuration or threshold was changed.

## Mechanism Status

| component | runtime status | actual input/coverage | decision role |
|---|---|---|---|
| Same-meter 30-day baseline | ACTIVE | 5 meters; 305/455 meter-days evaluable | supplies baseline and separation |
| Daytime active-window gate | ACTIVE | all five target-meter streams | candidate formation |
| Current activation | ACTIVE | 5 meters; B-L-13 single-channel | H1 stage A |
| Duration/persistence | ACTIVE | 7/7 v0.10 evidence cases | stage A and evidence gate |
| Native phase selectivity | ACTIVE, partial | 4/5 meters; 6/7 evidence cases | stage A and evidence gate |
| Transient penalty | ACTIVE | constructable feature cases | stage A/evidence contradiction |
| H1 weighted evidence gate | ACTIVE | current-derived families only | specificity/action decision |
| Shadow warm-up/quality state | ACTIVE | 305/455 meter-days evaluable | pre-decision state gate |
| Solar/geographic context | UNAVAILABLE | 0/5 meters, 0/7 evidence cases | no score contribution |
| Municipal rated load | UNAVAILABLE | 0/5 meters, 0/7 evidence cases | no score contribution |
| Municipal policy | UNAVAILABLE | 0/5 meters, 0/7 evidence cases | no score contribution |
| Cabinet mapping | UNAVAILABLE | 0/5 meters; mapping header-only | no runtime join |
| H3 queue optimizer | INACTIVE | H1 architecture call; 0/5 in path | not invoked |

## Evidence for Unavailable Fields

`feature_case` explicitly emits `None` for `load_mismatch`, `load_evidence`,
`solar_evidence`, and `policy_evidence`. It emits `False` for
`near_solar_boundary` and `normal_partial_policy`; these are defaults in the
constructed case, not observations of municipal conditions. The v0.10
evidence artifact independently records solar, load, and policy unavailable
for all seven candidate cases.

The anonymized AMI manifest exposes interval-end current channels and energy,
but no municipal cabinet identity. The local mapping CSV contains only its
header. The meter profile's `contract_power_kw` is source metadata and is not
passed to the H1 feature constructor; it is not municipal rated-load evidence
for this runtime.

## Active H1 Contribution Boundary

The active score path is limited to current activation and its interaction
with duration, current-derived persistence, native measured-channel
selectivity when available, the frozen weighted evidence gate, and transient
contradiction handling. H1 is not the H2/H3 availability-aware gate: H1 does
not availability-renormalize missing evidence, and H3 queue ordering is not
called. Those are code branches, not active H1 components.

## Claim Boundary

This is a runtime provenance result, not a performance result. It does not
establish streetlight field accuracy, real-background false-positive rate,
fault probability, municipal performance, physical fault cause, or validity
of unavailable solar/load/policy/cabinet fields. Current-derived activation,
persistence, and phase selectivity are anomaly-signals under the frozen
anonymized AMI path only.

## Audit Constraints

- v0.9/v0.10 implementation, frozen configuration, and anonymized AMI
  artifacts were inspected once.
- No result, threshold, code, or experiment was changed or executed.
- Only the registry and the two requested LUNA C documents are deliverables.
