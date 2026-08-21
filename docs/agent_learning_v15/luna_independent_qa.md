# LUNA v0.15 Independent Red-Team QA

## Final verdict

**PASS WITH EXPLICIT NON-EVALUABLE SUBRESULTS**

The release-level v0.15 artifact contract is satisfied after regeneration and
the reported full preflight is `PASS`. No predecessor result, threshold,
configuration, code, or result artifact was modified by this QA. The PASS is
not a field-performance approval: it means the frozen target-domain
counterfactual QA gates and claim boundaries are internally satisfied.

## Scope and evidence reviewed

Reviewed current v0.15 manifests, paired results, ablation configs, runtime
mechanism audit, natural shadow output, case evidence matrix, statistics
protocol, ablation protocol, mechanism grade, final summary, Flutter card, and
Flutter disclosure documentation. The requested preflight PASS was accepted as
the supplied execution evidence; this QA did not rerun tests, builds, Git, or
experiments.

## Gate results

| Gate | Verdict | Evidence / finding |
|---|---|---|
| v0.10 source/target overlap | PASS | Final scalar metadata records `v10_overlap_count=0`; pair records have `source_v10_overlap=false` and `target_v10_overlap=false`. |
| canonical-six buffer overlap | PASS | Holdout metadata records `canonical_overlap_count=0`; pair records have source and target canonical overlap false. |
| predecessor freeze | PASS | `v15_predecessor_freeze.json` is `PRE_OUTCOME_FROZEN`; H1 config/detector hashes and predecessor v0.10-v0.14 artifact hashes are sealed. |
| negative/inconclusive preservation | PASS | Final summary preserves v0.13 `FROZEN_NEGATIVE_NON_EVALUABLE`; v0.14 preserves London blocked provenance, CoDEx `NOT_REPLICATED`, and SustDataED2 `INCONCLUSIVE`. |
| holdout outcome independence | PASS | Holdout metadata says `selection_uses_outcome=false`; selection is sealed before result access. |
| deterministic IDs/hashes | PASS | Pair-result manifest, injection manifest, holdout hash, selection seed, source/target row hashes, and pair IDs are present and linked. |
| one operator per meter-day | PASS | Holdout metadata says `one_operator_per_meter_day=true`; pair contract enforces consistent assignment. |
| A1 active runtime ablation | PASS | A1 removes persistence and is marked active-only with unchanged H1 thresholds. |
| A2 phase-only gate | PASS WITH LIMIT | A2 removes phase evidence only for phase-eligible pairs; R coverage is 24/36 and B coverage is 14/35, correctly classified `NOT_EVALUABLE_INCOMPLETE_COVERAGE`. |
| A3/A4 alias | PASS | A3 explicitly aliases A4 because removing specificity/contradiction leaves the threshold-only branch; the alias reason is recorded. |
| B4 identity exception | PASS | B4 permits source/target equality only when action and score are identical; the identity exception is explicit and controlled. |
| same thresholds | PASS | Ablation config preserves stage-A and specificity thresholds at 0.525 and sets `no_threshold_retune=true`. |
| paired meter-day analysis | PASS | Results contain paired cells, valid/excluded denominators, meter and operator strata, and use meter-day clustering. |
| exact McNemar | PASS | R and B primary families contain A1-A5 with exact p-values and discordant cells; Z1 is secondary unadjusted. |
| nested bootstrap | PASS | Protocol fixes seed `202615` and 10,000 nested meter/meter-day resamples; cluster support is reported per comparison. |
| Holm R/B | PASS | Holm correction is separated by endpoint family; A2 remains reported despite non-evaluable coverage. |
| natural shadow | PASS | Output is derived from original `control_action`, labelled truth-free descriptive, and has no truth/recovery/FPR/accuracy columns. |
| mechanism grading | PASS | Baseline-relative evidence is `EMPIRICALLY_NECESSARY` for R; the positive B RD is correctly graded `ADVERSE_CONTROLLED_BENIGN_ESCALATION`, not necessity. All unsupported/insufficient components remain non-evaluable or null. |
| Flutter disclosure | PASS | Card/docs state freeze, no-truth shadow, diagnostic-only canonical six, and prohibit field accuracy, real FPR/specificity, fault probability, and general anomaly claims. |
| full preflight | PASS | Supplied final signal reports full v0.15 preflight PASS; artifact gate includes the corrected nonzero-valid and adverse-B checks. |

## Findings by severity

### P0 / P1 release blockers

None found.

### P2 observations

- A2 is not inferentially evaluable on the complete assigned endpoint because
  phase provenance gates remove pairs. The artifact correctly retains the
  excluded denominators and reports `NOT_EVALUABLE_INCOMPLETE_COVERAGE`; it must
  not be upgraded to a mechanism grade.
- Eleven B4 identity-noop overlaps are present by design. They are acceptable
  only under the recorded exception requiring equal source/target timestamps,
  equal actions, and equal scores. They must remain separately disclosed in
  future reruns.
- The all-meter-day audit reports canonical overlap rows as excluded inventory,
  while the selected holdout manifest reports zero canonical overlap. These are
  different denominators; the final QA relies on the holdout manifest for the
  release gate and records the distinction to prevent misreading.

## Statistical interpretation

R A5 has positive paired RD and passes the frozen Holm/cluster criteria, so the
reported grade is limited to `EMPIRICALLY_NECESSARY` within this sealed
counterfactual corpus. B A5 has a significant positive RD, which means the
ablation increases controlled-benign escalation under the frozen endpoint; the
correct grade is `ADVERSE_CONTROLLED_BENIGN_ESCALATION`. It is not a claim of
real-background FPR or specificity.

The null, non-evaluable, adverse, and comparator results remain visible. No
result is translated to field accuracy, municipal performance, fault
probability, or general electrical anomaly performance.

## Claim boundary check

The v15 Flutter card and documentation are disclosure-only and preserve the
required prohibitions. Natural shadow is original-control-action descriptive
output without field truth. Canonical six remains diagnostic reference only.

## QA conclusion

`PASS`: the corrected v0.15 release is suitable for its narrow target-domain
mechanism-ablation claim boundary, with A2 explicitly non-evaluable and B A5
explicitly adverse benign escalation. It is not suitable for any field-fault,
real-background specificity/FPR, fault-probability, or general anomaly claim.
