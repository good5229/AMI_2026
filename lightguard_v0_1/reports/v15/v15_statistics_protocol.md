# LightGuard v0.15 paired-statistics protocol

## Status and claim boundary

**Status:** `PRE_OUTCOME_FROZEN`

This protocol evaluates target-domain counterfactual mechanism contribution on
the new v0.15 holdout only. It does not estimate field-fault accuracy, field
fault recall, fault probability, real-background FPR, or real-world
specificity. v0.10 through v0.14 remain frozen predecessor evidence.

## Analysis population and unit

The primary unit is one eligible, assigned `counterfactual_pair` nested in one
`meter_day`. A pair contains the same source segment, target segment, assigned
operator, and frozen injection parameters evaluated by Full H1 and its paired
comparator. It is included only if both detector runs complete and retain a
valid, same-threshold action mapping.

One meter-day receives one assigned anomaly or benign operator only. Time rows,
score rows, source windows, repeated replays, and multiple evidence records are
not independent observations. Meter is the top-level repeated-measure cluster;
meter-day is nested within meter. The analysis manifest must record all five
meter IDs as anonymized stable IDs, date, operator, pair ID, and variant status
before outcomes are opened.

## Frozen variants and endpoints

Reference is `A0_FULL_H1`, unchanged from the v0.10/v0.9 decision contract.
The primary ablation family contains only runtime-active components:

| ID | Frozen comparison | Intended mechanism |
|---|---|---|
| A1 | Full H1 vs `MINUS_PERSISTENCE` | persistence evidence |
| A2 | Full H1 vs `MINUS_PHASE_EVIDENCE` | phase-selective evidence |
| A3 | Full H1 vs `MINUS_SPECIFICITY_CONTRADICTION_GATE` | controlled benign escalation suppression |
| A4 | Full H1 vs `STAGE_A_ONLY` | later-stage multi-evidence structure |
| A5 | Full H1 vs `MINUS_BASELINE_RELATIVE_EVIDENCE` | meter-relative baseline evidence |

`Z1_ROBUST_Z` is a transparent simple comparator. It is reported separately and
cannot contribute to a component necessity grade. Mechanism-only variants and
the preregistered limited interactions are secondary, descriptive analyses.
No variant may change threshold, weights, stage logic outside its named
knockout, calibration set, pair allocation, or action mapping.

For assigned anomaly pairs, the binary endpoint is
`informative_injection_recovered`: `1` when the frozen action reaches
Inspect-or-Observe, otherwise `0`. For assigned controlled benign pairs, the
binary endpoint is `controlled_benign_escalated`: `1` when the frozen action
reaches Inspect-or-Observe, otherwise `0`. The latter is explicitly a
controlled-benign escalation rate, not FPR or specificity.

Continuous score differences and median paired score uplift are descriptive;
they do not replace action endpoints and cannot rescue an action-scale failure.

## Pair table and estimands

For each endpoint and comparison, construct the paired table with Full H1 as
the first response and comparator as the second:

| | Comparator = 1 | Comparator = 0 |
|---|---:|---:|
| Full H1 = 1 | `n11` | `n10` |
| Full H1 = 0 | `n01` | `n00` |

The paired risk difference is `RD = (n10 - n01) / N`.

- Recovery necessity direction: `RD_recovery > 0` means Full H1 recovers more
  assigned informative injections than its ablation.
- Controlled-benign gate direction: `RD_benign < 0` means Full H1 escalates
  fewer assigned controlled benign perturbations than its ablation.
- Every table includes `N`, all four cells, missing/invalid pair counts, and
  action-scale status. Do not report only favourable discordant cells.

## Exact paired test

For each valid primary comparison, use the two-sided exact McNemar test:

`p_exact = 2 * P[Binomial(n10 + n01, 0.5) <= min(n10, n01)]`, capped at `1`.

The test is calculated before any correction and reported with its discordant
count. It is a conditional paired-direction test, not an independent-sample
classifier comparison. If `n10 + n01 = 0`, record `NO_DISCORDANT_PAIRS` and
set the exact p-value to `1.0`; it cannot support necessity.

Because meter-days are repeated within meters, exact McNemar evidence is not
the only requirement for a confirmatory conclusion. It must agree with the
clustered confidence interval and stratum checks below.

## Clustered confidence intervals and repeated measures

Use a two-stage, meter-nested bootstrap with fixed seed `202615` and `10,000`
replicates:

1. Resample meters with replacement from the frozen eligible-meter list.
2. For each selected meter, resample that meter's eligible meter-days with
   replacement, retaining the matched Full/comparator outcomes as one pair.
3. Recalculate the paired risk difference on the resampled pairs.
4. Report the 2.5th and 97.5th percentiles as the 95% cluster-bootstrap CI.

If fewer than three meters contain an endpoint's valid assigned pairs, or fewer
than 80% of nominal bootstrap replicates are estimable, report
`INSUFFICIENT_CLUSTER_SUPPORT`; retain the point estimate but do not assign
`EMPIRICALLY_NECESSARY`. The limited number of target meters is always stated
with the interval.

## Multiple-comparison families

Family `R`: the five two-sided exact McNemar p-values for recovery, A1 through
A5. Family `B`: the five two-sided exact McNemar p-values for controlled benign
escalation, A1 through A5. Apply Holm's step-down procedure within, never
across, those two frozen families at family-wise alpha `0.05`.

Sort the family p-values in ascending order. For rank `i` of family size `m`,
compare with `0.05 / (m - i + 1)` and stop rejecting at the first failure. Save
both raw and Holm-adjusted p-values. A2, A4, A5 benign results and A3 recovery
results remain reported in their assigned family even if the intended mechanism
is weaker; they cannot be silently omitted. Z1, mechanism-only, interactions,
per-meter, and per-operator results are labelled `SECONDARY_UNADJUSTED` and do
not affect necessity grades.

## Meter and operator stratification

Report each comparison by stable anonymized meter ID and by assigned operator.
For every stratum, include assigned, valid, missing/non-comparable, Full H1
event rate, comparator event rate, paired RD, and discordant counts. These are
effect-stability diagnostics, not extra primary hypothesis tests.

A stratum is `ADEQUATE_FOR_DIRECTION` only with at least five valid assigned
pairs and at least one discordant pair. A primary effect is directionally
contradicted when an adequate meter stratum has an RD opposite to the required
direction. Operator strata establish mechanism relevance only when the operator
was prospectively assigned as relevant to that component.

## Missing and non-comparable handling

Freeze eligibility before outcomes. Every assigned pair receives exactly one of
these statuses:

| Status | Treatment |
|---|---|
| `VALID` | Included in its assigned endpoint analysis |
| `SOURCE_OR_TARGET_MISSING` | Excluded from both detector outcomes; counted by meter/operator |
| `PAIR_CONSTRUCTION_FAILED` | Excluded from both detector outcomes; counted by meter/operator |
| `VARIANT_RUNTIME_UNAVAILABLE` | Non-evaluable for that comparison; never recoded as success/failure |
| `NOT_COMPARABLE_ACTION_SCALE` | Non-evaluable for action endpoint; continuous score shown descriptively only |
| `FULL_H1_RUNTIME_FAILURE` | Release-blocking protocol deviation; no primary inference |

No status may be changed after result review. A comparison is
`NOT_EVALUABLE_INCOMPLETE_COVERAGE` when valid pairs are below 90% of its
pre-outcome eligible assigned pairs, any meter has less than 70% of its
assigned pairs valid, or a runtime/action-scale failure triggers the condition.
The report must display denominators before and after exclusions. There is no
imputation, pair replacement, operator reassignment, or favourable-case subset.

## Effect-size and necessity grades

The following grades are applied per component only after all primary results
are produced. They are target-domain counterfactual mechanism grades, not field
fault or universal-detector grades.

| Grade | Frozen rule |
|---|---|
| `EMPIRICALLY_NECESSARY` | Valid coverage; component-relevant endpoint meets effect threshold; Holm-adjusted exact `p < 0.05`; cluster-bootstrap 95% CI excludes zero in required direction; no adequate meter contradiction; and relevant operator direction is observed |
| `TARGET_DOMAIN_CONTRIBUTORY` | Valid coverage and required-direction effect/CI support, but no Holm support, no relevant operator support, or limited meter stability |
| `NO_EVIDENCE_OF_NECESSITY` | Valid coverage but effect threshold or paired support is not met; report negative/null result unchanged |
| `NOT_EVALUABLE` | Coverage, action comparability, or cluster-support rule fails |

Primary effect thresholds are fixed as follows:

- For A1, A2, A4, and A5 recovery: `RD_recovery >= +0.05`, or `>= +0.10`
  within a prospectively relevant anomaly-operator stratum.
- For A3 controlled benign escalation: `RD_benign <= -0.03`, meaning the
  ablation raises controlled-benign escalation by at least 0.03 versus Full
  H1, with the corresponding relevant benign-operator result in the same
  direction.
- An intended mechanism without an assigned relevant operator is
  `NOT_EVALUABLE` for an operator-specific necessity grade, even if an overall
  effect appears favourable.

`EMPIRICALLY_NECESSARY` requires both practical magnitude and paired
statistical support. A significant but sub-threshold effect is not upgraded;
neither is a threshold-sized effect with a CI crossing zero or a failed Holm
test. All component grades, including unfavourable and non-evaluable results,
must appear in the final table.

## References

- McNemar (1947), https://doi.org/10.1007/BF02295996
- Newcombe (1998), https://doi.org/10.1002/(SICI)1097-0258(19981130)17:22%3C2635::AID-SIM954%3E3.0.CO;2-C
- Holm (1979), https://doi.org/10.2307/4615733
- Hoffmann et al. (2020), https://doi.org/10.18637/jss.v095.i01
- Neuhaus (2001), https://doi.org/10.1146/annurev.publhealth.22.1.115
