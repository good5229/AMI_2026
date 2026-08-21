# Blinded Field Validation Protocol

1. Freeze the detector and candidate list before dispatch assignment.
2. Sample candidate and non-candidate cabinets using a predeclared stratified design; do not let inspectors see scores or candidate rank.
3. Record every visit with `field_outcome_schema.json`, including unable-to-adjudicate outcomes and evidence references.
4. Lock outcomes before joining them to detector results through `candidate_event_id`.
5. Report the sampling frame, exclusions, abstentions, unresolved outcomes, and confidence intervals.
6. Estimate field recall only when the sampled frame contains independently inspected candidate and non-candidate units with a defensible denominator.
7. Keep repair savings, dispatch costs, and ROI separate until same-scope official cost denominators exist.
