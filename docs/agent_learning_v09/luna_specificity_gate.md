# Agent Learning

## Role

LUNA explainable specificity-gate research for LightGuard v0.9. This note is
research and pre-registration guidance only. It does not inspect v0.9
confirmatory outcomes and does not alter detector, scenario, or validation
data.

## Actual model

LUNA subagent role requested by the v0.9 goal. No model substitution is made in
the design record.

## Sources reviewed

Access date for all sources below: 2026-08-20.

### Required orchestration and repository sources

- [OpenAI: Harness engineering](https://openai.com/index/harness-engineering/)
  - Repository knowledge should be a navigable system of record; executable
    checks and explicit invariants are preferable to undocumented judgment.
- [OpenAI: Introducing the Codex app](https://openai.com/index/introducing-the-codex-app/)
  - Independent agent work should have isolated scopes and explicit review
    boundaries.
- [OpenAI Codex](https://openai.com/codex/)
  - Codex workflows are intended to support long-running, testable engineering
    tasks with human-controlled boundaries.
- [OpenAI Codex AGENTS.md](https://github.com/openai/codex/blob/main/docs/agents_md.md)
  - Repository-local instructions are the routing layer for agent work.
- [OpenAI Codex multi-agent specification](https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/multi_agents_spec.rs)
  - Independent information-seeking tasks can run in parallel only when their
    scopes are self-contained and their write sets do not overlap.

### Task-specific authoritative sources

- [scikit-learn precision-recall curve](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_curve.html)
  - A score threshold changes precision and recall together; the full threshold
    trace must be retained rather than reporting only a selected point.
- [scikit-learn cross-validation guide](https://scikit-learn.org/stable/modules/cross_validation.html)
  - Grouped validation prevents the same group from appearing in training and
    testing; time-correlated data requires care beyond IID splitting.
- [NIST Smart Grid Framework](https://www.nist.gov/ctl/smart-connected-systems-division/smart-grid-group/smart-grid-framework)
  - Interoperability, testing/certification, and a common language are part of
    a trustworthy smart-grid control boundary.
- [Geifman and El-Yaniv, SelectiveNet, PMLR](https://proceedings.mlr.press/v97/geifman19a.html)
  - Selective prediction treats abstention as an explicit operating choice and
    evaluates the risk-coverage trade-off rather than forcing every case into a
    class.
- [US DOE Connected Streetlighting Systems](https://www.energy.gov/cmei/ssl/connected-streetlighting-systems)
  - Controller measurements can improve accountability, but measurement
    accuracy and infrastructure condition are operational risks; a measurement
    anomaly must therefore remain distinguishable from a proven asset fault.
- [US DOE Lighting Controls Solutions](https://www.energy.gov/cmei/ssl/lighting-controls-solutions)
  - Controls should be selected and documented against objectives, system
    capabilities, communications, and field-operation constraints.

## Relevant methodology

### 1. Scope and non-negotiable invariants

The v0.8 C1/C2/C3 results are frozen regression and failure-analysis evidence.
They are not a tuning set for v0.9. No threshold, feature weight, veto, or
queue rule may be selected by reading the v0.8 confirmatory rows or any v0.9
confirmatory result. The v0.9 episode split is fixed before scenario
generation; a region-date episode is the group boundary.

The scoring contract is:

- `weather_weight = 0` in every candidate. KMA/KASI data are context,
  provenance, and stress-stratification metadata only.
- Missing rated load is `unknown`. It is never replaced by a regional average,
  fixture-count product, nominal wattage, or a value learned from another
  region.
- Missing phase evidence is `unknown`, not balanced or healthy.
- An unresolvable conflict produces `abstain` or `data_check_required`, never a
  confident `normal` or `inspect` result.
- Stage B may suppress a Stage A candidate, but may not invent evidence absent
  from the input contract.
- H3 can order work but cannot promote an abstained or rejected case into an
  anomaly decision.

### 2. Candidate set

At most three candidates are pre-registered:

1. **H1: two-stage specificity gate.** Stage A preserves the C1-like sensitive
   candidate generator. Stage B requires independent, explainable evidence and
   applies boundary, policy, and contradiction controls.
2. **H2: availability-aware gate.** H1's evidence is reweighted only over
   observed features, with hard requirements for solar timing and persistence,
   an explicit availability floor, and an abstention route.
3. **H3: queue optimizer.** H1/H2 decision states are unchanged. A bounded
   operational priority score orders `inspect`, `observe`, and `data_check`
   work. It is not allowed to turn a weak or unknown case into `inspect`.

The threshold-only comparator is retained as a comparator, not a candidate: it
is Stage A alone with `score >= t_A` and has no specificity gate.

### 3. Bounded evidence families

Every evidence component is clipped to `[0, 1]`, carries its raw value and
availability flag, and is assigned to exactly one family. The pre-registered
families are:

- **Solar boundary (`E_solar`)**: signed minutes relative to sunrise, sunset,
  civil dawn, and civil dusk. For a confirmed ON interval, post-sunrise tail
  evidence is `clip((minutes_after_sunrise - 15) / 105, 0, 1)` and pre-sunset
  activation evidence is `clip((minutes_to_sunset - 15) / 105, 0, 1)`.
  `E_solar` is the larger of the two relevant sides. The 15-minute grace and
  120-minute transition span are fixed before calibration. A close civil
  twilight boundary is also emitted as a contradiction flag, not hidden in a
  boolean day/night feature.
- **Persistence (`E_persist`)**: `0.6 * clip((continuous_on_minutes - 10) /
  50, 0, 1) + 0.4 * on_fraction_last_60m`. Short transient counts are retained
  as a reason code and cannot be silently treated as persistence.
- **Expected-load residual (`E_load`)**: only when both expected rated load and
  comparable AMI power are present, `clip((expected_kw - observed_kw) /
  max(expected_kw, 0.1), 0, 1)`. This is direction-specific evidence for
  under-consumption during an expected ON interval. If rated load or AMI power
  is missing, the component is unavailable; there is no imputation.
- **Phase selectivity (`E_phase`)**: a fixed categorical mapping from observed
  phase pattern to `1.0` for sustained selective loss, `0.5` for two-phase
  selectivity, and `0.0` for all-phase or no selective evidence. The raw phase
  pattern and duration are logged. Missing phase telemetry is unavailable.
- **Policy incompatibility (`E_policy`)**: `1.0` only when the observed
  pattern is explicitly outside the supplied allowed-partial policy; `0.0`
  when explicitly allowed. Missing policy is unavailable and cannot be treated
  as incompatibility.

The fixed H1 weights are `solar=0.30`, `persistence=0.25`, `load=0.20`,
`phase=0.15`, and `policy=0.10`. These are a bounded pre-registration, not an
invitation to tune against holdout results. A contradiction score is

`C = max(boundary_conflict, transient_conflict, policy_conflict,
load_phase_conflict)`.

Each contradiction component is binary or in `[0, 1]` and must have a logged
reason code. Two evidence values derived from the same raw signal count as one
family for the independent-evidence rule.

### 4. Threshold and action protocol

The only score threshold grid is `{0.525, 0.550, 0.575, 0.600}` for `t_A` and
`t_B`. The grid is enumerated on calibration only. H1's final rule is:

`candidate_A = (stage_a_score >= t_A)`

`specificity_score = weighted_mean(E_available) - 0.20 * C`

`inspect = candidate_A and specificity_score >= t_B and independent_families >= 2
and not explicit_policy_allowed`

The rule emits `normal` only when Stage A is false or a reliable specificity
rejection has no unresolved contradiction. Otherwise it emits `observe`,
`data_check_required`, or `abstain` according to the missing/contradictory
evidence state. The reason codes are deterministic:
`STAGE_A_BELOW_THRESHOLD`, `SOLAR_BOUNDARY`, `INSUFFICIENT_PERSISTENCE`,
`ALLOWED_PARTIAL`, `LOAD_UNAVAILABLE`, `PHASE_UNAVAILABLE`,
`CONTRADICTORY_EVIDENCE`, and `INSUFFICIENT_INDEPENDENT_EVIDENCE`.

### 5. H2 availability-aware rule

Let `a_j` be the availability indicator for family `j` and `w_j` its fixed H1
weight. H2 computes:

`A = sum(w_j * a_j) / sum(w_j)`

`specificity_H2 = sum(w_j * a_j * E_j) / sum(w_j * a_j) - 0.20 * C`

H2 requires `solar` and `persistence` availability, at least two independent
available families, and `A >= 0.60`. Load may be unavailable, including for
Chungju, but the decision must carry `LOAD_UNAVAILABLE` and may not claim a
load-based reason. If solar or persistence is unavailable, or `A < 0.60`, the
result is `abstain`/`data_check_required`; it is not `normal`. The availability
floor is fixed, not tuned on confirmatory data.

### 6. H3 queue optimizer

H3 receives only the output of H1/H2 and never overrides a gate. For eligible
`inspect` or `data_check_required` work, use a bounded score:

`Q = 0.40 * specificity_score + 0.20 * recurrence + 0.15 * asset_criticality
    + 0.15 * age_since_last_review + 0.10 * evidence_completeness`

All terms are clipped to `[0, 1]`, have documented source fields, and are
renormalized only over available queue fields. No missing load term is created.
`abstain` remains outside the inspection queue until a data-quality task is
completed. Ties use stable cabinet ID ordering. Queue efficiency is secondary;
the primary detector gates remain recall, normal FPR, hard-negative FPR, and
worst-cell recall.

## Risks

- A continuous solar margin can still misclassify local control schedules;
  report boundary bins and side of sunrise/sunset separately.
- Persistence and repeated intervals can be correlated; the independent-family
  count prevents double-counting them as separate proof.
- Rated-load mismatch, AMI latency, and phase telemetry loss can create a
  plausible-looking but non-causal residual. The raw values, timestamps, and
  availability mask must be auditable.
- An availability-aware score can improve apparent specificity by abstaining
  too often. Report abstention and coverage beside all performance metrics, and
  enforce the v0.9 abstention limit.
- Queue prioritization can create operational selection bias. It must not be
  used as evidence that the detector found more faults.
- Four threshold values and three architecture labels are still a multiple
  comparison opportunity. Freeze the chosen configuration before any
  confirmatory read and disclose all calibration candidates.
- KMA weather can be a proxy for boundary difficulty. Keep it as a stratified
  context variable and never let it enter the score without a new pre-registered
  experiment.

## Rules adopted for LightGuard

1. Preserve v0.8 exactly as regression/failure-analysis evidence; no v0.8
   confirmatory retuning.
2. Freeze the 48 official 2025 region-season episodes and prove zero episode,
   date, KMA-observation, case, and signal-parameter overlap before scoring.
3. Evaluate the threshold-only comparator plus H1/H2/H3 on calibration only;
   select by FPR and hard-negative FPR gates before recall.
4. Freeze candidate configuration and its SHA-256 before confirmatory execution;
   no post-holdout retuning.
5. Record per-case feature values, clipping, availability, component scores,
   contradiction flags, reason codes, threshold, action, candidate ID, and
   source hashes.
6. Report recall, normal FPR, hard-negative FPR, worst region-season recall,
   AP, abstention, Wilson 95% intervals, and fixed-seed episode-cluster
   bootstrap deltas. An honest `selected_candidate: null` is a valid result.
7. Keep actual AMI replay as regression evidence only, without treating its
   outputs as truth labels or a product-promotion gate.

