# LightGuard v0.15 final summary

## Predecessor freeze
# v0.15 external and target-domain synthesis

- v0.13 MAD is frozen `FROZEN_NEGATIVE_NON_EVALUABLE`.
- v0.14 London remains `PRIMARY_BLOCKED_PROVENANCE`; CoDEx-VFD remains `NOT_REPLICATED`; SustDataED2 remains `INCONCLUSIVE`.
- v0.15 can describe paired, target-domain counterfactual mechanism contribution only. It cannot replace, rehabilitate, or erase the external findings.
- Natural shadow is truth-free target-side action density and disagreement only.

## Active mechanisms
- same-meter 30-day off/on current baseline
- fixed daytime active-window gate
- current-derived activation evidence
- continuous-on duration and current-derived persistence
- native measured-channel selectivity
- short-duration/transient contradiction penalty
- fixed weighted evidence gate
- 30-day warm-up and history-quality state

## Holdout distribution and hash
- Manifest: v15_background_holdout_manifest.json
- SHA-256: f5a2c00f29fffa64e29b69061074771d452054321cd00d0249887ca0d50f75f6
- Frozen metadata: `{"canonical_overlap_count": 0, "future_leakage_count": 0, "holdout_sha256": "7cdb91f34b5772980be21cf79a2a2c68d86bfaa478de043254b8f93351230983", "identity_noop_overlap_count": 11, "one_operator_per_meter_day": true, "seed": "LG-v15-HOLDOUT-20260821", "selected_count": 71, "selection_uses_outcome": false, "source_target_overlap_false_count": 60, "status": "PRE_OUTCOME_FROZEN", "target_count": 71, "v10_overlap_count": 0}`

## Operators
- Operator assignment and class are sealed in `v15_pair_results.csv`; all assigned operators are reported below through paired strata.

## Full versus Z1
| Endpoint | RD Full-Z1 | Status |
|---|---:|---|
| R | 0.02777778 | EVALUABLE |
| B | -0.02857143 | EVALUABLE |

## Ablation
| Endpoint | Variant | RD | Holm p | Status |
|---|---|---:|---:|---|
| R | A1 | 0.00000000 | 1.00000000 | EVALUABLE |
| R | A2 | 0.00000000 | 1.00000000 | NOT_EVALUABLE_INCOMPLETE_COVERAGE |
| R | A3 | 0.00000000 | 1.00000000 | EVALUABLE |
| R | A4 | 0.00000000 | 1.00000000 | EVALUABLE |
| R | A5 | 0.22222222 | 0.03906250 | EVALUABLE |
| B | A1 | 0.00000000 | 1.00000000 | EVALUABLE |
| B | A2 | 0.00000000 | 1.00000000 | NOT_EVALUABLE_INCOMPLETE_COVERAGE |
| B | A3 | 0.00000000 | 1.00000000 | EVALUABLE |
| B | A4 | 0.00000000 | 1.00000000 | EVALUABLE |
| B | A5 | 0.60000000 | 0.00000475 | EVALUABLE |

## Meter stability
- Rows reported: 44

## Operator stability
- Rows reported: 54

## Mechanism grade
# v0.15 target-domain mechanism grades

| Component | Endpoint | RD | Holm p | CI | Necessity grade | Sufficiency |
|---|---|---:|---:|---|---|---|
| persistence | R | 0.00000000 | 1.00000000 | [0.00000000, 0.00000000] | NO_EVIDENCE_OF_NECESSITY | NOT_ASSESSED_BY_SINGLETON_ABLATION |
| phase evidence | R | 0.00000000 | 1.00000000 | [, ] | NOT_EVALUABLE | NOT_ASSESSED_BY_SINGLETON_ABLATION |
| specificity/contradiction gate | R | 0.00000000 | 1.00000000 | [0.00000000, 0.00000000] | NO_EVIDENCE_OF_NECESSITY | NOT_ASSESSED_BY_SINGLETON_ABLATION |
| Stage-A-only structure | R | 0.00000000 | 1.00000000 | [0.00000000, 0.00000000] | NO_EVIDENCE_OF_NECESSITY | NOT_ASSESSED_BY_SINGLETON_ABLATION |
| baseline-relative evidence | R | 0.22222222 | 0.03906250 | [0.06060606, 0.40909091] | EMPIRICALLY_NECESSARY | NOT_ASSESSED_BY_SINGLETON_ABLATION |
| persistence | B | 0.00000000 | 1.00000000 | [0.00000000, 0.00000000] | NO_EVIDENCE_OF_NECESSITY | NOT_ASSESSED_BY_SINGLETON_ABLATION |
| phase evidence | B | 0.00000000 | 1.00000000 | [, ] | NOT_EVALUABLE | NOT_ASSESSED_BY_SINGLETON_ABLATION |
| specificity/contradiction gate | B | 0.00000000 | 1.00000000 | [0.00000000, 0.00000000] | NO_EVIDENCE_OF_NECESSITY | NOT_ASSESSED_BY_SINGLETON_ABLATION |
| Stage-A-only structure | B | 0.00000000 | 1.00000000 | [0.00000000, 0.00000000] | NO_EVIDENCE_OF_NECESSITY | NOT_ASSESSED_BY_SINGLETON_ABLATION |
| baseline-relative evidence | B | 0.60000000 | 0.00000475 | [0.40000000, 0.80645161] | ADVERSE_CONTROLLED_BENIGN_ESCALATION | NOT_ASSESSED_BY_SINGLETON_ABLATION |

EMPIRICALLY_NECESSARY requires Holm, directional clustered CI, and adequate non-contradictory meter/operator strata. These are counterfactual-corpus results only, never field-fault, real-background FPR, accuracy, specificity, or probability claims.

## Natural shadow
- Truth-free target-side density rows: 26

## Canonical six
- Canonical cases remain references, not target truth; see `v15_case_evidence_matrix.csv`.

## Interpretation route
- Use paired counterfactual results for target-domain mechanism contribution, then route candidate actions to human review. Do not infer a confirmed fault or field rate.

## Human review
- Inspect evidence, AMI completeness, source/target lineage, and operational context before maintenance action.

## Claim boundary
- No field-fault accuracy, fault recall, real-background FPR, field specificity, or fault probability claim is permitted.
