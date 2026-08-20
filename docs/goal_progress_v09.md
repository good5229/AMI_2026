# LightGuard v0.9 Goal Progress

Date: 2026-08-20
Branch: `codex/context-aware-validation`
Baseline HEAD: `8772c2759d16ed7a6e669b940880e10cb242d1d6`

## Checkpoints

- [x] CP1a: v0.8 code, data, official context, AMI replay, and Flutter state frozen.
- [x] CP1b: v0.8 false-positive inventory and unchanged taxonomy complete.
- [x] CP1c: SOL/TERRA/LUNA pre-validation learning records complete.
- [x] CP2: 48 official 2025 episodes and zero-overlap split frozen.
- [x] CP3: 384 calibration cases evaluated and H1 candidate configuration frozen.
- [x] CP4: 576 confirmatory cases evaluated without retuning; H1 passed controlled promotion gates.
- [x] CP5: episode bootstrap, hard-negative, solar-boundary, missing-feature, and episode effects complete.
- [x] CP6: six actual-AMI replays and Flutter evidence complete; independent QA and complete preflight pending.
- [ ] Release: commit and push current branch; update PR #2 without creating a branch.

## Immutable policies

- v0.8 is regression and failure-analysis evidence only, never v0.9 tuning data.
- Split seed is `20260901`; calibration and confirmatory episode/date/KMA-observation overlap must be zero.
- Weather is `context_only` with score weight `0`.
- Chungju rated load remains unavailable; imputation is prohibited.
- Confirmatory results cannot change candidate parameters.
- Product promotion failure is represented as `selected_candidate: null`.

## Final release gate

- 2026-08-20: independent QA PASS with residual risks (Critical/High/Medium 0, Low 2).
- 2026-08-20: `scripts/v09_preflight.sh` PASS, including deterministic replay, artifact contracts, Flutter analyze/test/web/APK.
