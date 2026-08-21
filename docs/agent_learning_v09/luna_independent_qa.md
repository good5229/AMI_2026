# LUNA v0.9 Independent Red-Team QA Learning

Date: 2026-08-20 (Asia/Seoul)

Role: independent final QA. This pass did not modify product code, scripts,
data, scenarios, configs, other reports, `.env`, Git, branch, commit, or push.
The only tracked outputs of this pass are this learning note and
`lightguard_v0_1/reports/v09/v09_independent_audit.md`.

## Decision

Overall result: `PASS with residual risks` for the controlled v0.9 evidence
package. Critical findings: `0`. High findings: `0`. Medium findings: `0`.
Low residual risks: `2`. Non-critical statistical limitation: `1`.

The frozen H1 candidate passes the controlled confirmatory promotion gates:
recall `0.91666667`, normal FPR `0.0`, hard-negative FPR `0.0`, worst
region-season recall `0.91666667`, AP `1.0`, and abstention `0.0`. This is not
field AMI accuracy, municipal fault truth, or production authorization.

## Independent observations

- The canonical v0.8 freeze manifest is complete. It contains the v0.8
  calibration, confirmatory, and candidate-freeze hashes; C1/C2/C3 shared
  detector and runner hashes; official-context hashes; actual AMI replay asset
  hashes; Flutter state; the v0.7 SHA; and the frozen git baseline.
- The reports-side `v08_freeze_manifest.json` is a release pointer to the
  canonical data manifest and repeats the key v0.7/v0.8 hashes.
- v0.8 is explicitly marked as failure-analysis/regression-reference-only and
  `v08_used_for_v09_tuning` is false. The v0.9 calibration runner reads the
  v0.9 calibration set, while confirmatory evaluation reads the frozen v0.9
  holdout and candidate config.
- The episode manifest has 48 ready 2025 episodes: 3 regions, 4 seasons, 4
  episodes per region-season cell, with 24 calibration and 24 confirmatory
  episodes. KMA stations are 159, 105, and 127 for Suyeong, Gangneung, and
  Chungju respectively.
- Independent set checks found zero overlap for episode ID, global date,
  KMA station-date, KMA timestamp hash, case ID, signal parameter ID, and
  asset cabinet UID.
- All generated cases have `weather_weight=0.0` and
  `load_imputation=none`. Missing rated-load or phase evidence remains
  unavailable rather than imputed.
- The candidate configuration SHA is
  `b536f8ca68222662c717cd27a6af4c3c64a3330782b0545503df6e4aff3e6232`.
  `confirmatory_seen=false`, both retuning flags are false, and the
  confirmatory summary references that exact SHA.
- The six AMI replay rows have `field_truth_label=unavailable` and
  `promotion_gate_input=false`. They are technical regression/replay rows,
  not truth labels and not promotion evidence.
- Wilson intervals were independently recomputed for H1 from 264/288 recall,
  0/288 normal false positives, and 0/264 hard-negative false positives.
- The episode bootstrap was independently reproduced in memory with 24
  episode units, 2,000 resamples, and seed `20260901`. No frozen report was
  rewritten by the check.

## Non-critical bootstrap limitation

All four H1-minus-threshold-only bootstrap deltas (recall, FPR,
hard-negative FPR, and AP) were constant across the 2,000 resamples. This is
an expected consequence of the balanced generated episode construction: each
episode contributes the same signal/label composition and therefore the
episode resampling cannot expose between-episode variation for these deltas.
The bootstrap implementation is structurally correct, but its uncertainty
intervals are not informative for these constant contrasts. This is not a
promotion-gate failure; future evidence should use naturally varying episodes
or field-labeled AMI units.

## KASI provenance assessment

The provenance is defensible for a narrower claim. Thirty-six records are
derived from the public KASI web calculator page and its public JavaScript
assets, with SHA-256 values recorded for `algorithms.js` and `delta_t.js`.
Twelve records retain previously frozen official normalized values. No KASI
API key was needed for the web-calculator path, and no internal solar formula
was introduced into the v0.9 data package.

The defensible claim is: “KASI-public-web-calculator-derived solar context,
with source-page and source-asset provenance.” It is not: “raw KASI API
observations,” “official almanac table values for every episode,” or “field
truth.” The KASI page itself says the calculator is input-derived, can differ
slightly from monthly almanac data, and documents an estimated calculation
error below one minute. The package must retain that narrower wording.

## QA/statistical learning

- Group-level separation is the relevant invariant: observations belonging to
  the same domain group must not be split across train/calibration and
  confirmation. This is consistent with scikit-learn's definition of
  non-overlapping `GroupKFold` groups.
- The H1 gate is an explainable selective decision boundary. Explicit
  abstention/availability states preserve a reject option instead of silently
  converting missing evidence into a positive or negative label.
- Wilson intervals are appropriate for the small finite binomial denominators,
  but they describe the frozen controlled sample. They do not convert
  generated cases into independent field observations.
- Region, season, weather regime, episode, and region-season interaction
  outputs remain descriptive controlled effects. They must not be written as
  causal weather effects or municipal generalization claims.

## Sources consulted

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

