# Terra Agent B: v0.11 H1-Independent Proxy Detectors

## Task record and scope

- Date: 2026-08-21
- Role: Agent B, raw-current proxy detector implementer.
- Preconditions: P0 Route C is sealed after a 149-file, 1,165,875-row audit with usable Gold `0` and usable Silver `0`.
- Preservation: v0.10 release `d34d8323b3742c9116060d9548bd29c18750cb1f`, frozen H1, raw/Office sources, audit artifacts, harness, UI, and Git state are not modified.
- Workflow exception: the repository contract normally requests a harness backlog entry. The commissioned scope permits only this document and `scripts/run_v11_independent_detectors.py`; this task record is the permitted trace.

## Purpose and claim boundary

This work creates three independent implementations that describe unusual patterns in raw AMI current. They are proxy anomaly signs, not outcome labels. Route C permits coverage, internal overlap, deterministic control comparison, and data-quality reporting only. It does not permit a field-outcome conclusion or a claim that an observed signal represents a specific operational condition.

The detector implementations have no access to H1, asset data, schedules, solar data, weather, scenario injection, previous detector decisions, canonical-six contents while scoring, or labels. The shared raw-current source means their agreement is not independent corroboration.

## Time split and seal order

1. Read the protected B-line workbook and confirm its immutable SHA-256.
2. Confirm hashes in the v0.10 preservation manifest without writing to it.
3. Fit all profiles and thresholds only from April 2026 logical dates.
4. Write the detector freeze JSON.
5. Score May and June 2026 from the frozen configuration.
6. Write `v11_proxy_scores_prejoin.csv`, calculate its SHA-256, and write `v11_proxy_score_seal.json`.
7. Only after that seal, load the six canonical rows for descriptive joining and meter/time/month matched controls.

The score file contains derived scores and opaque sample identifiers only. It excludes raw current values. Source `24:00` is normalized to next midnight for timestamp ordering while retaining the prior logical date, matching the v0.10 raw manifest convention.

## D1/P1: robust meter-local time-slot residual

For each meter and 15-minute local slot, D1 calculates the April median of the sum of observed phase currents and a robust MAD scale. The May-June score is the absolute standardized residual. Its April 99.5th percentile, subject to a minimum threshold of four robust units, is frozen before the score period. This adapts to each meter's ordinary daily shape without using any schedule or context source.

## D2/P2: causal EWMA/CUSUM persistence

D2 consumes only the magnitude of D1's raw-current residual before its threshold decision. The state begins at the final April state and is updated after each score-time decision. It combines an EWMA of residual excess with a decayed CUSUM, then freezes a meter-specific April 99.5th-percentile threshold. It is causal within the score period: no later May-June sample affects an earlier score.

D2 is not evidence independent of D1. It is a distinct persistence transform of the same current stream and is reported as such.

## D3/P3: three-phase current-share pattern

D3 applies only when all three current channels are observed and their total is positive. It models the April meter-slot median share of each phase and its robust scale, then takes the maximum absolute standardized phase-share residual. Rows without three observed phases are `N/A`, including one-phase measurements. They are not converted to zero or a negative signal.

## Deterministic matched controls

After score sealing, each canonical row is anchored to the nearest score-time sample. The control sampler searches only raw score-window rows that match meter, logical month, and 15-minute slot, use a different logical date, and lie outside every canonical event's four-hour exclusion window. It chooses the candidate with the minimum SHA-256 under a fixed namespace. Detector scores do not enter eligibility or selection.

This yields a reproducible descriptive comparator, not a negative outcome set.

## Concordance, uncertainty, and blinded packet

- Pairwise concordance reports signal counts, intersections, unions, and Jaccard overlap. Its caption explicitly states common raw-source dependence.
- Meter-day cluster bootstrap uses 2,000 resamples and fixed seed `202611`. It reports uncertainty for proxy-signal shares only.
- The blinded packet has four mutually exclusive, priority-ordered strata: `S3_PHASE_PATTERN`, `S2_PERSISTENCE`, `S1_RESIDUAL`, and `S0_NO_PROXY`. Each requests 15 deterministically selected samples where available. The packet hides stratum, source meter, timestamp, and detector outputs; the separate local key is necessary to unblind after an independently specified review protocol.

## Runtime artifacts

Running `python3 scripts/run_v11_independent_detectors.py` writes:

- `lightguard_v0_1/data/validation/v11/v11_proxy_detector_freeze.json`
- `lightguard_v0_1/data/validation/v11/v11_proxy_scores_prejoin.csv`
- `lightguard_v0_1/data/validation/v11/v11_proxy_score_seal.json`
- `lightguard_v0_1/data/validation/v11/v11_proxy_canonical_six.csv`
- `lightguard_v0_1/data/validation/v11/v11_proxy_matched_controls.csv`
- `lightguard_v0_1/data/validation/v11/v11_proxy_artifact_manifest.json`
- `lightguard_v0_1/reports/v11/v11_proxy_concordance.csv`
- `lightguard_v0_1/reports/v11/v11_proxy_meter_day_bootstrap.json`
- `lightguard_v0_1/reports/v11/v11_proxy_detector_summary.md`
- `lightguard_app/assets/data/context/v11_proxy_detector_summary.json`

All downstream readers must preserve the Route C wording in the app summary. A later evaluation requires a separately audited, time-aligned, independently produced outcome source and must keep these proxy artifacts immutable.

The authoritative H1-aware blind-review packet is assembled later by
`build_v11_release.py`, after the proxy score seal. It retains actual stratum
availability rather than fabricating cases to fill a requested group.
