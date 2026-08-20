# LightGuard v0.10 Frozen Real-Background Counterfactual Protocol

## Status and pre-score resolution

`FROZEN_BEFORE_H1_OUTCOME`, protocol version `2`.

The TERRA draft proposed scaled perturbations and an always-blocked gate. The
physical review subsequently rejected unrestricted scaling. Before any H1
transport score was run, the orchestrator replaced that draft with this
constrained executable protocol. It measures frozen-H1 behavior under stipulated
current-only counterfactuals, not field accuracy, recall, specificity, or FPR.
The unmodified background is never labelled normal, safe, or fault-free.

## Frozen source and feature boundary

- Ignored B-feeder workbook SHA-256: `c18b49022d1c7dee2117a8d65a07d71351fb1aea8538751b7032867e4081b7d0`.
- Meters: `B-L-9`, `B-L-12`, `B-L-13`, `B-L-14`, `B-L-35`.
- Period: 2026-04-01 through 2026-06-30, interval-end, Asia/Seoul.
- Only measured current may change in-memory. Energy, voltage, timestamps, row
  order, and missingness are immutable and raw current values are not committed.
- No municipal asset, rated load, KMA, KASI, weather, maintenance, or repair join.
- H1 stays at stage-A `0.525`, specificity `0.525`, weather `0`, no imputation.
- Solar, load, and policy evidence are unavailable. Persistence is current-derived;
  phase evidence exists only for measured native phases.

## Background pool freeze

The primary unit is one `(meter_id, local_date)` on the 96-slot 15-minute grid.
The first pre-H1 pool attempt showed that requiring all 96 slots left only 29
B-L-12 days, below the 40-unit balance target. Before injection or H1 scoring,
the source-quality rule was therefore frozen at at least 90 usable slots
(93.75%). Missing slots remain missing and are never inserted. Eligibility is
source-only:

1. Date is 2026-05-01 through 2026-06-30, allowing 30 days of prior history.
2. Present timestamps are unique and members of the canonical 96-slot grid.
3. At least 90 slots have finite, non-negative values for every measured phase.
   Each assigned graft source and target interval must itself be complete;
   otherwise the pair is `not_constructable`.
4. The unit does not intersect a canonical-six same-meter buffer from four hours
   before event start through four hours after event end.
5. H1 score/action/candidate and canonical outcome are forbidden inputs.

Within each meter sort eligible units by
`SHA256("LG-v10-POOL-20260820|meter|date")`, then freeze the first 40. A shortfall
fails the gate; no cross-meter replacement is allowed. The pool is exactly 200
balanced meter-days. B-L-12 missingness is not filled: qualifying days preserve
unavailable slots and no injected interval may cross them.

## Past-only source catalog and graft rule

For target day `d`, source rows and baseline quantities come from the same meter
in `[d-30 days,d)`. OFF and ON references are meter-local medians at 10:00-15:00
and 22:00-04:00. Source selection uses timestamp, completeness, amplitude band,
duration, then `SHA256("LG-v10-SOURCE-20260820|operator|meter|date|source_start")`.
H1 outcome is unavailable to selection.

The first pre-H1 constructability pass found that requiring every source interval
to remain inside one amplitude band rejected 103 of 200 assigned units. Before H1
scoring, source selection was frozen instead on the mean activation of each
complete real segment: choose the segment closest to the operator target within
the broad source-only bounds full/post/phase `[0.50,1.50]`, partial `[0.05,0.85]`,
weak `[0.05,0.75]`, and benign `[0.00,0.50]`. Values are still copied without
scaling and realized activation is reported; no unit or operator is reassigned.

All grafts use identity residual scale `1.0`: for source `s`, source OFF `b`, and
target `x`, write `x + max(0,s-b)` on approved measured phases. No phase is
inferred and energy is unchanged. An unavailable required source segment yields
`not_constructable`; the unit is not replaced or reassigned.

## Deterministic operator assignment

Three-phase meters cycle through six codes below; one-phase meters cycle through
the five excluding `phase_selective`. Each background receives one variant.

| code | class | frozen current-only transform |
|---|---|---|
| `deep_day_full` | anomaly | 8 intervals from 10:00; graft an 8-interval naturally ON residual to every measured phase. |
| `daytime_partial` | anomaly | 8 intervals from 12:00; graft a naturally observed 0.20-0.60 activation residual without scaling. |
| `post_switch_persistence` | anomaly | 6 intervals after the target's observed ON-to-OFF transition; continue its preceding real ON tail. This is observed schedule context, not sunrise. |
| `phase_selective` | anomaly | 3P only; 8 intervals from 10:00; graft one deterministic measured phase and retain the others. |
| `weak_long_duration` | anomaly | 16 intervals from 10:00; graft a naturally observed 0.20-0.45 residual segment. |
| `benign_transition` | controlled benign | at most 2 intervals adjacent to an observed transition; graft a naturally observed 0.05-0.15 residual. This is stipulated benign, not actual normal truth. |

Phase selection is
`SHA256("LG-v10-PHASE-20260820|meter|date") mod measured_phase_count`.

## Provenance and committed representation

Every pair records injection ID, operator/class, target meter/timestamps/phases,
source meter/timestamps/row-ID hash, input/output hashes, `scale=1.0`, copied-cell
and skipped-missing counts, unchanged-energy identity, and raw/pool/H1/protocol
hashes. The committed pair table contains only features, decisions, scores, reason
codes, intervals, and hashes; never raw source current or energy values.

## Frozen H1 mapping

Activation/duration use a past-only meter-local OFF/ON separation. Persistence
uses the v0.9 duration equation. Phase selectivity uses native phases only.
`solar_evidence`, `load_evidence`, and `policy_evidence` are null. Solar/policy
flags are false only because those rules are not applied, with explicit unavailable
reason codes. Original and injected copies are independently scored with frozen H1.
Severity is `normal < observe/data_check_required < inspect`; abstain is separate.

## Metrics and transport gate

An anomaly pair is informative when original action is below inspect. Recovery is
an injected severity increase: normal to observe/inspect, or observe to inspect.
Original inspect to inspect is non-informative, never a true positive.

Report IRR, inspect-or-observe and inspect-only recovery, score-uplift median/IQR/
positive rate, interval IoU, worst-meter/operator IRR, and 3P-only phase recovery.
For benign controls report paired Benign Escalation and Benign Inspect rates, never
real-background FPR or specificity.

The Track-A semi-synthetic gate is frozen before outcomes:

- informative-pair IRR `>= 0.80`;
- worst-meter IRR `>= 0.60`;
- benign escalation `<= 0.05`;
- median injected score uplift `> 0`.

PASS allows only “real-background counterfactual transport validation passed.”
FAIL triggers optional R1 design; PASS prohibits R1.

## Dependence, uncertainty, and integrity

Use 2,000 fixed-seed (`20261020`) meter-day cluster bootstrap replicates, keeping
each pair together; Wilson intervals are secondary and leave-one-meter-out is
required. Never bootstrap 15-minute rows.

Execution fails if a v0.9/raw hash changes, selection depends on H1, energy or
missingness changes, a background has multiple primary variants, a 1P meter gets
phase-selective injection, provenance is incomplete, or a gate changes after
outcomes.
