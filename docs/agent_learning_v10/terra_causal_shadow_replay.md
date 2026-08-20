# TERRA v0.10 Learning Note: Streaming Causal Shadow Replay

## Run identity and scope

- Requested model label: `terra`.
- Actual active model: `GPT-5` (Codex runtime identity supplied to this agent).
- Access date: 2026-08-20 (Asia/Seoul).
- Task: protocol-only audit for a chronological, past-only 30-day shadow replay.
- Inspected repository inputs: the v0.10 raw AMI manifest, v0.5 causal
  protocol/leakage materials and causal implementation, and frozen v0.9 claim
  contracts only.

The raw workbook is untracked and no source rows are copied into the manifest.
The eligible population is B-L-9, B-L-12, B-L-13, B-L-14, and B-L-35 for
2026-04-01 through 2026-06-30, in `Asia/Seoul`. Source timestamps are
interval-end timestamps; a source `24:00` is normalized to the following
midnight. The manifest records a 15-minute median cadence, no existing duplicate
timestamps, and one- or three-phase current availability by meter. It also records
substantial energy absence for B-L-13 and B-L-35, so the replay must preserve
channel availability rather than create values.

## What the required sources contribute

| Source | Method takeaway carried into v0.10 |
|---|---|
| [scikit-multiflow `EvaluatePrequential`](https://scikit-multiflow.readthedocs.io/en/stable/api/generated/skmultiflow.evaluation.EvaluatePrequential.html) | A stream observation is evaluated in arrival order before it becomes part of history. v0.10 applies the ordering rule to detector state, without importing supervised measures into the unlabeled AMI stream. |
| [Montiel et al., 2018, *Scikit-Multiflow*](https://jmlr.csail.mit.edu/papers/v19/18-251.html) | Streaming frameworks need explicit evaluator semantics. v0.10 therefore records timestamp meaning, availability time, state version, and audit hashes per origin. |
| [Bifet et al., 2010, *MOA*](https://www.jmlr.org/papers/v11/bifet10a.html) | Large evolving streams require online-oriented evaluation and reproducible experiment machinery. v0.10 freezes ordering, quality gates, and output denominators ahead of replay. |
| [NIST: Type A evaluations of time-dependent effects](https://www.itl.nist.gov/div898/handbook/mpc/section5/mpc5311.htm) | Short-term, day-to-day, and longer-term variation should be distinguished. v0.10 reports separate cadence, channel-availability, level, and transition-time drift descriptors. |
| [NIST: Recommended Calibration Interval](https://www.nist.gov/calibrations/recommended-calibration-interval) | Stability assessment should use documented, time-indexed evidence rather than a universal interval. v0.10 retains rolling history quality and coverage alongside every drift value. |
| [Eichstadt et al., 2016, NIST: time-dependent measurements](https://www.nist.gov/publications/challenges-uncertainty-evaluation-time-dependent-measurements) | Dynamic measurement treatment needs stated assumptions and uncertainty-aware reporting. v0.10 does not reconstruct energy, infer missing phases, or conceal incomplete windows. |
| [Dawid, 1984, the prequential approach](https://rss.onlinelibrary.wiley.com/doi/10.2307/2981683) | Sequential statements must be tied to information available when issued. v0.10 keeps the current row out of historical state and seals candidate traces before canonical comparison. |
| [Hyndman, time-series cross-validation](https://pkg.robjhyndman.com/forecast/reference/tsCV.html) | Rolling forecast origins evaluate each origin from an earlier subset; window length is explicit. v0.10 uses a fixed 30-calendar-day trailing history and no full-period baseline in operational results. |
| [Gama et al., 2014, concept-drift adaptation](https://doi.org/10.1145/2523813) | A changing stream calls for time-aware monitoring, not retrospective pooling. v0.10 labels drift measures as descriptive measurement/schedule signals and does not retune the frozen detector. |

## Frozen interpretation boundary

The six canonical intervals are known detector candidates, not independently
verified physical outcomes. The anonymous AMI stream has no repair, inspection, or
field-outcome labels. Its outputs may describe score availability, candidate worklist
behavior, overlap with the six fixed intervals, rank agreement, and measurement or
schedule drift. They may not support a claim about confirmed physical faults,
operational promotion, municipal performance, or economics.

v0.9's H1 and its controlled-scenario decision remain frozen. The v0.10 replay
does not alter configuration, thresholds, feature handling, weather weight, source
rows, or any v0.9 selection decision. It invokes the frozen detector only when the
protocol's causal and quality gates are met. Municipal assets, KMA/KASI context,
and any external data remain prohibited for these anonymized meters.

## Decisions incorporated into the protocol

- `availability_time` is the normalized source interval end. The row can be
  scored at that time; every consumed historical row must have an earlier
  availability time.
- The operational history is meter-local and exactly `[d - 30 calendar days, d)`.
  A full-period comparator, if ever created for diagnosis, is separately marked
  `noncausal_full_sample` and cannot feed a decision or promotion.
- The first potential score time is after an eligible 30-day history. Insufficient
  elapsed history is `not_evaluable_warmup`; insufficient qualified history is
  `not_evaluable_quality`; a current-row feature deficiency is `abstained_quality`.
- Exact duplicate rows are collapsed deterministically; conflicting duplicates are
  quarantined. Same-time rows never update one another's history.
- A candidate decision is immutable at its decision time. Episode closure may be
  learned later, but that later observation records a finalization event and never
  rewrites the earlier decision.
- The canonical-six artifact is inaccessible to scoring and loaded only after a
  pre-overlap candidate trace hash is sealed. Fixed overlap is then a reporting
  join, not an input to any detector state or threshold.

The accompanying protocol turns these decisions into the implementation contract,
including exact per-origin proof fields, meter-day output rows, descriptive drift
metrics, and leakage gates.
