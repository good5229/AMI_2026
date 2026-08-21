# LightGuard v0.15 Independent LUNA Audit

## Final decision

**PASS**

Release-level QA passes after the corrected regeneration. This is a narrow
artifact and claim-boundary PASS for frozen target-domain counterfactual
mechanism analysis. It is not a field validation or production-readiness
decision.

## Audit matrix

| Area | Status | Independent conclusion |
|---|---|---|
| Holdout isolation | PASS | Scalar final metadata gives 71 selected pairs, `v10_overlap_count=0`, `canonical_overlap_count=0`, `selection_uses_outcome=false`, and future leakage 0. |
| Determinism | PASS | Holdout, injection, pair-result, config, predecessor-freeze, selection, source-row, and target-row hashes are recorded. |
| Meter-day assignment | PASS | One operator is assigned per meter-day; pair IDs and operator classes are retained across variants. |
| Freeze integrity | PASS | v0.10-v0.14 predecessor hashes and H1 config/detector hashes are sealed; no retuning is permitted. |
| Runtime mechanism scope | PASS | A1, A2, and A5 target active runtime inputs; A3/A4 are an explicit threshold-only alias; inactive mechanisms are not imputed or ablated. |
| Identity exception | PASS | B4 is the only permitted source/target identity exception and requires identical action and score. |
| Pair statistics | PASS | R is anomaly recovery and B is controlled-benign escalation; both have separate A1-A5 Holm families, exact McNemar cells, and nested cluster bootstrap protocol. |
| Direction and grades | PASS | R necessity uses positive RD; B necessity uses negative RD; positive significant B RD is graded adverse benign escalation. |
| Natural shadow | PASS | Original `control_action` is the source of the truth-free descriptive shadow; forbidden truth/performance columns are absent. |
| Canonical evidence | PASS | Six canonical events are diagnostic references only and retain v0.13/v0.14 negative or inconclusive status. |
| Flutter disclosure | PASS | The static card/docs prohibit field accuracy, real FPR/specificity, fault probability, and general anomaly claims. |
| Preflight | PASS | Supplied final signal is full v0.15 preflight PASS; corrected artifact gates include nonzero valid-pair and B adverse-direction enforcement. |

## Result-specific findings

### P0/P1

No release-blocking finding.

### P2

1. `A2` is correctly non-evaluable for the primary inference because the phase
   gate leaves only 24/36 anomaly pairs and 14/35 benign pairs. This is a
   provenance limitation, not evidence of phase necessity or non-necessity.
2. `B4` contains 11 identity-noop overlaps in the holdout inventory. The
   exception is explicitly allowed and checked for equal actions/scores; it
   must not be generalized to other operators.
3. `v15_active_mechanisms_audit.json` counts canonical-overlap days in the
   complete exclusion inventory, while the selected holdout manifest reports
   zero overlap. Both values are internally interpretable, but future reports
   should keep the audit-population and selected-holdout labels adjacent.

## Frozen statistical reading

- R A1, A3, and A4 show no necessity evidence under the frozen action endpoint.
- R A2 is `NOT_EVALUABLE` because of the phase gate.
- R A5 is `EMPIRICALLY_NECESSARY` within the sealed counterfactual corpus under
  the preregistered paired and clustered criteria.
- B A1, A3, and A4 show no necessity evidence.
- B A2 is `NOT_EVALUABLE` because of the phase gate.
- B A5 is `ADVERSE_CONTROLLED_BENIGN_ESCALATION`; its positive RD is not a
  favorable specificity result and must not be renamed as necessity.
- Z1 remains a secondary comparator and does not determine mechanism grades.

## Predecessor and claim preservation

The final artifacts preserve:

- v0.13 MAD `FROZEN_NEGATIVE_NON_EVALUABLE`;
- v0.14 London `PRIMARY_BLOCKED_PROVENANCE`;
- v0.14 CoDEx-VFD `NOT_REPLICATED`;
- v0.14 SustDataED2 `INCONCLUSIVE`;
- canonical six as `CANONICAL_REFERENCE_NOT_TARGET_TRUTH`;
- no field fault accuracy, real-background FPR/specificity, fault probability,
  or general anomaly performance claim.

## Release recommendation

**PASS for the declared v0.15 target-domain mechanism-ablation scope.** The
release may report the constrained R A5 mechanism grade and the adverse B A5
controlled-benign result exactly as labelled. It must retain all non-evaluable
denominators and must not extend these results to municipal field performance,
fault truth, fault probability, or universal anomaly detection.

QA documents only were written for this task. No code, result artifact,
threshold, configuration, Git state, test, build, or experiment was changed.
