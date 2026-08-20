# Terra Label Methodology: Raw-Data Audit and Proxy-Anomaly Sign Grouping

## Task record and scope

- Date: 2026-08-21
- Role: Agent A, Label Audit Methodologist
- Scope: define conservative label-audit and claim-control rules for v0.11.
- Preservation rule: v0.10 at `d34d8323b3742c9116060d9548bd29c18750cb1f`, H1, raw/Office data, `.env`, `official_docs/`, and `harness_docs/` are out of scope and must not be changed by this work.
- Workflow exception: the repository contract normally requests a harness backlog entry before a file change. The commissioning instruction prohibits any file other than this document, so this in-document task record is the only permitted trace for this documentation-only assignment.

## Purpose and terminology

This document separates three concepts that must not be conflated:

- **Operational event**: a physical lighting or electrical condition at a specific asset and time.
- **Observed signal**: a meter, schedule, weather, maintenance, or derived-data observation that may be consistent with an event.
- **Label**: a recorded target used for analysis or evaluation. A label can be confirmed, weak/silver, or absent; it is not automatically ground truth.

For LightGuard, an AMI pattern such as reduced load during an expected lighting window is an observed signal. It is not proof of partial outage, lamp count, root cause, or safety impact without independent operational evidence. A label derived solely from the same AMI values and rules that the detector evaluates is a proxy label and may be useful for controlled development only.

## Evidence hierarchy

The hierarchy determines permissible language and evaluation use. Higher levels do not erase uncertainty; they make its source explicit.

| Level | Evidence type | Typical LightGuard example | Permitted use | Not permitted |
| --- | --- | --- | --- | --- |
| E0 | Synthetic or scenario-injected signal | Injected 20% load loss or sunrise-overrun into a replay | Detector regression test; sensitivity experiment | Claim about field prevalence, field accuracy, or a real fault |
| E1 | Single proxy observation | AMI residual crosses a rule threshold | Candidate queue; descriptive count marked as proxy | Confirmed-event label; precision/recall claim |
| E2 | Multiple, non-independent proxies | AMI residual plus a schedule deviation computed from the same meter interval | Prioritization signal with lineage | Treating agreement as independent confirmation |
| E3 | Independent operational corroboration | Time-aligned, source-separate work order, operator observation, or independent meter that supports the pattern | Silver label; audited association analysis | Ground-truth or causal claim unless the record explicitly verifies the event |
| E4 | Time-aligned, independently adjudicated field outcome | Field inspection or maintenance closeout that identifies the asset, time, condition, and disposition | Held-out outcome evaluation and carefully scoped performance reporting | Generalizing outside the audited population or period without a transport check |

Independence is about how the evidence is produced, not merely whether it comes from different columns or files. Two fields produced from the same AMI series, the same threshold rule, or the detector output are one evidence family unless a documented process shows otherwise.

## Source-backed method principles

| Topic | Source and evidence | Conservative operational consequence |
| --- | --- | --- |
| Weak and silver labels | Ratner et al. describe weak supervision as heuristic labeling functions with unknown accuracies and correlations, and model source lineage rather than assuming labels are clean. [PVLDB paper](https://www.vldb.org/pvldb/vol11/p269-ratner.pdf) | Preserve each proxy's origin, coverage, abstention, version, and dependency. Do not collapse several correlated heuristics into an asserted truth label. |
| Measurement error and noisy labels | Natarajan et al. study binary classification when observed labels are class-conditionally corrupted, showing that the noise mechanism matters to risk estimation. [NeurIPS 2013](https://papers.nips.cc/paper_files/paper/2013/hash/3871bd64012152bfb53fdf04b401193f-Abstract.html) | Treat missed faults and false proxy positives as potentially asymmetric and context-dependent. Do not assume random, equal-rate label error without an audit that supports it. |
| Label leakage and circular validation | Kaufman et al. define leakage as information about the target that would not legitimately be available at prediction time and recommend explicit learn-predict separation. [ACM TKDD](https://dl.acm.org/doi/10.1145/2382577.2382579) | A detector must never be scored against labels generated from its own outputs, its threshold decision, future data, or features unavailable at alert time. This is the project definition of circular validation. |
| Test-label fallibility | Northcutt et al. report that label errors in commonly used test sets can change benchmark conclusions. [JMLR 2021](https://jmlr.org/papers/v22/20-688.html) | Hold-out status alone is insufficient. Record label provenance and audit disagreement or ambiguity before treating a benchmark as decisive. |
| Traceability and validation governance | NIST AI RMF 1.0 calls for managing AI risk across design, development, use, and evaluation and includes data provenance and measurement among relevant practices. [NIST AI 100-1](https://doi.org/10.6028/NIST.AI.100-1) | Version the label policy, source snapshots, adjudication rules, exclusions, and evaluation split; keep the evidence chain inspectable. |

These sources justify process controls, not an empirical conclusion about LightGuard's current detector. Their reported results, domains, and assumptions must not be transferred as LightGuard performance claims.

## Route selection

Every record set, experiment, and reported metric must declare one route before analysis. If the route changes, create a new label-set version rather than silently promoting existing rows.

### Route A: adjudicated outcome evaluation

Use Route A only when all of the following hold:

- A time-bounded target event is defined before evaluation.
- Each positive and negative outcome is supported by E4 evidence, or the absence of an event is established through an explicit adjudication protocol rather than missing paperwork.
- The adjudicator or source does not use the candidate detector decision, its score, or its post-alert explanation as a determining input.
- The event evidence is time-aligned to the alert window and asset identity is resolved with a documented matching rule.
- Train, threshold-selection, and final-test units are separated by an appropriate leakage boundary: at minimum time; additionally feeder, asset, or episode when their dependence makes a random split misleading.
- Ambiguous, unresolved, duplicate, and out-of-window records have a documented disposition.

Allowed outputs: precision, recall, false-alert rate, missed-event rate, calibration, and confidence intervals, each scoped to the audited population, period, event definition, and evaluation protocol.

### Route B: silver/proxy-label analysis

Use Route B when one or more E1-E3 signals exist but Route A is not satisfied. Route B is the default for AMI-derived anomaly-sign grouping unless independent field outcomes have been linked and audited.

Required conditions:

- The target operational event and each proxy rule are documented separately.
- Each proxy records source system, source timestamp, extraction version or hash, rule version, expected direction, and known dependency with other proxies.
- Proxy-label generation is separated from detector scoring. A label may not directly reuse the detector's final score, alert state, or thresholded decision.
- When a proxy uses AMI, the report explicitly states which AMI intervals are available at alert time. Future-window proxies cannot evaluate a real-time alert.
- A stratified manual audit or Route A bridge sample is planned before interpreting any rate as prevalence or performance.
- Disagreement among proxies is retained as a category; it is not auto-resolved by majority vote unless a pre-registered, evidence-based weighting rule exists.

Allowed outputs: counts of proxy-sign groups, descriptive overlap, data-quality rates, and hypothesis-generating rankings. Use terms such as **proxy anomaly signature**, **candidate**, **silver label**, or **corroborated candidate**, with the evidence level stated.

### Route C: unlabeled/context-only analysis

Use Route C when no defensible event label exists, including when only schedules, weather, geography, asset metadata, or raw AMI readings are available without a valid proxy policy.

Required conditions:

- State that no event-level performance evaluation is possible.
- Limit outputs to coverage, missingness, temporal alignment, distribution shift, data plausibility, and scenario-injection behavior.
- Keep any scenario injection separate from observed raw records and label it synthetic in tables, charts, and filenames.

Allowed outputs: readiness findings, data-quality findings, and synthetic regression-test results. No fault rate, detection rate, or real-world precision/recall may be reported.

## Claim rules

1. Reserve **confirmed fault/event**, **ground truth**, and **detector performance** for Route A with E4 outcomes. If field closeout merely records a visit, call it a work-order corroboration, not confirmation.
2. In Route B, say **consistent with**, **proxy-sign group**, or **candidate for inspection**. Do not infer lamp count, failure mechanism, causality, or public-safety impact from load deviation alone.
3. In Route C, say **data-quality observation** or **synthetic detector response**. Do not use observed raw-data volume as evidence of anomaly prevalence.
4. A rate requires its denominator, inclusion/exclusion rules, unit of analysis, time range, evidence route, and uncertainty method. A zero count is not a zero-risk claim.
5. A model-vs-label comparison is invalid if the label includes the model output, threshold, post-alert feature, future information, or a deterministic transformation of these. Mark the result `CIRCULAR_INVALID`, not `PASS`.
6. Metrics may not be pooled across evidence routes. Report Route A, B, C results in separate tables and charts.
7. Do not claim generalization across municipality, season, feeder, or asset type unless the held-out evaluation explicitly covers that boundary. Otherwise report it as an untested transport assumption.
8. Do not use a proxy rule's own agreement rate as an estimate of operational accuracy unless linked to an independently adjudicated sample and its sampling design is stated.
9. Preserve abstentions and unknowns. Recasting missing AMI, missing work orders, or unmatched asset IDs as negative labels is prohibited without an explicit negative-label protocol.
10. Any result based on raw or Office files must publish only non-sensitive aggregate metadata permitted by project policy; this methodology itself must not copy raw values or identifiers.

## Concrete QA checks

Run these checks before a v0.11 result is labeled valid. A failed hard gate blocks Route A performance reporting; a warning can permit Route B/C descriptive reporting only when disclosed.

| ID | Check | Pass condition | Failure handling |
| --- | --- | --- | --- |
| QA-01 | Label contract | Event definition, unit, onset/window, positive, negative, unknown, and exclusion states are versioned before scoring. | Hard fail: no label-based metric. |
| QA-02 | Provenance ledger | Every label/proxy has source system, extraction timestamp, source snapshot hash or immutable identifier, transformation/rule version, and evidence level. | Hard fail for A/B; Route C only. |
| QA-03 | Prediction-time availability | All predictor and label inputs are tagged with availability time; no final-test feature or label uses information after the alert decision time. | Hard fail: `CIRCULAR_INVALID`. |
| QA-04 | Dependency map | Proxy pairs declare shared raw source, derivation, and operator; dependent proxies cannot be counted as independent corroboration. | Downgrade E2/E3 claim to the lowest supported level. |
| QA-05 | Detector-label separation | Label-generation code and detector-decision code have distinct inputs/versions; no detector score, alert state, or explanation feeds the label. | Hard fail: `CIRCULAR_INVALID`. |
| QA-06 | Time and entity linkage | Asset match, time-zone, interval convention, tolerance window, duplicates, and one-to-many links are logged; unmatched records remain unknown. | Hard fail for A; warning and route downgrade for B. |
| QA-07 | Episode grouping | Contiguous alerts are grouped by a predeclared gap rule before counting; an episode cannot appear in both development and test partitions. | Hard fail for event-level performance. |
| QA-08 | Split integrity | Train, threshold tuning, and final evaluation are mutually exclusive on declared time/asset/feeder/episode boundaries; split manifests are immutable. | Hard fail for performance reporting. |
| QA-09 | Negative-label audit | A sample of negatives is reviewed to distinguish no-event evidence from missing or delayed evidence; sampling frame and reviewer rule are recorded. | No recall, specificity, or false-negative claim. |
| QA-10 | Blind adjudication | For Route A bridge samples, reviewers do not see detector decision/score; a second reviewer or adjudication procedure handles disagreements. | Silver only; no independent Route A metric. |
| QA-11 | Proxy disagreement table | For each proxy-sign group, publish overlap, abstention, contradiction, and missingness counts by relevant stratum. | Restrict result to a single-proxy E1 statement. |
| QA-12 | Sensitivity analysis | Re-run descriptive grouping over plausible schedule tolerance, baseline window, and missingness treatment choices; report material changes. | Mark conclusion threshold-sensitive. |
| QA-13 | Scenario isolation | Injected rows carry a synthetic flag and cannot enter field prevalence or outcome metrics; replay source and injection rule are versioned. | Hard fail: synthetic/observed contamination. |
| QA-14 | Claim lint | Automated or manual review checks every headline/table caption against the claim rules and its route/evidence level. | Remove or relabel unsupported wording. |

## Minimum audit outputs

Before any detector comparison, produce these auditable artifacts without exposing protected raw data:

- A label dictionary with event definition, evidence level, route, source lineage, and allowed claim text.
- A source-dependency graph showing which proxy labels share AMI, schedule, weather, field-work, or detector-derived inputs.
- A timestamp availability matrix distinguishing alert-time inputs from future corroboration.
- A route-specific cohort manifest with inclusion, exclusion, unknown, and duplicate counts.
- A disagreement and missingness report by asset/feeder/time stratum where disclosure is permitted.
- A QA ledger listing `PASS`, `WARN`, `FAIL`, or `CIRCULAR_INVALID`, the owner, the evidence, and the remediation required.

## Decision rule for v0.11

Until an independently adjudicated, time-aligned field-outcome set satisfies Route A, v0.11 should be reported as Route B for proxy anomaly-sign grouping and Route C for coverage/readiness or scenario-only analyses. Any later promotion to Route A must retain the original Route B/C versions and the full provenance trail; it must not overwrite earlier proxy labels as if they had been confirmed outcomes.
