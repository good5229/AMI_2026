# v0.10 injection physical plausibility review

## Decision summary

Review identity: Subagent C. Requested model: `luna`. Actual runtime model: GPT-5/Codex. This is a physical-plausibility and provenance review, not a detector-performance or field-accuracy result.

The injection engine is **BLOCKED for unrestricted injection**. It can receive a **PASS** only for the constrained current-only path below: identity-copy of an approved measured current phase, exact interval-end timestamp join, no missing-value fill, no inferred phase, no energy mutation, and complete provenance.

## Evidence boundary

Only the v0.10 raw AMI manifest and anonymized AMI quality/meter profiles were inspected. The manifest reports:

- Five target meters, 2026-04-01 through 2026-06-30, `Asia/Seoul`.
- Interval-end timestamps, with source `24:00` normalized to the next midnight.
- Median current cadence of 15 minutes, no duplicate timestamps, and some 30-minute gaps.
- Current semantics `i1_ampere`, `i2_ampere`, and `i3_ampere`.
- `energy_reconstruction_allowed: false`.
- Three-phase measured-current count for B-L-9, B-L-12, and B-L-14; one-phase measured-current count for B-L-13 and B-L-35.

The review did not inspect raw `official_docs` rows/workbooks, `.env`, detector/config/results, app code, other reports, Git state, or tests.

## PASS/BLOCK conditions for the injection engine

| Gate | PASS condition | BLOCK condition |
| --- | --- | --- |
| Operation scope | Writes only an approved current column and records the source semantic as current. | Writes energy, voltage, power, power factor, status, or any unapproved column. |
| Source provenance | Uses the approved manifest/source identity, meter topology, phase, cadence, timestamp semantics, and quality state. | Missing source identity, unresolved denominator mismatch, generic meter substitution, or untraceable row mapping. |
| Phase topology | `3P4W`: only measured i1/i2/i3; `1P2W`: only the observed single phase. | Creates i2/i3 for a 1P2W meter, infers a phase from another phase, or claims complete 3-phase data with a missing required phase. |
| Value validity | Source current is present, finite, non-negative, and retains its current meaning. | Blank/invalid value is converted to zero or otherwise fabricated. |
| Scaling | Production path uses `s = 1.0`. Research-only mode is separately labeled `derived_current`; if used, `0.80 <= s <= 1.20` plus exact local rated-current and baseline guards are proven. | Any non-identity scale without exact local meter limits, any result beyond those limits, or any use of a generic manufacturer rating as the local limit. |
| Cadence | One-to-one exact join on meter, phase, and interval-end timestamp; source and target use `Asia/Seoul` and the manifest's next-midnight normalization. | Resampling, time shifting, duplicate joins, forward fill, interpolation, or synthetic row insertion. |
| Missingness | Missing source rows/channels remain missing and are excluded from complete-phase claims. | Missing is encoded as `0 A`, imputed, or treated as physical outage/phase loss without independent evidence. |
| Energy immutability | Pre/post energy values, timestamps, units, multipliers, accumulation semantics, and missingness mask are identical. | Any energy value, energy missingness, energy cadence, or energy row is changed, reconstructed, or reindexed. |
| Output audit | Every changed current cell carries source meter, timestamp, phase, semantic, source quality, operation, scale, and review status. | Changed cells cannot be traced to an approved measured source row. |

Any single BLOCK condition blocks the injection batch or the affected phase/time slice; it must not be downgraded to a warning.

## Meter and phase disposition

| Meter | Topology and observed evidence | Disposition |
| --- | --- | --- |
| B-L-9 | 3P4W; i1/i2/i3 present; current channel missing count 0; 15-minute current cadence; one 30-minute grid gap is reported. | **PASS** for exact measured i1/i2/i3 copies at matched timestamps. Preserve the grid gap; do not add a row. **BLOCK** any all-grid completion or energy edit. |
| B-L-12 | 3P4W; i1/i2/i3 present, but 46 current rows per phase are missing in the manifest. The manifest rate is 0.5266%, while the anonymized profile reports 0.497%. | **BLOCK** automatic whole-window injection until the denominator/provenance discrepancy is reconciled. After reconciliation, only nonmissing exact timestamp slices may PASS, with missing slices preserved and no complete-phase claim over them. |
| B-L-13 | 1P2W; i1 is the only measured phase; i2/i3 are structurally absent; current is 15 minutes while energy profile is 60 minutes and energy is heavily incomplete. | **PASS** only for i1 current-only copies at exact 15-minute timestamps. **BLOCK** i2/i3 creation, three-phase interpretation, and all energy manipulation. |
| B-L-14 | 3P4W; i1/i2/i3 present; current channel missing count 0; 15-minute current cadence; two 30-minute grid gaps are reported. | **PASS** for exact measured i1/i2/i3 copies at matched timestamps. Preserve grid gaps; do not add rows. **BLOCK** any all-grid completion or energy edit. |
| B-L-35 | 1P2W; i1 only; two i1 missing rows; i2/i3 structurally absent; energy profile is 60 minutes and energy is heavily incomplete. | **PASS** only for i1 nonmissing exact timestamp copies with the two gaps preserved. **BLOCK** i2/i3 creation, three-phase interpretation, and all energy manipulation. |

## Required implementation review record

Before a batch can be marked PASS, the engine review record must contain:

1. The unchanged energy identity result, including missingness-mask equality.
2. The exact source-to-target key count and duplicate check.
3. The per-phase eligibility decision and topology evidence.
4. The count of copied current cells, skipped missing cells, and any preserved target gaps.
5. The scale (`1.0` for production PASS) and the source operation label.
6. The B-L-12 rate reconciliation result, if B-L-12 is included.
7. A statement that no current value was used to reconstruct or alter energy.

## Final status

- **PASS condition:** constrained, phase-selective, identity current copy with exact cadence/provenance and byte/value-identical energy.
- **BLOCK condition:** unrestricted grafting; synthetic phase creation; missing-to-zero conversion; resampling; non-identity scaling without exact meter-specific guards; energy mutation; or unresolved B-L-12 quality/provenance discrepancy.
- **Current recommended eligible slices:** B-L-9 i1/i2/i3, B-L-13 i1, B-L-14 i1/i2/i3, and B-L-35 i1, subject to the per-timestamp gates above. B-L-12 remains blocked for automatic whole-window use pending reconciliation.

