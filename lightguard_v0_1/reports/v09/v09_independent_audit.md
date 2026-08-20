# LightGuard v0.9 Independent Red-Team Audit

Date: 2026-08-20 (Asia/Seoul)

## Verdict

`PASS with residual risks` for controlled v0.9 confirmatory evidence.

| Severity | Count | Finding |
|---|---:|---|
| Critical | 0 | No release-blocking gate failure found. |
| High | 0 | No high-severity integrity or claim-boundary failure found. |
| Medium | 0 | No medium-severity failure found. |
| Low | 2 | Exact v0.8 taxonomy bytewise comparison is limited by the absence of a separately named immutable v0.8 taxonomy baseline; tracked-secret membership was not checked with Git because Git operations were explicitly prohibited. |
| Non-critical limitation | 1 | All four bootstrap deltas are constant because generated episodes are balanced. |

The result promotes H1 only inside the controlled generated,
episode-separated validation boundary. It does not establish field AMI
accuracy, fault truth, causal weather effects, or production readiness.

## Gate-by-gate result

| Gate | Result | Evidence |
|---|---|---|
| v0.8 confirmatory data not used for v0.9 tuning | PASS | Canonical freeze says regression/failure-analysis only; `v08_used_for_v09_tuning=false`; v0.9 runners use v0.9 inputs. |
| 48 official 2025 episodes | PASS | 48 ready episodes, 24 calibration and 24 confirmatory, covering Suyeong/Gangneung/Chungju x four seasons. |
| Episode/date/KMA split isolation | PASS | Episode ID, global calendar date, KMA station-date, and KMA timestamp-hash intersections are all zero. Stations are 159/105/127. |
| Case/signal/asset isolation | PASS | Case ID, signal parameter ID, and asset cabinet UID intersections are all zero. |
| Candidate freeze and no retune | PASS | Candidate config SHA is `b536f8ca68222662c717cd27a6af4c3c64a3330782b0545503df6e4aff3e6232`; `confirmatory_seen=false`; post-holdout retuning is false; summary references the same SHA. |
| v0.8 hard-negative taxonomy | PASS with low residual risk | v0.9 inventory/taxonomy preserves the frozen v0.8 row-level identifiers and hard-negative categories. A separately named immutable v0.8 taxonomy baseline is not present for an independent bytewise diff, so the semantic “unchanged” claim remains provenance-based. |
| Weather and missing-load policy | PASS | Every generated case has `weather_weight=0.0` and `load_imputation=none`; no rated-load imputation was detected. |
| Actual AMI replay boundary | PASS | Exactly six rows; all truth labels are `unavailable` and all promotion inputs are `false`. Decisions include inspect/observe/normal states but are not truth outcomes. |
| Wilson intervals | PASS | Independent recomputation matches H1 intervals for recall 264/288, normal FPR 0/288, and hard-negative FPR 0/264. |
| Episode-cluster bootstrap | PASS with limitation | In-memory reproduction matches 24 episode units, 2,000 resamples, seed `20260901`. All four H1-minus-threshold-only deltas are constant due balanced generated episodes; this is non-critical but reduces uncertainty informativeness. |
| Descriptive subgroup claims | PASS | Region, season, weather-regime, episode, and region-season outputs are controlled descriptive analyses, not causal or municipal field claims. |
| KASI provenance | PASS with narrowed claim | 36 records use the public KASI calculator path with recorded `algorithms.js` and `delta_t.js` hashes; 12 retain frozen official normalized anchors. This supports calculator-derived context provenance, not raw API/almanac truth. |
| Secret policy | PASS with low verification residual | No `.env` value was accessed or written; repository ignore rules include `.env`, `harness_docs/`, `official_docs/`, and Office extensions. Git tracked-file inspection was intentionally not run because the user prohibited Git operations. |
| Flutter controlled boundary | PASS | The v0.9 summary contains 576 confirmatory cases, 24 confirmatory episodes, zero episode/date/KMA overlaps, H1 metrics, Wilson intervals, and `actual_ami_is_truth=false`; Flutter analyze/test also passed. |
| Required artifacts | PASS | Required v0.9 data, reports, freeze pointer, actual AMI replay, bootstrap, boundary, missing-feature, and final-summary artifacts are present. |

## Confirmatory metrics

H1: recall `0.91666667` with Wilson 95% `[0.87900183, 0.94336249]`; normal
FPR `0.0` with `[0.0, 0.01316283]`; hard-negative FPR `0.0` with
`[0.0, 0.01434229]`; worst cell recall `0.91666667`; AP `1.0`; abstention
`0.0`.

The threshold-only comparator has normal FPR `0.33333333` and hard-negative
FPR `0.36363636`, so the observed specificity recovery is visible inside the
controlled generated holdout. It must not be generalized to actual municipal
AMI without field truth.

## KASI claim boundary

The KASI public page states that the calculator derives results from user
inputs, that monthly almanac values can differ slightly, and that calculation
error can be below one minute. The JavaScript assets were not independently
re-hosted or treated as an official API response. The defensible statement is:

> v0.9 uses KASI-public-web-calculator-derived solar context with recorded
> page/asset provenance; 12 dates remain frozen official normalized anchors.

The package must not claim raw KASI API observations, complete official
almanac-table coverage, or solar values as field truth.

## Commands and exact outcomes

The independent read-only Python checker recomputed all split intersections,
case counts, policy fields, candidate SHA, Wilson intervals, KASI status counts,
actual AMI truth exclusion, required artifact presence, and the 2,000-resample
bootstrap in memory. Result: every check printed `PASS`; failures: `[]`.

`flutter analyze` first failed before analysis because the sandbox could not
write Flutter SDK cache files (`Operation not permitted`). The same command was
then rerun with the permitted elevated SDK-cache access:

```text
No issues found! (ran in 3.7s)
```

`flutter test` was run with the same permitted access:

```text
All tests passed!
```

Not run by instruction: `flutter build web`, `flutter build apk`, and the full
`scripts/v09_preflight.sh`. Also not run: `scripts/test_v09_artifacts.py`,
because its contract invokes `git ls-files` and the user explicitly prohibited
Git operations in this independent QA pass. No Git command, branch change,
commit, or push was performed.

## Residual risks and disposition

- The generated episode design is balanced enough to make all bootstrap
  contrasts constant. Keep the result as a structural reproducibility check,
  not as evidence of broad uncertainty coverage.
- Preserve the narrower KASI calculator-derived wording until raw official
  almanac/API records or field-labeled solar validation are available.
- Add a separately frozen v0.8 taxonomy baseline in a future authorized change
  if bytewise taxonomy-drift detection is required.
- Perform tracked-secret verification only in a future authorized Git/CI gate;
  this pass did not inspect `.env` or mutate Git by design.

## Sources

Accessed 2026-08-20.

- [OpenAI: Harness engineering](https://openai.com/index/harness-engineering/)
- [OpenAI: Introducing the Codex app](https://openai.com/index/introducing-the-codex-app/)
- [OpenAI: Codex](https://openai.com/codex/)
- [OpenAI Codex: AGENTS.md guidance](https://github.com/openai/codex/blob/main/docs/agents_md.md)
- [OpenAI Codex: multi-agent specification](https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/multi_agents_spec.rs)
- [Agentic AI Foundation: agents.md repository](https://github.com/agentsmd/agents.md)
- [scikit-learn: GroupKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html)
- [scikit-learn: cross-validation guide](https://scikit-learn.org/stable/modules/cross_validation.html)
- [NIST AI Risk Management Framework](https://airc.nist.gov/airmf-resources/airmf/)
- [Geifman and El-Yaniv, SelectiveNet, PMLR](https://proceedings.mlr.press/v97/geifman19a.html)
- [KASI: public sunrise/sunset calculator](https://astro.kasi.re.kr/life/pageView/9)
- [KASI public algorithms.js](https://astro.kasi.re.kr/resources/js/life/algorithms.js)
- [KASI public delta_t.js](https://astro.kasi.re.kr/resources/js/life/delta_t.js)

