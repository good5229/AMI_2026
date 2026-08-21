# LightGuard v0.5 Experiment Protocol: Causal Actual-AMI Replay

## Status, scope, and claim boundary

This is a pre-registered design protocol, not an executed result. It does not
modify production scoring, source AMI rows, scripts, or frozen v0.3/v0.4
artifacts. A future implementation must create its evidence manifest before
reporting any result.

Actual AMI means only anonymized competition data. It must not be joined to
Busan/Suyeong assets, municipal mappings, weather, repair records, or other
external context. The six canonical replay intervals are known detector
candidates, not ground-truth field faults.

The required population is five B-line lighting meters: B-L-9, B-L-12,
B-L-13, B-L-14, and B-L-35, from 2026-04-01 through 2026-06-30. Record
meter/date eligibility, timezone, cadence, and timestamp convention from the
source before execution. An unresolved meter/date is excluded from causal
claims and reported as unresolved, not silently dropped.

## Frozen references

- v0.3 regression-only SHA:
  935bc5ea7d70e878f15113dc08d11dfee7ebcbb350d90d421f46a7704cf27368
- v0.4 calibration SHA:
  8fe85425f6ca3b9bc2517a137da96d3edc22bbf387209b53efd933364496032e
- v0.4 confirmatory-holdout SHA:
  1be716621da5b53bce11a748d9b05e63d4aa329e7d62b8f16e606b2ccff09831
- frozen configuration:
  activation=0.6, duration=0.25, load=0.25, phase=0.2,
  policy_penalty=0.2, solar_penalty=0.2, transient_penalty=0.2,
  threshold=0.55, weather=0.0.

No v0.5 work may mutate these assets, select a replacement from the v0.4
confirmatory holdout, or reactivate weather scoring. Weather remains
0.0/context_only in every replay, stress, and sensitivity run.

## Causal time and availability contract

1. Parse every immutable source row into meter_id, source_row_id, raw
   timestamp, timezone, documented cadence, channel values, and
   availability_time.
2. Establish whether the source timestamp denotes an interval start or end
   before scoring. For interval-end data, availability_time is the stated
   end. For interval-start data, it is the end implied by documented cadence.
   If this cannot be established, do not score that meter/date causally.
3. A decision origin d is the availability_time of a scoreable source
   observation. The observation's own raw channels may be scored at d. Every
   baseline, imputer, scaler, cadence estimate, duplicate rule, transition
   estimate, and threshold-derived historical feature may consume only rows
   with availability_time strictly less than d.
4. Equal-availability rows are contemporaneous. They may be scored
   independently or as a declared same-time batch, but none may enter another
   same-time row's history.
5. A local-calendar-day report aggregates decisions after scoring. It must not
   allow a later same-day row to alter an earlier decision.
6. Meter-local history is the default. Cross-meter pooling, a full-period
   daylight/on schedule, event-derived alignment, or external context is
   prohibited unless separately proven available before d. Actual-AMI context
   join remains none.

### Past-only preprocessing and episode state

- Derive all baselines and preprocessing inside meter-origin history, never
  over the full three-month corpus.
- Exact duplicates use a predeclared idempotent source-order-independent rule.
  Conflicting duplicates are quarantined and recorded at their availability
  time; no value is selected after viewing later rows or outcomes.
- Missing current, voltage, energy, or phase is unavailable/degraded, never
  numeric zero and never silent imputation.
- A candidate episode can remain provisional until a closing observation is
  available. Persist candidate_start, last_observed_candidate_time,
  episode_finalization_time, and source-row IDs. Do not backdate a decision or
  use a future noncandidate to rewrite an earlier candidate.
- Canonical events are unavailable to scoring. Load them only after candidate
  scores and episode traces are frozen, for fixed overlap calculations.

## Walk-forward design

Process each meter in nondecreasing availability_time and score every eligible
source observation at native cadence. If implementation needs resampling, its
boundaries and timestamp convention must be frozen before execution and must
not depend on candidate or event outcomes.

| Variant | Historical interval at decision d | Minimum elapsed history | Status if insufficient |
|---|---|---|---|
| rolling_7d | [d - 7 calendar days, d) | 7 calendar days | not_evaluable_warmup |
| rolling_14d | [d - 14 calendar days, d) | 14 calendar days | not_evaluable_warmup |
| rolling_30d | [d - 30 calendar days, d) | 30 calendar days | not_evaluable_warmup |
| expanding | [first usable available row for meter, d) | 7 calendar days | not_evaluable_warmup |

Calendar-day arithmetic uses source timezone. Elapsed days are necessary but
not sufficient. Before any detector output is viewed, the manifest also
freezes each meter's minimum historical row count and
historical-availability requirement. An origin failing either is
not_evaluable_warmup or not_evaluable_quality; it never receives a fallback
baseline.

Run all variants independently. Common-origin comparisons include only
decision units eligible for all four variants after the same availability and
quality gates. With complete 2026-04-01 history this cannot precede
2026-05-01, but derive the exact per-meter date rather than assume it.

For every meter, decision origin, and variant, preserve an audit row with:

- decision_time and timestamp semantics;
- window_start and exclusive historical cutoff;
- historical row count, availability fraction, and minimum/maximum historical
  availability_time;
- historical source-row hash, separate candidate-row ID, and
  preprocessing/baseline values;
- channel-state availability, candidate score/decision, episode state, and
  finalization time; and
- configuration, source, and transform-manifest hashes.

The maximum consumed historical availability_time must be strictly earlier
than decision_time. Absence of this proof fails the causal run.

## Predeclared comparison units

Candidate-set comparisons must not use a run-specific episode duration or
post-hoc event window. Before execution, freeze a lattice of meter_id plus
15-minute source-time bin. If documented native cadence is not 15 minutes,
freeze another one-cadence source-time bin before execution or report the
cross-run comparison as not_evaluable.

Rank comparisons use all common scoreable decision units from the lattice, not
only units selected as candidates by either run. Report the common-unit
denominator and unavailable counts. Use average ranks for Spearman rho and
tie-aware Kendall tau-b. For Top-K overlap, use frozen secondary key meter_id,
availability_time, source_row_id only for deterministic membership; report
the score-tie count at K and raw score cutoff too.

## Metrics and permitted wording

Actual AMI has no repair outcome or independently verified fault label.
Actual-AMI reports may not use field accuracy, field recall, precision,
false-positive rate, AP, NDCG, true fault, fault detection rate, municipal
AMI performance, dispatch saving, or field cost saving. Such label-dependent
metrics remain allowed only for labelled controlled validation.

| Metric | Definition | Interpretation limit |
|---|---|---|
| Canonical-event replay coverage | Report covered fixed intervals out of all six and out of scoreable fixed intervals. Coverage needs a post-score past-only episode overlap. | Reproducibility of known candidates, not recall. |
| Event interval IoU | Duration(intersection) / duration(union), one-to-one highest-IoU matching. Equal-IoU ties break by candidate_start then source-row ID; unmatched is 0. | Alignment, not fault correctness. |
| Candidate count and density | Count merged episodes. Density is count / observed meter-days, where a meter-day has at least one usable source row. Report numerator and denominator by meter and total. | Worklist volume, not a fault rate. |
| Candidate distribution | Median, IQR, p10/p90 for duration, activation, score; phase patterns; unavailable/abstained counts. | Behavior description only. |
| Baseline CV and drift | CV is historical SD / historical mean for one named positive baseline. Zero or predeclared-epsilon denominator is undefined. Drift is adjacent-month raw/percent change with coverage. | Measurement variation, not accuracy. |
| Transition-time drift | Median and IQR change in meter-local transition time across April, May, June with coverage. | Schedule/measurement drift only. |
| Candidate Jaccard | Lattice-intersection size / lattice-union size. Empty union is undefined, not 1.0. | Candidate-set stability. |
| Rank stability | Spearman rho, Kendall tau-b, Top-K overlap on common scoreable lattice, with ties, n, unavailable counts, and Top-K boundary data. | Ordering stability, not label quality. |

For labelled controlled validation, separately report established anomaly
recall, normal false-positive rate, P@10, P@20, candidate count, and AP/NDCG
only if true labels support them. Do not mix controlled and actual-AMI
denominators or use controlled labels to label actual AMI.

## Noncausal full-sample comparator

One diagnostic comparator may recreate the full-sample baseline only when it
uses the entire three-month meter history. Label it noncausal_full_sample in
every table, chart, filename, and narrative. It is not operational and cannot
promote a configuration.

Compare it with each past-only variant using the same lattice: candidate
Jaccard, canonical coverage, interval IoU, rank agreement, activation and
baseline differences, and unavailable counts. Future-row use is the reason
for the noncausal label, not a reason to hide it.

## Deterministic data-quality stress suite

Verify source immutability before every derived input. Each run records
source-row IDs, transform family, level, base seed, and deterministic hash of
seed, level, and source-row ID. Use base seeds 550501 through 550506 for
families A through F. Never seed by an event or tune a transform after its
output is seen.

| Stress | Levels | Frozen transform rule | Required reporting |
|---|---|---|---|
| A. Random missingness | 5%, 10%, 20% | Deterministically mask eligible observations, preserve timestamps, mark channels unavailable. | Controlled metrics; actual coverage, Jaccard, count/density change, unavailable count. |
| B. Contiguous gaps | 30, 60, 120 minutes | Mask deterministic native-cadence blocks; record fixed-interval overlap after scoring. | A outputs plus gap-intersection flag. |
| C. Downsampling | 15 to 30; 15 to 60 minutes | Freeze current summary, interval-energy aggregation, and output timestamp convention. If native cadence differs, use not_applicable. | Resolution, coverage/stability, duration shift, unavailable count. |
| D. Phase dropout | I1, I2, I3 where present | Mask one available phase; missing remains unavailable, never zero/imputed. | Phase consistency, abstentions, candidate changes. |
| E. Duplicate timestamp | Exact; conflicting | Inject source-identifiable derived rows. Exact duplicates use the frozen rule; conflicts are quarantined. | Duplicate disposition, stability, quarantine count. |
| F. Measurement-channel missing | Current, voltage, energy where present | Mask one named channel and require unavailable/degraded detector state. | Channel disposition, output change, unavailable count. |

Run each level independently from the pristine baseline, never cumulatively.
Keep controlled and actual-AMI outputs separate and retain the same
eligibility denominators for a comparison. A stress-induced unavailable origin
remains in its audit denominator; it must not vanish to make a result appear
stable.

## Local one-at-a-time sensitivity audit

The v0.4 configuration is primary. This is local description around it, not a
search, optimization, or production-selection procedure.

- Threshold grid: 0.50, 0.525, 0.55, 0.575, 0.60.
- For each non-zero frozen weight, run -20%, -10%, frozen, +10%, +20% of that
  one weight: activation, duration, load, phase, policy_penalty,
  solar_penalty, transient_penalty.
- In a weight run, every other configuration value, including threshold,
  weather, rule order, normalization behavior, source input, decision
  origins, transform, and seed, stays frozen.
- Do not renormalize remaining weights, compensate a second coefficient, or
  combine threshold and weight changes. If internal normalization is
  unavoidable, record its deterministic formula and prove no second
  configured parameter changed.
- Weather is excluded from perturbation and remains 0.0/context_only.
- Do not randomly search, jointly optimize, or retune on the v0.4
  confirmatory holdout.

For every grid point retain parameter_id, complete frozen and varied vectors,
configuration/source/transform hashes, controlled metrics, actual count and
density, canonical coverage, Jaccard to frozen configuration, rank stability,
unavailable origins, and output hash. Publish the complete surface, including
the frozen and unfavorable points.

This design estimates local main-effect response only. It does not test
interactions or response surfaces. No domain-justified numeric criterion for
stable or knife_edge is frozen here, so neither adjective is authorized after
execution. Report descriptive distributions and interaction_untested instead.
A future interaction study requires separately pre-registered factorial work;
it cannot be retrofitted from OAT outputs.

## Required reproducibility evidence

The implementing agent must produce a v0.5 manifest with source,
frozen-reference, transform-input, configuration, and output hashes;
source-row counts; meter/date eligibility; timezone/cadence/timestamp
semantics; pre-scoring history requirements; commands/package versions/revision
and seeds; full parameter grid; origin audit rows; common-origin denominators;
unavailable counts; and deterministic rerun rules.

Any public-data URL needed for an uncommitted input must be shown to the user
before downloading or relying on it. A deterministic rerun may differ only in
explicitly excluded run-timestamp fields.
