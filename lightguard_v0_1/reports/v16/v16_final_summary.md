# LightGuard v0.16 competition-aligned action utility

## Official competition alignment

- Business fit: converts AMI evidence into explicit operator work lanes.
- Development feasibility: reuses frozen H1 and adds a deterministic action policy.
- Idea specificity and completeness: fixes asset eligibility, evidence, lane, and next action contracts.
- Use purpose and tangible effect: reports controlled field-dispatch candidates avoided, never actual savings.
- Generality: covers all official streetlight assets and both official supply-phase classes.

## Frozen v0.15 failure diagnosis

- Data-quality review and field dispatch were conflated in the benign endpoint.
- Frozen H1 emitted normal, observe, and data_check_required but no inspect action on the replay corpus.
- A5 removed the general action-generating evidence rather than a targeted benign guardrail.
- A2 was structurally unavailable on the two official single-phase meters.

## Official asset scope

- Official meters: 129
- Streetlight eligible: 5
- Out of LightGuard scope: 124
- The 124 out-of-scope meters are eligibility controls, not normal labels or FPR evidence.

## Frozen disjoint holdout

- Pairs: 80
- Meters: 5
- v0.10 overlap: 0
- v0.15 replayed pairs: 71
- Pre-outcome B-L-12 extension pairs: 9
- canonical overlap: 0
- Independent validation: false; all runtime-eligible meter-days were already consumed by v0.15.
- Holdout SHA-256: `197d716afda003837d12b2f47f94c7cc7953bfbb88062dc3639906baa09b99a7`

## Exploratory paired service routing

| Endpoint | P1 rate | P0 rate | RD | Status | Prospective target |
|---|---:|---:|---:|---|---|
| R | 0.04878049 | 0.26829268 | -0.21951220 | POST_HOC_DESCRIPTIVE_ONLY | R_RD>=-0.10 |
| B | 0.02564103 | 0.05128205 | -0.02564103 | POST_HOC_DESCRIPTIVE_ONLY | B_RD<=-0.10 |

## Service coverage

- Evaluable official single-phase meters: 2/2
- Evaluable official three-phase meters: 3/3
- Single-phase absence of Ib/Ic is treated as asset topology, not telemetry failure.

## Required prospective confirmatory experiment

- Collect at least one new season of AMI after 2026-06-30 for all five streetlight meters.
- Freeze at least 30 history days, then reserve later meter-days before inspecting outcomes.
- Record operator disposition for data-quality review, remote monitor, and field inspection separately.
- Link field inspection results only after the queue and decision have been frozen.
- Test the prospective targets R RD >= -0.10 and B RD <= -0.10 with meter-day clustered inference.

## Interpretation

The output is a post-hoc work-routing replay: data-quality review, remote monitor, or field-inspection candidate. Human review remains mandatory before maintenance.

## Claim boundary

No independent validation, field-fault accuracy, real-background FPR or specificity, fault probability, confirmed maintenance truth, or actual cost-saving claim is permitted.
