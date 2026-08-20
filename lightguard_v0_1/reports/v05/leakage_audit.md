# LightGuard v0.5 Leakage Audit

## Audit status and scope

DESIGN AUDIT ONLY - implementation evidence pending.

This document defines acceptance gates for future actual-AMI walk-forward
replay, deterministic robustness testing, and local one-at-a-time sensitivity.
It does not assert that v0.5 replay, stress, or sensitivity execution has
happened. It does not authorize production-code changes or changes to frozen
v0.3/v0.4 artifacts.

Actual AMI contains six known detector candidates, not independently labelled
field faults. Field-performance, municipal-performance, operational-saving,
and economic-impact claims are out of scope without labels, mappings, and
denominators.

## Frozen evidence inspected

| Item | Current evidence | Audit consequence |
|---|---|---|
| v0.3 frozen controlled set | SHA 935bc5ea7d70e878f15113dc08d11dfee7ebcbb350d90d421f46a7704cf27368 | Regression reference only; no mutation. |
| v0.4 calibration | SHA 8fe85425f6ca3b9bc2517a137da96d3edc22bbf387209b53efd933364496032e | Calibration record only; no new tuning. |
| v0.4 confirmatory holdout | SHA 1be716621da5b53bce11a748d9b05e63d4aa329e7d62b8f16e606b2ccff09831 | No selection, retuning, or promotion. |
| v0.4 frozen rule | Threshold 0.55; weather 0.0/context_only | Preserve exactly; sensitivity is descriptive only. |
| Actual-AMI replay anchors | Six anonymized competition candidates; interval 6/6, phase 6/6, peak 2/6 | Known candidates, not field-fault labels. |
| Replay provenance | Six source-row-only windows; no interpolation; context join none | Preserve source separation and source-row provenance. |

## Leakage threat model and controls

| Threat | Failure mode | Required control | Required evidence | Gate |
|---|---|---|---|---|
| Availability-time leakage | Baseline at d includes availability_time >= d. | Filter history strictly before d; record candidate separately. | Cutoff, min/max consumed time, historical-row hash, candidate-row ID. | Fail causal run. |
| Same-time leakage | A row in an equal-availability group becomes another's history. | Treat equal-availability rows as contemporaneous. | Same-time policy and per-origin row list. | Fail affected origin. |
| Timestamp-semantic leakage | Interval-end row is known at its interval start. | Establish timestamp/cadence convention first. | Per-meter timezone, cadence, semantic status. | Exclude unresolved meter/date. |
| Daily-bucket leakage | Later same-day row changes an earlier decision. | Score native-cadence origins; aggregate after scoring. | Decision-time trace inside daily report. | Fail causal run. |
| Global preprocessing | Scaler, imputer, cadence, transition, or baseline fits once on all dates. | Derive every state inside meter-origin history. | Per-origin provenance/state hash. | Fail run. |
| Future duplicate resolution | Conflicting duplicate chosen after later sequence or result review. | Exact rule is frozen/idempotent; conflicts quarantine. | Duplicate disposition before scoring. | Never silently choose value. |
| Event peeking | Canonical intervals tune score, baseline, threshold, merge width, or matching. | Load events after score/episode trace freeze. | Log separating scoring from overlap. | Fail if event enters features. |
| Episode look-ahead | Future noncandidate closes/deletes/backdates earlier episode. | Persist online state and finalization time. | Start, observed end, finalization, row trace. | Label noncausal if post-processed. |
| Cross-meter/context leakage | Another meter, weather, or municipal context forms AMI baseline. | Meter-local default; AMI context join none. | Meter/source IDs; config/output audit. | Fail unapproved join/pooling. |
| Holdout leakage | v0.4 results alter production weights or threshold. | Frozen config plus predeclared descriptive grid only. | Parameter vectors/grid/no replacement. | Fail production change. |
| Stress contamination | Transform or scoring changes after stress outcome. | Fixed family/level/seed; pristine reruns. | Source/input/output hashes and seed ledger. | Report all declared levels. |
| Missingness coercion | Missing channel becomes numeric zero. | Explicit unavailable/degraded state. | Channel-state audit and abstentions. | Fail affected run. |
| Comparison-set drift | Jaccard/ranking uses run-specific duration or selected-only units. | Freeze source-time lattice; compare all common scoreable units. | Lattice, n, ties, unavailable, Top-K boundary. | not_evaluable without lattice. |
| Metric-label leakage | Candidates become faults or support accuracy/recall/precision/FPR/AP/NDCG. | Use coverage, IoU, density, drift, stability only. | Claim-language scan. | Block forbidden language. |
| Stability-threshold leakage | Stable/knife_edge threshold invented after surface known. | Publish full OAT surface; no adjective without pre-execution rule. | Rule or descriptive-only limitation. | Block post-hoc conclusion. |
| Interaction overclaim | OAT claimed to test combined parameter behavior. | State interaction_untested; separate factorial preregistration for interactions. | Scope and one-varied-parameter proof. | Block interaction/optimization claim. |

## Walk-forward acceptance checklist

- [ ] The five B-line meters have source range, timezone, cadence, and
  interval-start/end semantics documented.
- [ ] Every scoreable source observation has decision_time equal to
  availability_time and a separate candidate-row ID.
- [ ] Every historical feature has a consumed-row hash and maximum consumed
  availability_time strictly earlier than decision_time.
- [ ] Equal-availability rows never train or baseline one another.
- [ ] rolling_7d, rolling_14d, rolling_30d, and expanding run independently.
- [ ] Elapsed-day, row-count, and availability requirements freeze before
  detector output is viewed.
- [ ] Warm-up/quality failures are counted as not_evaluable_warmup or
  not_evaluable_quality, never given a fallback.
- [ ] Common-origin comparisons include only units eligible for all variants.
- [ ] A full-sample diagnostic, if created, is noncausal_full_sample
  everywhere and never operating performance.
- [ ] Canonical intervals enter only post-score fixed overlap.
- [ ] Actual-AMI outputs avoid field accuracy/recall/precision/FPR/AP/NDCG.

## Robustness and metric acceptance checklist

- [ ] Every A-F level has frozen family, level, base seed, row-level
  deterministic transform rule, source/input/output hashes, and pristine
  comparator.
- [ ] Stress levels run independently, not cumulatively.
- [ ] Missing channels/conflicting duplicates are unavailable/quarantined,
  never zero or silently chosen.
- [ ] Controlled and actual AMI are separate populations with their own
  metrics and denominators.
- [ ] Coverage reports all-six and scoreable-event denominators; IoU matching
  and ties freeze before execution.
- [ ] Jaccard uses frozen lattice and returns undefined for empty union.
- [ ] Ranking reports common units, ties, n, Top-K boundary, and unavailable.
- [ ] Density shows merged-episode numerator and observed-meter-day denominator
  by meter and aggregate.

## Frozen local sensitivity acceptance checklist

- [ ] Threshold uses only 0.50, 0.525, 0.55, 0.575, 0.60.
- [ ] Each non-zero weight uses only -20%, -10%, frozen, +10%, +20% of that
  one weight.
- [ ] Each run changes exactly one configured parameter. No threshold-plus-
  weight run, second-weight compensation, random search, or joint tuning.
- [ ] All other settings, inputs, origins, transforms, seeds, and weather
  0.0/context_only remain frozen.
- [ ] Any unavoidable internal normalization is documented and does not
  change a second configured parameter.
- [ ] Every grid point, including unfavorable and frozen points, retains
  configuration/source/transform/output hashes and required metrics.
- [ ] No grid point is promoted because it performs better on v0.4 holdout.
- [ ] Without a pre-execution domain rule, stable and knife_edge labels are
  absent; output is descriptive and interaction_untested.

## Claim-language gate

Permitted for actual AMI: past-only replay, canonical-event replay coverage,
event interval overlap, candidate density, candidate-set stability, rank
stability, baseline drift, data availability, phase consistency, unavailable
count, and interaction_untested.

Forbidden for actual AMI: field accuracy, field recall, precision,
false-positive rate, AP, NDCG, true fault, fault detection rate, municipal
AMI performance, dispatch savings, field cost saving, causal field impact,
and parameter interaction effect.

The six canonical items are known detector candidates from anonymized
competition AMI. They are not independently labelled field faults.

## Critical requirements for the implementing/main agent

1. Do not modify a v0.3/v0.4 frozen artifact or promote a sensitivity point.
2. Make availability-time, past-only preprocessing, and origin-level
   source-row provenance executable and auditable.
3. Preserve actual-AMI source separation: context join none and weather
   0.0/context_only.
4. Record every declared stress and OAT outcome, including unavailable and
   unfavorable results.
5. Show the user any required public-data URL before downloading or using a
   new public input.
6. Do not claim field, municipal, operational, causal-impact, or economic
   results without labels, mappings, and official denominator.
