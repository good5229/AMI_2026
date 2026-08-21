# LightGuard v0.16 competition-aligned action utility protocol

## Official objective

The official competition evaluates business fit, development feasibility,
idea creativity and specificity at document review, then development
feasibility, completeness, use purpose, tangible effect, and generality at
the presentation stage. An AMI-backed app artifact is a bonus deliverable,
and a viable idea may proceed to an R&D-linked operating model.

LightGuard v0.16 therefore evaluates an actionable AMI service workflow, not
another detector leaderboard. The service must distinguish data-quality work,
remote monitoring, and a field-inspection candidate so that every alert does
not become a maintenance dispatch.

## Frozen v0.15 failure diagnosis

1. The v0.15 benign endpoint treated every non-normal action, including
   `data_check_required`, as escalation. That conflated telemetry QA with a
   field visit.
2. A5 removed baseline-relative activation globally. It tested an action
   generation switch rather than a targeted benign-suppression mechanism.
3. A2 required three native phases. Two of the five official streetlight
   meters are contractually single-phase, so incomplete phase coverage was a
   structural service limitation rather than random missingness.
4. The five tested B-line meters are all official streetlight assets in the
   supplied 129-meter registry. A/C expansion cannot be represented as more
   streetlight truth; the other 124 meters are scope-gate controls only.

## Frozen questions

- Can a three-lane action policy reduce controlled benign field-dispatch
  candidates without losing more than 10 percentage points of controlled
  anomaly dispatch capture relative to the unguarded H1 action mapping?
- Can all five official streetlight meters, including the two single-phase
  meters, produce an evaluable lane decision?
- Does the metadata eligibility gate admit exactly the five official
  streetlight assets and route the remaining 124 assets out of LightGuard
  scope without calling this an anomaly or false-positive result?
- What truth-free target-side action densities would an operator see before
  any field labels are available?

## Frozen policies

- `P0_COLLAPSED_NON_NORMAL`: reproduce the v0.15 endpoint semantics by mapping
  every non-normal H1 action to one undifferentiated inspection candidate.
- `P1_GUARDED_LANES`: preserve the same H1 threshold. `data_check_required`
  enters the QA lane. `observe` or `inspect` becomes a field candidate only
  when activation and persistence evidence are both at least 0.5. A
  three-phase asset additionally requires phase evidence at least 0.5; a
  contractually single-phase asset uses the two temporal evidence families
  and is not penalized for absent phases that do not exist.

The 0.5 evidence-family confirmation boundary is an exploratory policy rule.
The actual H1 vocabulary audit occurred during v0.16, so no v0.16 result is
confirmatory. No result may retune the H1 score threshold, confirmation
boundary, operator assignment, or replay corpus further.

## Feasibility gate and replay corpus

The supplied April-June data contains 71 streetlight meter-days that pass the
v0.15 zero-missing 30-day history gate, and v0.15 consumed all 71. Those pairs
are reused as `POST_HOC_SERVICE_POLICY_REPLAY`. The fifth official meter,
`B-L-12`, was excluded only because 0.53% of its current intervals are missing.
Before generating v0.16 outcomes, a B-L-12 coverage extension selects complete
target and source segments while allowing sparse gaps elsewhere in the 30-day
history. Its target/source days exclude v0.10 units and canonical buffers.
The combined experiment must not be called fully independent, confirmatory, or
externally validated.

Descriptive paired endpoints compare P1 minus P0:

- `R`: controlled anomaly field-dispatch capture.
- `B`: controlled benign field-dispatch escalation.

Report counts, rates, paired risk difference, and meter/operator/phase strata.
Do not report inferential p-values, confidence intervals, non-inferiority, or
Holm decisions from this post-hoc replay. The prospective follow-up target is
to preserve anomaly dispatch capture within 10 percentage points while
reducing controlled benign dispatch by at least 10 percentage points, but
that target can only be tested on newly collected future-period AMI.

## Claim boundary

This is post-hoc controlled service-routing replay and service-coverage
evidence. It is not independent validation, field-fault accuracy,
real-background FPR or specificity, fault probability, confirmed maintenance
truth, or actual cost saving.
