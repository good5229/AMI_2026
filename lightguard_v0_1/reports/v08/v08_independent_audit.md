# LightGuard v0.8 Independent Red-Team Audit

## Audit identity and scope

- Reviewer: Subagent D / LUNA
- Model actually used: `gpt-5.6-luna`
- Checked date: `2026-08-20` (Asia/Seoul)
- Scope: fresh-context inspection of committed/frozen and uncommitted v0.8 artifacts, implementation, reports, Flutter card, and required verification commands.
- Change boundary: no direct edits to product code, data, scripts, or existing reports. Only this report, the learning note, and ignored harness records were written. No Git command was used.
- External AMI boundary: this audit does not claim actual regional AMI performance.

## Commands run and actual results

| Command | Result |
|---|---|
| `./scripts/v08_preflight.sh` | PASS, authoritative orchestrator evidence supplied after approved Flutter SDK-cache permissions. v0.7 freeze, v0.8 deterministic passes 1/2, artifact contracts, analyze, test, Web release, and Android release all passed. |
| `/Users/bellhundred/flutter_3_44_0/bin/flutter pub get` | PASS. Dependencies resolved; 16 constrained newer-version notices. |
| `/Users/bellhundred/flutter_3_44_0/bin/flutter analyze` | PASS. `No issues found!` |
| `/Users/bellhundred/flutter_3_44_0/bin/flutter test` | PASS. `All tests passed!`, 21 tests. |
| `/Users/bellhundred/flutter_3_44_0/bin/flutter build web --release` | PASS. Web release built. |
| `/Users/bellhundred/flutter_3_44_0/bin/flutter build web --release --base-href /AMI_2026/` | PASS. Exact Pages command built Web release. |
| `/Users/bellhundred/flutter_3_44_0/bin/flutter build apk --release` | PASS. APK built at 52.2 MB. |
| `python3 scripts/build_v08_design.py --check` | PASS, executed by `v08_preflight`. |
| `python3 scripts/test_v08_artifacts.py` | PASS, executed by the supplied successful `v08_preflight`. |
| Read-only split/SHA audit command | PASS: 288/432 rows; all five overlap sets empty; v0.7 case-ID overlap 0; Chungju load null and `unavailable_no_imputation`; manifest mismatches 0. |

The integrated preflight was not rerun in this restricted sandbox, per instruction. The supplied orchestrator result is treated as authoritative for the integrated gate; the previously observed SDK-cache permission failure is therefore resolved for this audit run. The individual Flutter commands independently passed as recorded above.

## 11-item Independent QA Gate

| # | Required check | Status | Evidence and boundary |
|---:|---|---|---|
| 1 | v0.7 frozen 96 cases were not used for tuning | PASS | `scripts/build_v08_design.py:1-5` states that v0.7 cases are not read; `scripts/run_v08_calibration.py:123-132` materializes only calibration rows and records `v07_cases_ingested: false`; `scripts/test_v08_calibration.py:23-25` enforces it. The independent case-ID comparison found 0 overlap. The shared v0.7 official context cache is an exogenous context source, not v0.7 outcome-row ingestion. |
| 2 | Calibration and confirmatory are separated | PASS with residual risk | `scripts/build_v08_design.py:271-318` creates unique IDs, seeds, signal parameters, and factor tuples; `:335-371` checks uniqueness and disjoint asset pools. `scripts/test_v08_artifacts.py:35-38` checks all five declared split fields. Independent audit found zero overlap for case ID, seed, factor tuple, signal parameter ID, and asset cabinet UID. Both splits nevertheless reuse the same 12-cell context cache; see F-01. |
| 3 | No parameter changes after confirmatory results | PASS | `scripts/run_v08_confirmatory.py:43-52` verifies the frozen design and candidate-freeze SHA before loading confirmatory rows; `:151-185` evaluates frozen configs only; `:193-200` records `selected_candidate` and `retuning_after_holdout: false`. `scripts/test_v08_artifacts.py:41-45` enforces null selection and no retuning. |
| 4 | No unsupported Chungju load imputation | PASS | `scripts/build_v08_design.py:79-91` sets Chungju rated load to `None` and status `unavailable_no_imputation`; `:367-371` enforces blank load fields and the status. `scripts/run_v08_feature_availability.py:24-35` removes values without adding replacements. Current Chungju rows contain only null load values and `unavailable_no_imputation`. |
| 5 | Weather effect is not exaggerated | PASS | `scripts/run_v08_confirmatory.py:178-196` applies a predeclared incremental rule; current summary records `weather_policy: context_only`, and `lightguard_v0_1/reports/v08/v08_weather_candidate_decision.md:3-7` preserves that decision. C3 did not become a promoted production candidate. |
| 6 | Wilson and bootstrap calculations are correct | PASS with estimand note | `scripts/v08_detector.py:108-116` implements the Wilson score interval; `scripts/run_v08_confirmatory.py:83-110` uses fixed seed `20260820`, 1,000 resamples, and `(cell_id, label)` strata. The summary and uncertainty report preserve those settings. Wilson intervals use all class rows; abstention-excluded `recall_evaluable` and `fpr_evaluable` are separately reported by `scripts/v08_detector.py:128-163`. |
| 7 | No actual regional AMI claim | PASS | `scripts/run_v08_confirmatory.py:137-145` sets `actual_ami: false`; `:198-200` states no actual Gangneung/Chungju performance claim. The final report prohibits actual regional generalization at `lightguard_v0_1/reports/v08/v08_final_summary.md:109-114`; the Flutter test enforces unavailable status at `lightguard_app/test/unit/v08_detector_validation_test.dart:11-21`. |
| 8 | Scenario data and actual data are clearly separated | PASS | Calibration source is `v08_controlled_calibration_not_actual_ami` at `scripts/run_v08_calibration.py:57-90`; confirmatory source is `v08_controlled_confirmatory_not_actual_ami` at `scripts/run_v08_confirmatory.py:131-145`. The app documentation also calls the holdout controlled and actual regional AMI unvalidated at `lightguard_app/docs/v08_detector_validation.md:1-3`. |
| 9 | SHA artifacts reproduce | PASS | `scripts/v08_preflight.sh:18-28` compares two deterministic manifest hashes; `scripts/test_v08_artifacts.py:68-71` recomputes every manifest file hash. The independent check found no manifest mismatches. Design SHA is checked by `scripts/build_v08_design.py --check` and by calibration/confirmatory freeze guards. |
| 10 | Flutter card matches reports | PASS | `v08_detector_card.dart:46-76` displays 432 cases, C1 recall/FPR, Wilson values, no imputation, context-only weather, and the actual regional AMI limitation. These values align with `v08_detector_summary.json`, `v08_detector_validation.md:1-3`, and `v08_uncertainty_summary.md:3-20`. The card does not display C3 as promoted and does not claim field performance. |
| 11 | Test/build actually succeeds | PASS | The supplied authoritative integrated `./scripts/v08_preflight.sh` result is PASS after approved SDK-cache permissions. It reports v0.7 freeze PASS, v0.8 deterministic passes 1/2 and artifact contracts PASS, analyze with no issues, 21 tests passed, Web release PASS, and Android release APK PASS at 52.2 MB. The independent individual commands also passed. |

## Severity-ranked findings

### F-01 [MEDIUM] Holdout independence is row-level, not context-episode-level

Both materializers use the same official context source: `scripts/run_v08_calibration.py:18-19,121-124` and `scripts/run_v08_confirmatory.py:21-22,128-135`. Each split is separately seeded and uses disjoint generated identifiers and asset pools, but both draw observations from the same 12 region-season KMA/KASI cache. The confirmatory generator selects an observation by `random_seed % len(observations)` in `scripts/run_v08_calibration.py:51-55`, so the context pool and potentially individual hourly observations can recur across splits.

Impact: this does not leak v0.7 outcome rows, labels, or candidate parameters, and weather remains context-only after C3 failed promotion. It does limit the strength of the phrase “independent holdout” for a future weather-sensitive candidate.

Recommended disposition: for a future weather candidate, freeze disjoint date windows or context episodes for calibration and confirmatory, and report both row-level and context-level overlap checks. Until then, describe the current result as an independently generated scenario/asset holdout under shared official context cells.

### F-02 [LOW] Abstention estimand should be labeled more explicitly

`scripts/v08_detector.py:128-163` computes Wilson recall/FPR using all abnormal/normal rows while separately computing `recall_evaluable` and `fpr_evaluable` after removing abstentions. The uncertainty report labels the first pair simply as “recall” and “FPR” at `lightguard_v0_1/reports/v08/v08_uncertainty_summary.md:7-12`.

Impact: the calculation is internally consistent, but users may not know whether an abstention is being counted as a miss, excluded from evaluation, or both in separate views.

Recommended disposition: retain both estimands but label the intervals as unconditional detection-rate Wilson intervals and add explicit evaluable-only intervals if abstention becomes production-facing.

### F-03 [LOW] Goal progress document remains stale

`docs/goal_progress_v08.md:5-6,26-33,42-49` still says the approved-permission rerun is in progress, the initial permission issue is an active blocker, and the next step is to rerun the preflight. This conflicts with the regenerated final report at `lightguard_v0_1/reports/v08/v08_final_summary.md:98-106` and the supplied authoritative PASS evidence.

Impact: this is documentation freshness only and does not change the frozen artifacts, detector parameters, or QA result. It can nevertheless cause a future agent to repeat a completed gate or report the wrong project phase.

Recommended disposition: update `docs/goal_progress_v08.md` in a separately authorized documentation change to record the approved-permission PASS and this audit's residual risks.

## Findings not observed

- No Critical finding was observed.
- No unsupported Chungju load imputation was observed.
- No post-holdout candidate promotion or parameter mutation was observed.
- No actual Gangneung/Chungju AMI performance claim was observed in the reviewed report, app asset, app documentation, or Flutter card.
- No SHA mismatch was observed in the v0.8 reproducibility manifest.
- No candidate parameter or confirmatory holdout mutation was observed: design SHA `9fba439a...`, calibration SHA `b9825d7b...`, candidate-freeze SHA `12fdb827...`, and holdout SHA `71a4d709...` remain unchanged from the prior audit.

## Allowed and prohibited claims after this audit

Allowed:

- v0.8 generated calibration and confirmatory scenario rows are separated by the declared row, signal, and asset identifiers.
- Experimental C1/C2 recall improved on the controlled confirmatory scenarios, but the candidates failed the FPR gate and were not promoted.
- Weather remains context-only under the current decision rule.
- Chungju rated load remains unavailable with no imputation.

Prohibited:

- Actual regional AMI generalization or field accuracy.
- Gangneung or Chungju AMI performance.
- Actual fault detection rate, maintenance savings, or production readiness for C1/C2/C3.
- Treating the shared-context controlled holdout as actual regional AMI validation.

## Final verdict

**PASS with non-critical residual risks.** All 11 Independent QA Gate items are satisfied using the supplied authoritative integrated preflight PASS plus the independently repeated individual Flutter gates. No Critical finding remains, no candidate parameters or holdout rows changed, and the regenerated report and Flutter card are consistent. Residual risks are limited to shared KMA/KASI context episodes across the two splits, explicit labeling of full-sample versus abstention-excluded estimands, and stale `docs/goal_progress_v08.md` status text. Actual regional AMI performance remains unvalidated and must not be claimed.
