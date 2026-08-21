# TERRA A v0.15 Target-Domain Ablation and Paired Design Learning Record

**Role:** TERRA A experimental-design methodologist.

**Actual Model:** This is not a new predictive model. The object of study is the already frozen, runtime-active LightGuard H1 decision path evaluated under a paired counterfactual protocol. The estimand is the within-pair change caused by removing a predeclared active component while retaining the same input, eligibility gates, threshold, and output scale. It is not feature attribution, fault-cause identification, or a new estimate of Suyeong-gu streetlight accuracy.

**Sources Reviewed:**

- [NIST/SEMATECH, What is experimental design?](https://www.itl.nist.gov/div898/handbook/pri/section1/pri11.htm) - experiments require a plan fixed before data are analysed so conclusions are objective.
- [NIST/SEMATECH, selecting an experimental design](https://www.itl.nist.gov/div898/handbook/pri/section3/pri33.htm) - factor count and experimental objective determine an appropriate factorial or screening design.
- [scikit-learn permutation importance](https://scikit-learn.org/stable/modules/permutation_importance.html) - held-out permutation importance describes reliance of one fitted model; it is not intrinsic feature value and can be misleading with correlated features.
- [Hemming and Taljaard, cluster randomized trial design](https://pmc.ncbi.nlm.nih.gov/articles/PMC10555937/) - inference and analysis must respect the cluster-level experimental unit, including small-cluster corrections.
- [Cochrane Handbook, variants on randomized trials](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-23) - analysis must match non-standard designs such as cluster and crossover trials.
- [NIST/SEMATECH, CUSUM control charts](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm) - cumulative sums provide a change signal, not a physical cause label.

**Methodological Relevance:** A conventional feature permutation would destroy correlated temporal context and can create impossible electrical histories. This protocol instead applies deterministic runtime ablations to the exact same frozen counterfactual pair. NIST design principles support prespecifying factors and limiting interactions. Paired analysis removes pair-shared context; meter-day clustering prevents high-frequency rows or multiple windows from becoming false replicates. The result supports only component dependence of this fixed decision path on the sealed target-domain counterfactual corpus.

**Risks:** Runtime components may be correlated, a component may be unavailable because a provenance gate fails, pair construction can leak labels or calendar context, and an altered active-component set can change the meaning of an operational action. A null ablation is not proof of non-causality or physical irrelevance. A positive ablation is not proof that the component represents a real streetlight fault. Phase quantities must never be fabricated from incomplete channels, and CUSUM is never a cause classifier.

**Adopted Rules:**

1. Freeze source manifests, pair IDs, anomaly/benign allocation, eligibility, active-component set, thresholds, tie rules, and seeds before any v0.15 outcome is inspected.
2. Score Full H1 and every runtime-active ablation on the identical pair side with the identical frozen threshold. Do not recalibrate, retune, rescale, or select components after observing results.
3. Use `meter-day` as the cluster and counterfactual pair as the paired comparison stratum. Windows, readings, phases, and repeated runs inside a meter-day are descriptive observations, never independent replicas.
4. Evaluate singleton removals and only the two preregistered interactions `baseline x persistence` and `persistence x structural-change`; all other interactions are descriptive only.
5. Require the phase/baseline provenance gates before evaluating their components. A failed gate yields `NOT_EVALUABLE_GATE`, not an imputed score or a substitute feature.
6. Report `NOT_COMPARABLE_ACTION_SCALE` whenever Full H1 and an ablation do not expose the same eligible action scale. Do not turn that status into a zero effect, a pass, or a fail.
7. Interpret permutation diagnostics only as a secondary sensitivity check on held-out meter-day clusters; they cannot replace paired runtime ablation or establish causal necessity.
8. Preserve v0.10-v0.14 files and their results unchanged. This record is a pre-outcome design artifact and contains no v0.15 performance number.
