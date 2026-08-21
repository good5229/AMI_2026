# LightGuard v0.15 Target-Domain Mechanism Ablation, Necessity and Counterfactual Protocol

**Owner:** TERRA A

**Status:** PRE_OUTCOME_FROZEN

**Date:** 2026-08-21

## Scope and frozen predecessor boundary

This protocol assesses whether runtime-active components of the frozen H1 decision path are necessary or jointly sufficient **within the sealed target-domain counterfactual-pair corpus**. It does not alter, re-run, reinterpret, or use v0.10-v0.14 outcome values to choose a design. It preserves v0.13/v0.14's external-evidence boundary: no result here estimates Suyeong-gu streetlight field accuracy, fault probability, maintenance priority correctness, or a physical fault cause.

The evaluation begins only after a manifest freezes: source hashes; pair IDs; meter-day IDs; anomaly/benign allocation; labels and their provenance; time ordering; active components; component availability; phase/baseline gates; threshold; action map; seeds; and the analysis code version. Any change creates a new protocol version and cannot be merged into the v0.15 confirmatory result.

## Experimental question and unit

For each eligible counterfactual pair `p`, let `x(p, 0)` be its benign/control side and `x(p, 1)` its anomaly/counterfactual side. The same H1 runtime is invoked for both sides. No pair may be selected, discarded, matched, or re-labelled after any H1, ablation, or comparator outcome is viewed.

The inferential unit is the `meter-day` cluster. A pair belongs to exactly one meter-day; a meter-day belongs to exactly one analysis split. Multiple readings, time windows, assets, channels, phases, injected timestamps, or scenario repeats within that meter-day are not independent observations. Primary uncertainty uses paired, meter-day cluster bootstrap with 2,000 resamples and a fixed seed recorded in the manifest. If fewer than 40 meter-day clusters are eligible, report cluster count and use the paired cluster bootstrap interval without row-level p-values.

## H1 component registry and runtime eligibility

H1 is evaluated only through the active components named in the frozen runtime manifest. The following tags describe existing signal roles; they do not authorize adding a feature or changing its implementation.

| Tag | Existing runtime role | Availability gate | Ablation operation |
| --- | --- | --- | --- |
| `B` | meter-relative robust baseline departure / magnitude evidence | history and positive robust scale exist; baseline is strictly pre-window | remove only `B` from the fixed score/action path |
| `P` | persistence / temporal accumulation evidence | ordered valid timestamps and minimum frozen duration exist | remove only `P` |
| `C` | abrupt or structural-change evidence | ordered valid timestamps and frozen CUSUM/change semantics exist | remove only `C` |
| `M` | frozen multicomponent aggregation / consistency path | at least the manifest-specified non-phase components are available | remove only aggregation contribution; do not refit weights |
| `A` | phase/channel magnitude-asymmetry observation | all v0.14 PMC-3 gates pass: 3+ same-quantity named channels, common clock, physical scale, documented representation, independent aligned label, and pre-outcome split | remove only `A` |

`A` is absent, rather than zero, when the phase gate fails. Incomplete channels, RMS-only values, or unknown phase identity cannot create `A`, negative sequence, or a phase substitute. `B` is absent when its baseline gate fails; a within-window estimate, future history, or label-derived reference cannot replace it.

The runtime-active set is the intersection of these tags with the sealed manifest. Full H1 is that exact set. An ablation is admissible only for a tag active for **both sides of every included pair**. If availability differs within a pair, exclude the entire pair for that ablation and report the pre-outcome exclusion count.

## Paired conditions and threshold lock

For every included pair and each eligible ablation condition, execute:

1. `Full`: all runtime-active components, frozen preprocessing, and threshold `T`.
2. `-B`, `-P`, `-C`, `-M`, and `-A`: one admissible singleton removed, with every other component and threshold `T` unchanged.
3. `-(B,P)` and `-(P,C)`: the only confirmatory two-component removals, executed only when both components are active for all included pair sides.

`T` is the exact threshold serialized by the predecessor manifest. It must not be recalibrated per component, per class, per side, per meter, per day, or per action. Equal score boundary behavior, missing-value behavior, and action tie order are also inherited unchanged. The protocol does not use a retrained model, new normalizer, permutation-refit loop, or outcome-selected threshold.

For each condition `q`, derive pair-side alerts `a_q(p,s)` and the pair mechanism contrast `d_q(p) = a_q(p,1) - a_q(p,0)`. The primary condition contrast is `Delta_q = BA_q - BA_Full`, calculated at meter-day cluster level with the frozen anomaly/benign allocation. The report also gives the paired alert discordance rate and action concordance, but neither replaces `Delta_q`.

## Allocation, matching and leakage controls

The anomaly/benign allocation is fixed before H1 output access. Every pair contains one declared anomaly/counterfactual side and one declared benign/control side; neither allocation may be inferred from H1 scores. Pair matching may use only source identity, meter identity, calendar constraints, observation duration, data-quality masks, and pre-window covariates that exclude labels and post-window measurements.

Training, calibration, and evaluation split at meter-day level. A meter cannot contribute days to both calibration and evaluation unless the frozen predecessor protocol explicitly permits chronological separation; in that case all baseline history for an evaluation window is strictly earlier than its window. No time row, counterpart, derived history, scenario sibling, or duplicate may cross splits. Allocation balance is reported as counts of pairs and meter-days, never inflated sample rows.

## Necessity and sufficiency decisions

All thresholds below are effect-size and uncertainty rules fixed before outcomes. They are not production acceptance thresholds.

| Claim | Required preconditions | Frozen decision rule | Allowed conclusion |
| --- | --- | --- | --- |
| `NECESSARY_FOR_THIS_CORPUS` for component `j` | `j` active for all included pairs; comparable action scale; at least 30 meter-day clusters | singleton removal has `Delta_-j <= -0.05`, the 95% paired-cluster bootstrap upper bound is below `-0.02`, and at least 70% of discordant pairs degrade from correct Full alert behavior to incorrect ablation behavior | H1's observed discrimination in this corpus depends materially on `j` under the frozen path |
| `NOT_SHOWN_NECESSARY` | comparable action scale | any necessity condition fails | no necessity claim; this is not evidence that `j` is physically irrelevant |
| `SUFFICIENT_AS_PREREGISTERED_SUBSET` for subset `S` | `S` is one of `{B,P}`, `{B,C}`, `{B,P,C}`, or `{B,P,C,A}` when all members are gated; comparable scale; at least 30 clusters | restricted runtime using only `S` has `BA_S - BA_Full >= -0.02`, 95% paired-cluster lower bound at least `-0.05`, and action concordance with Full at least `0.90` | the subset approximates this frozen H1 path on this corpus only |
| `NOT_SHOWN_SUFFICIENT` | comparable action scale | any sufficiency condition fails | no subset sufficiency claim |
| `NOT_EVALUABLE_GATE` | a required baseline, phase, timestamp, or provenance gate fails | do not compute a substitute statistic | availability limitation only |
| `NOT_COMPARABLE_ACTION_SCALE` | Full and condition emit different eligible action scales, action vocabularies, or escalation eligibility | do not calculate action concordance, action delta, necessity, or sufficiency | score-level descriptive result may be separate only if score scale remains identical |

Balanced accuracy is reported only when both frozen allocation classes are present in the relevant meter-day cluster sample. If score-level discrimination is comparable but action scale is not, report the score result labelled `SCORE_ONLY_NOT_ACTION_COMPARABLE`; never use it for an operational priority claim.

## Limited interaction design

The confirmatory interaction set is deliberately limited to `B x P` and `P x C`. These are the only pairs that describe an ordered baseline-plus-duration or duration-plus-change mechanism without assuming a physical cause. For interaction `(j,k)`, calculate the departure from additivity:

`I_jk = Delta_-(j,k) - Delta_-j - Delta_-k`.

Call `INTERACTION_SIGNAL_FOR_THIS_CORPUS` only if the paired-cluster 95% interval for `I_jk` excludes zero and its absolute point estimate is at least `0.03` balanced-accuracy units. Otherwise report `NO_INTERACTION_SIGNAL_SHOWN`. Do not test higher-order interactions, mine subgroups, or interpret interaction direction as electrical causality. Phase interaction is excluded because its availability is provenance-gated and may be structurally absent.

## Secondary permutation diagnostic

Held-out, meter-day-blocked permutation importance may be produced only as a sensitivity diagnostic after the paired runtime analysis. Permute a component's already available input jointly within its meter-day and preserve time ordering where required; never permute rows independently. Use the same frozen evaluation split and record 30 repeats with a manifest seed. Correlated components can mask each other, so this diagnostic cannot decide necessity, sufficiency, physical mechanism, or component selection. The paired runtime ablation above remains primary.

## Reporting and claim limits

The final table must contain, per condition: active-component set, eligibility/gate status, meter-days, pairs, anomaly and benign counts, `BA`, `Delta_q`, paired-cluster interval, discordance, action-scale comparability, action concordance where valid, and the prespecified status. It must separately list all excluded pairs and their pre-outcome reason.

Permitted conclusion: a named component or fixed subset changed the frozen H1 path's paired target-domain discrimination under this corpus's counterfactual construction.

Prohibited conclusions: component is a real-world cause; an alert is a confirmed fault; performance applies to all Suyeong-gu cabinets; external datasets establish municipal accuracy; a phase quantity implies negative sequence; or a `NOT_COMPARABLE_ACTION_SCALE` result is an operational win or loss.

## Sources

- [NIST/SEMATECH experimental design](https://www.itl.nist.gov/div898/handbook/pri/section1/pri11.htm)
- [NIST/SEMATECH design selection and factorial screening](https://www.itl.nist.gov/div898/handbook/pri/section3/pri33.htm)
- [scikit-learn permutation importance](https://scikit-learn.org/stable/modules/permutation_importance.html)
- [Hemming and Taljaard on cluster randomized trials](https://pmc.ncbi.nlm.nih.gov/articles/PMC10555937/)
- [Cochrane Handbook, non-standard trial designs](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-23)
- [NIST CUSUM reference](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm)
