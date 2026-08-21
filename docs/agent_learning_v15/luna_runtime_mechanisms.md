# LUNA C v0.15 Runtime Mechanism Audit

## Role

LUNA C runtime auditor. This audit determines which v0.9/v0.10 H1 mechanisms
are actually activated by the executable AMI path. It is an implementation
and provenance audit only: no result, threshold, source code, or experiment
was changed or executed.

## Actual Model

The audited path is:

`run_v10_shadow_replay.py -> v10_shadow_engine.replay_meter ->
v10_counterfactual.baseline/activation/feature_case ->
v09_detector.decide(case, "H1", selected_config)`.

The frozen model is H1 from `v09_candidate_config.json` and
`v09_freeze_manifest.json`. The selected configuration is consumed as H1,
with weather scoring disabled, no load imputation, and no v0.10 Track-A
retuning.

## Sources Reviewed

1. [Python import system](https://docs.python.org/3.12/reference/import.html):
   import/call edges define the executable runtime boundary.
2. [Python JSON module](https://docs.python.org/3.12/library/json.html):
   frozen JSON configuration is serialized input; undocumented defaults are
   not assumed.
3. [Python hashlib module](https://docs.python.org/3/library/hashlib.html):
   SHA-256 manifest values identify frozen artifacts, not performance.
4. [NIST CUSUM guidance](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm):
   a change signal is not a physical cause or fault label.

## Repository Files Audited Once

- `scripts/v09_detector.py`
- `scripts/v10_ami.py`
- `scripts/v10_counterfactual.py`
- `scripts/v10_shadow_engine.py`
- `scripts/run_v10_shadow_replay.py`
- `lightguard_v0_1/data/validation/v09/v09_candidate_config.json`
- `lightguard_v0_1/data/validation/v10/v09_freeze_manifest.json`
- `lightguard_v0_1/data/validation/v10/v10_raw_ami_manifest.json`
- `lightguard_v0_1/data/validation/v10/v10_injection_manifest.json`
- `lightguard_v0_1/data/validation/v10/v10_background_pool_manifest.json`
- `lightguard_v0_1/reports/v10/v10_evidence_availability.csv`
- `lightguard_v0_1/reports/v10/v10_shadow_replay_summary.md`
- `lightguard_v0_1/reports/v10/v10_counterfactual_protocol.md`
- `lightguard_v0_1/reports/v10/v10_final_summary.md`
- `lightguard_v0_1/data/ami_cabinet_mappings.csv`
- `lightguard_v0_1/data/ami_meter_profiles.csv`
- `lightguard_app/assets/data/ami_event_windows/replay_manifest.json`
- the six anonymized AMI event-window CSV headers and representative rows

## Runtime Findings

`replay_meter` computes same-meter history, derives off/on current baselines,
and calls `feature_case` for a daytime active row. `feature_case` supplies
current-derived persistence and native measured-phase evidence. It explicitly
supplies `None` for `solar_evidence`, `load_evidence`, and `policy_evidence`,
and sets `near_solar_boundary` and `normal_partial_policy` to false. The H1
call therefore cannot infer those unavailable domains.

The anonymized AMI manifest identifies five target meters, interval-end
timestamps, current channels `i1/i2/i3`, and no municipal/cabinet join. Four
meters have three measured current channels and B-L-13 has only `i1`. The v0.10
evidence artifact records persistence available in 7/7 candidate cases, phase
evidence in 6/7, and solar/load/policy unavailable in 0/7. The mapping table is
header-only, so cabinet mapping is not runtime input. Profile contract-power
values are not passed into `feature_case` or `decide`; they are not municipal
rated-load evidence.

## Adopted Rules

- `runtime_available: true` requires that the audited execution path supplies
  the value to `feature_case`/`decide`, or applies it as an active
  pre-decision rule in `replay_meter`.
- A schema/report/profile field not joined to the H1 case remains unavailable.
- Missing solar, geographic, rated-load, policy, and cabinet mapping data are
  never replaced by proxies or inferred municipal values.
- Current-derived activation and persistence are signals only; they do not
  establish fault truth, field accuracy, or fault probability.
- `ablatable: true` means the supplied input/rule can be removed without
  changing the frozen threshold/config. No ablation was performed here.
- H3 queue ordering and H2/H3 availability-aware behavior are not active in
  the H1 call, despite their code existing in `v09_detector.py`.

## Summary

Active components are the meter-relative baseline, daytime active window,
current activation, duration/persistence, native phase selectivity when
available, transient penalty, H1 evidence gate, and shadow quality/warm-up
state. Unavailable or inactive components are solar/geographic context,
municipal rated load, policy, cabinet mapping, H3 queue ordering, and H2/H3
availability-aware normalization.
