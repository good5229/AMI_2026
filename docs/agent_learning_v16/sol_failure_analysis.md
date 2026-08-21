# v0.16 SOL failure analysis and competition alignment

## Official competition purpose

The competition is an AMI-based citizen-facing service idea competition, not a
detector benchmark. Document review evaluates business fit, development
feasibility, creativity, and specificity. Presentation review evaluates
development feasibility, completeness, use purpose, tangible effect, and
generality. An app based on the supplied AMI sample is a bonus artifact, and a
viable idea may proceed to an R&D-linked operating model.

The official registry contains 129 meters across A/B/C. Exactly five are
streetlight tariff and use assets, all on line B. Therefore A/C cannot be
presented as additional streetlight truth. They are useful only for metadata
scope routing or a future separately defined service.

## v0.15 failure causes

- The benign endpoint collapsed `observe` and `data_check_required` into one
  non-normal escalation concept. It did not measure field dispatch.
- A5 removed baseline-relative activation globally, so it suppressed both
  useful and benign actions rather than testing a precise contradiction gate.
- A2 required three phases even though B-L-13 and B-L-35 are officially
  single-phase.
- B-L-12 was excluded by a zero-missing 30-day gate despite only 0.53% current
  missingness. This prevented official 5/5 asset coverage.
- All 71 meter-days that passed the v0.15 zero-missing gate were consumed, so
  no fresh confirmatory streetlight holdout remained.

## v0.16 experiment and result

v0.16 separated data-quality review, remote monitoring, and field-inspection
candidates. It replayed 71 v0.15 pairs post hoc and added nine exploratory
B-L-12 pairs selected from complete segments outside v0.10 dates and canonical
buffers.

- Official asset coverage: 5/5, including 2 single-phase and 3 three-phase.
- Controlled anomaly dispatch RD, guarded minus collapsed: -21.95 percentage
  points.
- Controlled benign dispatch RD: -2.56 percentage points.
- Prospective targets R >= -10 points and B <= -10 points were both missed.

The policy is too restrictive for anomaly routing and provides too little
benign-dispatch reduction. No further threshold tuning is permitted on the
same April-June corpus.

## v0.17 prospective plan requiring new data

1. Collect at least 120 new consecutive days after 2026-06-30 for all five
   official streetlight meters: 30 warm-up days and at least 90 evaluation
   days, targeting 450 meter-days before exclusions.
2. Freeze asset topology, H1 threshold, action vocabulary, three-lane policy,
   missing-data rules, and meter-day split before reviewing outcomes.
3. Reserve the final 60 evaluation days per meter as the untouched test
   period. Earlier evaluation days may be used for policy development only.
4. Record operator disposition separately for data-quality review, remote
   monitor, and field candidate. Never infer a field visit from a non-normal
   detector action.
5. Blind field adjudicators to policy identity. Inspect all field candidates
   and a stratified sample of remote/no-action cases to estimate verification
   bias.
6. Primary controlled targets: anomaly dispatch RD >= -0.10 and benign
   dispatch RD <= -0.10. Primary operational targets with field labels must be
   frozen only after label definitions and sampling weights are approved.
7. Report meter-day clustered intervals, per-meter and phase-class stability,
   missingness, abstention, queue size, median triage time, and label coverage.
8. Stop without promotion if any official meter is non-evaluable, field labels
   are unavailable, the recovery non-inferiority target fails, or benign
   dispatch reduction fails.

## Claim boundary

v0.16 is exploratory service-routing replay. It is not independent validation,
field-fault accuracy, real-background FPR or specificity, fault probability,
confirmed maintenance truth, or actual savings.
