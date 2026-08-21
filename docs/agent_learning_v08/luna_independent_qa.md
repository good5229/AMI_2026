# Agent Learning Note

## Role

Subagent D / LUNA: independent fresh-context red-team QA for LightGuard v0.8 calibration, confirmatory holdout, reproducibility artifacts, claim boundaries, and Flutter integration.

## Model actually used

`gpt-5.6-luna`

## Checked date

`2026-08-20` (Asia/Seoul)

## Sources

- URL: https://openai.com/index/harness-engineering/
  - Institution/author: OpenAI, Ryan Lopopolo.
  - Checked: 2026-08-20.
  - Key point: reliable agent work depends on explicit repository knowledge, executable plans, observable feedback loops, and mechanically enforced invariants.
  - LightGuard application: treat the v0.8 design matrix, freeze hashes, artifact contracts, preflight, and audit report as executable evidence rather than relying on narrative intent.
- URL: https://itl.nist.gov/div898/handbook/prc/section2/prc241.htm
  - Institution/author: NIST/SEMATECH e-Handbook of Statistical Methods.
  - Checked: 2026-08-20.
  - Key point: the Wilson interval is obtained by inverting the binomial score test and is appropriate for small-sample proportions.
  - LightGuard application: verify the implemented Wilson formula and report recall/FPR intervals without substituting a normal approximation.
- URL: https://scikit-learn.org/stable/modules/model_evaluation.html
  - Institution/author: scikit-learn documentation.
  - Checked: 2026-08-20.
  - Key point: evaluation metrics must be tied to the defined scoring rule; precision, recall, average precision, and thresholded decisions answer different questions.
  - LightGuard application: keep recall, FPR, hard-negative FPR, average precision, abstention, and fixed threshold decisions separate in the holdout report.
- URL: https://www.nist.gov/publications/nist-framework-and-roadmap-smart-grid-interoperability-standards-release-40
  - Institution/author: National Institute of Standards and Technology, NIST SP 1108r4.
  - Checked: 2026-08-20.
  - Key point: smart-grid interoperability claims require explicit interfaces, actors, information exchanges, and security/reliability boundaries.
  - LightGuard application: do not treat generated scenario signals, public asset records, and competition AMI as one interoperable field system; require an authorized cabinet-to-meter mapping before a regional AMI claim.
- URL: https://doi.org/10.1016/j.patter.2023.100804
  - Institution/author: Sayash Kapoor and Arvind Narayanan, Patterns.
  - Checked: 2026-08-20.
  - Key point: leakage can arise during collection, preprocessing, modeling, sampling, and evaluation; access to a test set during model development creates optimistic estimates.
  - LightGuard application: audit case IDs, seeds, factor tuples, signal parameters, asset pools, feature masks, and post-holdout parameter changes separately. A row split alone is not treated as proof of every form of independence.
- URL: https://reproducibility.sigmod.org/
  - Institution/author: ACM SIGMOD Availability and Reproducibility Initiative.
  - Checked: 2026-08-20.
  - Key point: reproducibility submissions should document commands, options, environment, and an automated master experiment path.
  - LightGuard application: execute the repository preflight, record its exit status and exact commands, and compare deterministic manifest hashes rather than reporting only expected results.
- URL: https://aaai.org/conference/aaai/aaai-26/reproducibility-checklist/
  - Institution/author: Association for the Advancement of Artificial Intelligence.
  - Checked: 2026-08-20.
  - Key point: reproducible experiments should disclose tried parameters, selection criteria, seeds, infrastructure, metrics, run counts, variation, and final parameters.
  - LightGuard application: verify the candidate freeze before holdout execution, retain the failed gate, record seed `20260820` and 1,000 resamples, and prohibit post-holdout retuning.
- URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC3812051/
  - Institution/author: Sandve et al., PLOS Computational Biology, "Ten Simple Rules for Reproducible Computational Research."
  - Checked: 2026-08-20.
  - Key point: every result should retain the precise workflow, inputs, software, parameters, and provenance that produced it.
  - LightGuard application: require the v0.8 reproducibility manifest and verify every listed SHA-256 against the current bytes.

## Risks

- The initial restricted-sandbox preflight could not complete because the Flutter SDK attempted to update a cache outside the workspace and received `Operation not permitted`. The orchestrator subsequently supplied authoritative evidence that the exact integrated preflight passed after approved SDK-cache permissions; this rerun treats the gate as resolved.
- Calibration and confirmatory rows are disjoint in the declared identifiers and asset pools, but both splits draw official context from the same 12-cell 2025 KMA/KASI cache. This is a residual context-episode dependence risk for any future weather-promoted model.
- Wilson intervals are computed for unconditional class-level detection proportions, while separate evaluable metrics exclude abstentions. The distinction is mathematically visible in code but should remain explicit in user-facing interpretation.
- Generated scenarios are not field AMI observations. Absence of an actual Gangneung/Chungju cabinet-linked AMI mapping prevents regional field-performance claims.
- `docs/goal_progress_v08.md` still contains the pre-rerun blocker/pending wording even though the regenerated final report records the approved-permission preflight PASS.

## Adopted rules

- A deterministic artifact contract, freeze hash, or narrative flag is evidence only after recomputing it from current bytes.
- A confirmatory holdout is considered row/asset/signal separated only when case IDs, seeds, factor tuples, signal parameter IDs, and selected asset pools are disjoint; shared context sources are reported as a residual limitation.
- v0.7 cases remain regression-only. Official v0.7 context may be used as an exogenous source for v0.8 scenario materialization, but v0.7 outcome rows must not be ingested for tuning.
- Missing Chungju load is represented as unavailable with no imputation. Zero fixture counts are not converted into watts.
- Weather remains `context_only` unless a predeclared candidate improves the non-weather parent under the stated gate on confirmatory data. The observed C3 result does not satisfy that decision.
- No candidate is promoted when FPR or hard-negative FPR exceeds the predeclared limit, even when recall improves.
- An integrated preflight supplied as authoritative orchestrator evidence may be accepted when the exact command, permission change, and complete PASS output are recorded; the restricted reviewer must not rerun it when explicitly prohibited.
