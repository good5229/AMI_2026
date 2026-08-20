# LightGuard v0.9 Explainable Specificity-Gate Research

Status: pre-registered design proposal for calibration. This document is not a
result report and intentionally does not inspect v0.9 confirmatory outcomes.

## Objective and boundary

The v0.8 candidates preserved weak-signal recall but did not meet the declared
normal and hard-negative FPR gates. v0.9 therefore tests structural specificity
controls, not another unconstrained recall search. v0.8 remains frozen evidence
for regression and failure analysis only. Its confirmatory outcomes must not
choose any v0.9 feature, weight, threshold, veto, or queue rule.

The proposed candidates are deliberately limited to three:

| Candidate | Function | May change anomaly decision? |
|---|---|---|
| H1 | Sensitive Stage A plus explainable specificity Stage B | Yes |
| H2 | H1 with feature availability and explicit abstention | Yes |
| H3 | Bounded inspection/data-quality queue ordering after H1/H2 | No; ordering only |

The threshold-only Stage A comparator is reported but is not a candidate. All
three use `weather_weight = 0`. KMA/KASI context remains provenance,
episode-separation, and stratification information.

## Data contract for the gate

Each case must expose the following versioned fields, with source timestamp and
unit:

| Field family | Required bounded inputs | Missing-value behavior |
|---|---|---|
| Solar | sunrise, sunset, civil dawn/dusk, event timestamp | solar family unavailable; H2 abstains |
| Persistence | continuous ON minutes, ON fraction in trailing 60 minutes, transient count | persistence family unavailable; H2 abstains |
| Load | rated/expected kW, observed AMI kW, comparable interval | no imputation; load family unavailable |
| Phase | phase pattern, duration, phase observation timestamp | phase family unavailable |
| Policy | explicit allowed-partial status and policy version | policy family unavailable |
| Context | region, season, official date/episode, KMA/KASI source hashes | context only, never score input |

No feature may be inferred from region averages, fixture counts, another
cabinet, another episode, or an unavailable rated load. The absence itself is
an audit field.

## Shared bounded feature definitions

All numeric evidence is clipped to `[0, 1]`. Raw and clipped values are stored
so a reviewer can distinguish a real extreme from a capped value.

### Solar boundary evidence

For an ON observation:

```text
post_sunrise_tail = clip((minutes_after_sunrise - 15) / 105, 0, 1)
pre_sunset_activation = clip((minutes_to_sunset - 15) / 105, 0, 1)
E_solar = max(relevant post_sunrise_tail, relevant pre_sunset_activation)
```

The 15-minute grace and 120-minute transition span are pre-registered. A
near-civil-twilight observation generates `SOLAR_BOUNDARY` and can create a
contradiction; it is not collapsed into day/night. Report bins `0-15`, `15-30`,
`30-60`, `60-120`, and `>120` minutes on both sunrise and sunset sides.

### Persistence evidence

```text
run_component = clip((continuous_on_minutes - 10) / 50, 0, 1)
E_persist = 0.6 * run_component + 0.4 * on_fraction_last_60m
```

Transient count is retained as a separate conflict input. A transient cannot be
counted as sustained evidence merely because it has a high instantaneous score.

### Load residual evidence

Only when expected rated load and comparable observed AMI power both exist:

```text
E_load = clip((expected_kw - observed_kw) / max(expected_kw, 0.1), 0, 1)
```

This is under-consumption evidence during an expected ON interval. A missing
load or missing AMI value yields `available=false`, not zero and not an
imputed regional estimate. This rule is especially important for Chungju.

### Phase, policy, and contradiction evidence

`E_phase` is a fixed mapping: sustained selective loss `1.0`, two-phase
selectivity `0.5`, all-phase or no selective evidence `0.0`, and missing phase
telemetry `unknown`. The raw phase class and duration remain visible.

`E_policy = 1.0` only for a pattern explicitly outside a supplied policy.
Explicitly allowed partial operation is a veto for `inspect`; missing policy is
unknown and cannot be treated as incompatible.

The contradiction score is:

```text
C = max(boundary_conflict, transient_conflict, policy_conflict,
        load_phase_conflict)
```

Each term is in `[0, 1]` and emits one or more reason codes. Evidence generated
from the same source family counts once for the independent-evidence rule.

## H1: two-stage specificity gate

### Stage A: sensitive candidate generator

Stage A uses the frozen C1-like weak-signal generator interface. Its output is
not redefined here; its score is `stage_a_score`. The pre-registered threshold
grid is:

```text
t_A in {0.525, 0.550, 0.575, 0.600}
candidate_A = stage_a_score >= t_A
```

The threshold-only comparator reports `candidate_A` directly. It is expected
to reveal the same sensitivity/specificity trade-off that motivated v0.9.

### Stage B: evidence score and hard controls

The fixed evidence weights are:

```text
solar       0.30
persistence 0.25
load        0.20
phase       0.15
policy      0.10
```

For the H1 research score, an unavailable optional feature contributes neither
positive evidence nor a made-up value; the availability-aware interpretation
and abstention policy are formalized in H2. The pre-registered full-data form
is:

```text
S_B = 0.30*E_solar + 0.25*E_persist + 0.20*E_load
     + 0.15*E_phase + 0.10*E_policy - 0.20*C
```

The final threshold grid is:

```text
t_B in {0.525, 0.550, 0.575, 0.600}
```

H1 emits `inspect` only if all conditions hold:

```text
candidate_A
S_B >= t_B
at least two independent evidence families are present
explicit allowed-partial policy is false
no unresolved high contradiction
```

The action state machine is:

- `inspect`: Stage A and Stage B pass with explainable support.
- `normal`: Stage A is below threshold, or a reliable specificity rejection has
  no unresolved contradiction.
- `observe`: Stage A passes but the evidence is near the boundary or below the
  specificity threshold without sufficient basis for a fault claim.
- `data_check_required`: a required data source is missing or stale.
- `abstain`: contradictory or insufficient evidence makes a class unsafe.

`normal` is not permitted when the only reason for rejection is an unresolved
missing or contradictory feature.

## H2: availability-aware specificity gate

Let `a_j` indicate whether family `j` is available and `w_j` be the fixed H1
weight. Define:

```text
A = sum(w_j*a_j) / sum(w_j)
S_H2 = sum(w_j*a_j*E_j) / sum(w_j*a_j) - 0.20*C
```

H2 uses the same `t_A` and `t_B` grid as H1. It additionally requires:

- solar timing available;
- persistence available;
- at least two independent available evidence families;
- `A >= 0.60`;
- no explicit allowed-partial veto or unresolved contradiction.

When these conditions fail, H2 emits `abstain` or `data_check_required` rather
than `normal`. Missing load is allowed to reduce availability and coverage but
never triggers imputation. A successful no-load decision must carry
`LOAD_UNAVAILABLE` and must not cite load residual as supporting evidence.

This is a selective-classification contract: the system is evaluated on both
error rates and the fraction of cases for which it takes a decision. A lower
FPR obtained only by excessive abstention is not a specificity win.

## H3: bounded queue optimizer

H3 does not replace the detector. It receives action states from H1/H2 and
orders eligible operational work. Its terms are:

```text
Q = 0.40*S_gate + 0.20*recurrence + 0.15*asset_criticality
    + 0.15*age_since_last_review + 0.10*evidence_completeness
```

Every term is clipped to `[0, 1]` and has a source field. Queue fields that are
unavailable are omitted and the remaining fixed weights are renormalized;
missing load is not created. Stable cabinet ID breaks ties. `abstain` is not
promoted into `inspect`; it routes to a data-quality queue. H3's secondary
metrics may include top-k inspection precision and time-to-review, but H3 may
not claim detector recall or lower FPR from queue order alone.

## Calibration and promotion protocol

Only the pre-declared calibration episodes may enumerate the threshold grid.
For every comparator and H1/H2/H3 configuration, retain:

- recall, normal FPR, hard-negative FPR, AP, worst region-season recall;
- abstention and decision coverage;
- per-cell and per-episode confusion counts;
- Wilson 95% intervals;
- reason-code counts and missing-feature strata.

Selection is lexicographic: first satisfy normal FPR and hard-negative FPR
`<= 0.05`, then maximize recall subject to worst-cell recall `>= 0.55`, with AP
and abstention as secondary constraints. The declared v0.9 recall target is
`>= 0.70`; if no candidate satisfies the gates, freeze
`selected_candidate: null`.

Before confirmatory execution, freeze the selected candidate ID, feature schema,
weights, thresholds, availability floor, vetoes, reason-code mapping, and
SHA-256. No post-confirmatory retuning is permitted. The confirmation must use
episode-separated dates and KMA observations; a successful score cannot erase
an overlap or missing-data violation.

## Expected failure modes and mitigations

| Failure mode | Observable symptom | Required treatment |
|---|---|---|
| Twilight boundary | high Stage A score near civil dawn/dusk | boundary reason, observe/abstain, report solar bins |
| Pre-sunset normal activation | high activation before sunset | policy/solar gate; no threshold-only promotion |
| Post-sunrise tail latency | short tail with weak persistence | observe unless persistence and independent evidence support it |
| Allowed partial operation | repeated permitted pattern | hard veto to inspect; retain policy version |
| Transient switch/AMI delay | high instantaneous score, short run | transient contradiction; no sustained inference |
| Rated-load mismatch | residual without trustworthy rating | load unavailable/data check; never impute |
| Phase telemetry missing | apparent whole-cabinet anomaly | abstain or data check if phase is needed |
| Correlated evidence | solar and duration inflate one event | independent-family count and source-family tags |
| Weather confounding | error rate changes by weather regime | stratify/report only; weather score remains zero |
| Abstention masking errors | FPR falls as coverage collapses | report abstention and enforce coverage limit |
| Threshold overfit | calibration pass, holdout collapse | pre-freeze config and no retune |
| Queue selection bias | top queue looks better without detector change | report queue metrics separately from detector metrics |

## Auditability checklist

Every decision row must be reproducible from:

1. candidate ID and detector/code hash;
2. episode/date/region/KMA/KASI source identifiers and hashes;
3. input timestamps, timezone, raw values, units, and clipping flags;
4. feature availability mask and missingness reasons;
5. each evidence component, fixed weight, contradiction component, and reason
   code;
6. `t_A`, `t_B`, availability floor, action state, and queue score if present;
7. calibration/confirmatory split manifest hash and generation seed.

The audit must prove `weather_weight=0`, no load imputation, zero overlap across
episode/date/KMA observation/case/signal-parameter identifiers, and no
post-holdout configuration mutation. Actual competition AMI replay remains a
six-case regression comparison, not truth-labeled performance evidence or a
promotion gate.

## Decision

This research supports implementing H1/H2 as bounded, explainable candidates
and H3 as a downstream queue layer. It does not support reactivating weather
scoring, black-box replacement, load imputation, or threshold-only promotion.
The correct outcome of calibration or confirmation remains `selected_candidate:
null` when the declared specificity and coverage gates are not met.

