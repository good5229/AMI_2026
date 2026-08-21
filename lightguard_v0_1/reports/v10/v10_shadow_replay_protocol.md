# LightGuard v0.10 Frozen Streaming / Causal Shadow Replay Protocol

## 1. Status, scope, and immutable boundaries

**Status:** pre-execution protocol. This document freezes the v0.10 shadow replay
design only; it is not a result and it authorizes no detector, source, configuration,
or application change.

**Source population:** the untracked workbook fingerprinted by
`lightguard.v10.raw_ami_manifest.1`, restricted to B-L-9, B-L-12, B-L-13,
B-L-14, and B-L-35 from 2026-04-01 through 2026-06-30 in `Asia/Seoul`.
The manifest's source SHA-256, byte count, sheet name, target meters, columns,
row counts, cadence facts, phase availability, missing-channel counts, duplicate
counts, and `24:00` normalization counts are mandatory provenance inputs.

**Frozen detector policy:** invoke the frozen v0.9 H1 decision contract unchanged.
Do not alter any coefficient, threshold, rule order, weather treatment, or feature
policy; do not use an AMI output to select a replacement. Weather remains outside
the AMI score. There is no asset, municipal, KMA, KASI, repair, inspection, or other
external-context join.

**Claim boundary:** the stream has no independent field-outcome label. Output is
restricted to causal score/worklist behavior, data availability, canonical-six
post-score overlap, rank or candidate agreement, and descriptive measurement or
schedule drift. It is not evidence of confirmed physical outcomes, deployment
readiness, municipal behavior, or savings.

## 2. Canonical time, row identity, and chronology

### 2.1 Parse contract

For every source row, retain only the source-derived fields needed for replay:

- `meter_id`, immutable `source_row_id`, source sheet identity, raw timestamp,
  normalized timestamp, and `raw_row_sha256`;
- `availability_time`, which equals the normalized timestamp because the manifest
  establishes source interval-end semantics;
- `interval_start = availability_time - documented_cadence` and
  `interval_end = availability_time`;
- `i1_ampere`, `i2_ampere`, `i3_ampere`, `receiving_active_kwh`, and an explicit
  availability state for each channel; and
- parser version, source-manifest hash, and timezone (`Asia/Seoul`).

A source `24:00` normalizes to next-calendar-day `00:00` before chronology,
deduplication, window membership, or meter-day grouping. Energy is never
reconstructed. An absent phase is not zero; B-L-13 and B-L-35 retain their
one-measured-phase condition.

### 2.2 Deterministic order and same-time batches

Sort by `(availability_time, meter_id, source_row_id)`. All rows with one
`(meter_id, availability_time)` form a contemporaneous batch. Construct the
batch's historical state once from rows with strictly earlier availability time;
score each member against that frozen state; then append the accepted batch
members to future state. A row at time `d` never enters another row's history at
`d`, even when their source-row identifiers differ.

The row's raw channels are permitted inputs to its own frozen H1 invocation at `d`.
They are not historical inputs for that invocation.

### 2.3 Duplicate contract

Before scoring a same-time batch, group rows by
`(meter_id, availability_time, i1, i2, i3, receiving_active_kwh)` after timestamp
normalization.

- An exact group has one representative: the member with the lexicographically
  smallest immutable `source_row_id`. Record every suppressed ID, the group hash,
  and disposition `exact_collapsed`. The representative is the only state update.
- Rows sharing `(meter_id, availability_time)` but differing in any score-relevant
  raw channel are a `conflicting_duplicate` group. Quarantine every member from
  scoring and historical state. Emit one quality record per source row plus one
  batch record; do not choose a value by file order, later observations, or score.
- The raw manifest currently records zero duplicates. These rules are frozen for
  replay reproducibility and stress handling, not as a claim that future input is
  duplicate-free.

## 3. Past-only 30-day decision state

### 3.1 History definition

For an eligible row with decision time `d`, its only operational history is its
meter-local, deduplicated, non-quarantined state:

```text
H(m, d) = { r : r.meter_id = m and d - 30 calendar days <= r.availability_time < d }
```

Calendar arithmetic uses `Asia/Seoul`. The exclusive upper boundary is mandatory.
No full-April-to-June calculation, later same-day row, cross-meter pool, canonical
interval, external join, or future derived statistic may influence `H(m, d)`.

The frozen H1 procedure receives only the current eligible row plus quantities
deterministically derived from `H(m, d)` under its existing policy. It must not be
fit, scaled, imputed, normalized, or scheduled from a larger corpus. State advances
only after the complete contemporaneous batch is decided.

### 3.2 Warm-up and quality states

Each meter begins in `not_evaluable_warmup`. It can leave warm-up only when both
conditions are true at `d`:

- `d - first_eligible_availability_time >= 30 calendar days`; and
- the trailing 30-day expected-slot denominator is 2,880 (30 x 24 x 4) and at
  least 2,736 slots (95%) have all current channels that the manifest declares
  measured for that meter and that the frozen detector requires.

For the second condition, B-L-9, B-L-12, and B-L-14 use their three declared
measured phases; B-L-13 and B-L-35 use their declared single measured phase. An
unmeasured phase does not make a slot deficient, while a missing declared measured
phase does. The implementation must also report the maximum run of unavailable
expected slots; a run exceeding 24 consecutive expected slots (six hours) yields
`not_evaluable_quality`, even if the 95% count condition holds.

State precedence is frozen:

1. `quarantined_conflicting_duplicate`
2. `not_evaluable_warmup`
3. `not_evaluable_quality`
4. `abstained_quality`
5. `evaluable_no_candidate` or `evaluable_candidate`

`abstained_quality` applies after history passes but the current row lacks a frozen
H1-required score channel. No absent channel becomes zero and no fallback baseline
is created. All non-evaluable and abstained origins remain in output denominators.

### 3.3 Origin-level decision-time proof

Every parsed row writes one immutable origin audit record, whether or not it is
evaluable. For evaluable origins, it must include:

- `meter_id`, `source_row_id`, `raw_row_sha256`, raw/normalized timestamp,
  `interval_start`, `decision_time`, cadence, and timestamp semantics;
- `history_start`, exclusive `history_cutoff`, historical row/slot counts,
  qualified-slot count, qualified-slot fraction, maximum unavailable-slot run,
  and per-channel availability counts;
- `history_source_row_ids_sha256`, `history_raw_rows_sha256`,
  `max_history_availability_time`, `state_before_sha256`, and
  `state_after_sha256`;
- duplicate disposition, current-row channel state, state code, frozen detector
  configuration hash, transform hash, and output score/decision fields permitted
  by the frozen detector; and
- `causal_proof = max_history_availability_time < decision_time`.

An empty history has `max_history_availability_time = null` and cannot satisfy the
warm-up gate. A missing proof field, a false proof, a history hash mismatch, or a
row at/after the exclusive cutoff fails the replay rather than being repaired.

## 4. Candidate episodes and immutable meter-day outputs

### 4.1 Episode lifecycle

An evaluable candidate row opens or extends a meter-local provisional episode.
Rows are contiguous only if the next candidate's `interval_start` is no later than
the preceding candidate's `interval_end + documented_cadence`. The episode interval
is from the first candidate's `interval_start` through the last candidate's
`interval_end`.

When a later noncandidate, abstained, non-evaluable, or cadence-discontinuous row
arrives, it records `episode_finalization_time`; it never changes the earlier
candidate score, decision, start, end, source row IDs, or state hash. An episode
that reaches the source boundary without a closing row is `open_at_source_end` and
remains a valid provisional worklist item with an explicit finalization state.

Persist `episode_id`, `candidate_start`, `candidate_end`,
`last_candidate_availability_time`, `episode_finalization_time`, finalization
reason, all candidate source-row IDs hash, and the pre-overlap episode trace hash.

### 4.2 Meter-day ledger

After all origin decisions for a local calendar day are immutable, emit exactly one
`meter_id x local_date` ledger row. A later day cannot mutate it. Required fields:

- provenance: meter, date, timezone, raw/normalized source-row counts, first/last
  availability time, expected slots, and source-row hash;
- state counts: exact-collapsed rows, conflicting-duplicate rows, warm-up origins,
  quality-blocked origins, abstentions, evaluable origins, and candidate origins;
- worklist counts: provisional episodes opened, extended, finalized, and
  `open_at_day_end`; plus episode-duration summaries only for episodes finalized
  that day;
- availability: current-channel availability by declared phase, energy availability,
  qualified-slot fraction, maximum unavailable-slot run, and a boolean
  `usable_meter_day` (at least one evaluable origin);
- denominator fields: `observed_meter_day` (at least one parsed row),
  `usable_meter_day`, and cumulative meter-day totals; and
- `daily_output_sha256`, previous-day ledger hash, and the current state hash.

Daily candidate density is `episodes_opened / usable_meter_days`, reported with
both numerator and denominator by meter and overall. A day with source rows but no
evaluable origin remains observed and has `usable_meter_day = false`; it is never
dropped to improve a descriptive rate.

## 5. Descriptive drift ledger

Drift is a measurement/schedule descriptor, not a detector-selection signal. It
cannot alter H1 state, threshold, ranking, or quality policy. Each value records its
eligible denominator and state code.

For every evaluable origin and meter-day aggregation, calculate only from data
available before the relevant decision time:

| Metric | Past-only definition | Status when unavailable |
|---|---|---|
| Current-level shift | Difference and relative difference between the median total declared-measured current in `H(m,d)` and the immediately preceding nonoverlapping 30-day window `[d-60d, d-30d)`. | `drift_history_insufficient` until both windows pass their own channel-availability accounting. |
| Current spread shift | Difference in IQR and robust CV (`IQR / median`) for the same two windows; robust CV is null when median is nonpositive. | `undefined_nonpositive_denominator` or insufficient. |
| Cadence drift | Trailing-30-day median inter-arrival minutes, count above 15 minutes, maximum gap, and change from the preceding 30-day window. | insufficient. |
| Channel-availability shift | Difference in per-channel usable-slot fraction between trailing and preceding 30-day windows. | insufficient. |
| Transition-time shift | Difference in median observed off-to-on and on-to-off transition minute-of-day, with IQR and contributing-day count, between the same windows. | `transition_not_observed` or insufficient. |
| Worklist-volume shift | Difference in candidate origins and episode openings per usable meter-day between the same windows. | insufficient; descriptive only. |

Monthly April/May/June summaries are post-score aggregations of immutable
meter-day/origin values. They do not recompute an earlier baseline with later
same-month data. Every summary reports observed, usable, warm-up, quality-blocked,
and abstained meter-day counts beside the drift values.

## 6. Canonical-six post-score overlap

The canonical-six artifact is unavailable to parsing, state construction, H1
invocation, episode formation, drift calculation, and daily ledger generation.
Before loading it, write and hash the complete origin audit, candidate episode trace,
and meter-day ledger as `pre_canonical_overlap_sha256`.

Only after that seal may a reporting step load the fixed six canonical intervals.
It must preserve the canonical artifact hash and perform a one-to-one, maximum-IoU
match against finalized or source-end-open episodes. IoU is temporal intersection
duration divided by temporal union duration. Equal-IoU ties resolve by
`candidate_start`, then the candidate source-row-ID hash. Unmatched fixed intervals
and unmatched episodes receive IoU `0`.

Report, without feeding back to any earlier stage:

- fixed intervals covered by a nonempty overlap, out of all six;
- fixed intervals covered out of scoreable fixed intervals, with every exclusion
  reason and denominator; and
- matched interval IDs, candidate IDs, IoU, overlap duration, candidate
  finalization state, and the sealed pre-overlap hash.

This is reproducibility alignment with known detector candidates only. It does not
establish a physical-outcome label.

## 7. Required leakage and integrity gates

The implementation must fail closed on any failed gate and report the failure rather
than omit affected rows.

| Gate | Deterministic assertion |
|---|---|
| Source identity | Workbook fingerprint and source-manifest hash match the frozen manifest; raw source remains unmodified and untracked. |
| Time semantics | All parsed timestamps use `Asia/Seoul`; every `24:00` conversion occurs before ordering; `availability_time` equals normalized interval end. |
| Strict history | For every origin, every history row satisfies `availability_time < decision_time`; `max_history_availability_time` proves it. |
| Same-time isolation | Permuting source-row IDs inside a same-time batch does not change any member's state-before hash, score, or decision. |
| Prefix invariance | Replaying any prefix and then appending later rows leaves all earlier origin audit hashes, decisions, and meter-day hashes unchanged. |
| Window bound | Each consumed row is inside `[d-30 calendar days, d)` and belongs to the same meter; no full-period, cross-meter, or later-day aggregate is consumed. |
| Warm-up and quality | Origins failing elapsed history, 95% qualified slots, or six-hour gap limits receive the frozen state and no fallback baseline. Missing required current channels abstain rather than becoming numeric values. |
| Duplicates | Exact duplicates collapse to the declared representative; conflicting duplicates are quarantined; neither disposition depends on later input or output. |
| Canonical isolation | Candidate/origin/ledger pre-overlap hashes are identical when canonical input is withheld; canonical data is first read only after the seal. |
| Context isolation | Replay inputs contain no asset, municipal, KMA, KASI, repair, inspection, or other external-context fields. |
| Meter-day immutability | A new local day can append a ledger row but cannot alter any prior-day row or hash. |

## 8. Required reproducibility package and prohibited interpretations

Before publishing a replay output, retain the raw manifest, frozen H1 configuration
identifier/hash, parser and transform versions, package/runtime versions, timezone,
source-row count by meter, duplicate dispositions, all origin audits, episode trace,
meter-day ledger, drift ledger, canonical artifact hash, pre/post-overlap hashes, and
every gate result. A rerun may differ only in explicitly excluded run-timestamp
metadata.

Do not report label-dependent classification measures for this AMI stream. Do not
rename canonical overlap as a physical-outcome result, infer missing readings,
combine controlled-scenario and anonymous-AMI denominators, or use shadow replay to
promote, tune, or reject frozen v0.9 H1.
