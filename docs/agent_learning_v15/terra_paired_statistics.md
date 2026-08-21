# TERRA B v0.15 paired statistics learning record

## Role

TERRA B paired-statistics analyst. This record fixes the analysis rules before
any v0.15 holdout outcome, score, pair count, or ablation result is accessed.

## Actual Model

GPT-5 Codex (TERRA B role).

## Sources Reviewed

1. McNemar, Q. (1947). Note on the sampling error of the difference between
   correlated proportions or percentages. *Psychometrika*, 12, 153-157.
   https://doi.org/10.1007/BF02295996
2. Newcombe, R. G. (1998). Improved confidence intervals for the difference
   between binomial proportions based on paired data. *Statistics in Medicine*,
   17, 2635-2650. https://doi.org/10.1002/(SICI)1097-0258(19981130)17:22%3C2635::AID-SIM954%3E3.0.CO;2-C
3. Holm, S. (1979). A simple sequentially rejective multiple test procedure.
   *Scandinavian Journal of Statistics*, 6, 65-70.
   https://doi.org/10.2307/4615733
4. Hoffmann, D., et al. (2020). ClusterBootstrap: analysis of hierarchical data
   using generalized linear models with the cluster bootstrap. *Journal of
   Statistical Software*, 95. https://doi.org/10.18637/jss.v095.i01
5. Neuhaus, J. M. (2001). Assessing change with longitudinal and clustered
   binary data. *Annual Review of Public Health*, 22, 115-128.
   https://doi.org/10.1146/annurev.publhealth.22.1.115
6. Westfall, P. H., et al. (2011). *Multiple Comparisons and Multiple Tests*
   (2nd ed.). SAS Institute. Holm's sequential procedure is used because the
   confirmatory family is finite and fixed before outcomes.

## Methodological Relevance

- Full H1 and each ablation produce paired binary actions on exactly the same
  counterfactual pair. McNemar's conditional exact test therefore targets a
  directional imbalance among discordant actions, rather than treating the two
  detectors as independent samples.
- The estimand must remain an absolute paired action-probability difference,
  not an unpaired relative metric. Newcombe's paired-binomial work motivates
  reporting a risk difference and confidence interval alongside the exact test.
- Multiple meter-days from the same meter are repeated observations. The
  pair-level exact test alone does not remove meter clustering; a meter-nested
  cluster bootstrap is required for uncertainty and stability reporting.
- Holm correction controls the family-wise error rate for the predeclared
  component ablations without selecting a favourable subset after outcomes.

## Risks

- A meter-day is the primary experimental cluster, but five target meters may
  leave few top-level clusters. Bootstrap intervals can be wide or unstable;
  they are evidence of uncertainty, not a license to replace the frozen test.
- McNemar's exact conditional calculation assumes exchangeability of
  discordant pairs. Repeated meter observations can weaken that assumption, so
  its Holm-adjusted p-value is never sufficient by itself for a necessity
  claim.
- An ablation can change the score scale. Same-threshold action comparison is
  then still operationally relevant, but must be marked
  `NOT_COMPARABLE_ACTION_SCALE` if the frozen action mapping cannot be applied
  without a structural scale break. Threshold retuning is prohibited.
- Counterfactual benign perturbations are labelled controls, not naturally
  observed normal ground truth. Their escalation rate is not a real-background
  FPR, specificity, or field-fault metric.
- Missing runs, failed pair construction, and unavailable runtime evidence can
  induce selection bias. They must be reported by assigned operator, meter,
  and variant; no post-outcome exclusion or reassignment is permitted.

## Adopted Rules

1. Freeze the complete analysis population, operator allocation, detector
   variants, frozen threshold, bootstrap seed, and comparison families before
   opening any outcome file.
2. Use one assigned counterfactual pair per eligible meter-day in the primary
   analysis. Rows, windows, events, and multiple grafts within a meter-day are
   never additional primary observations.
3. Use two-sided exact McNemar tests for paired binary action endpoints, with
   the full H1 action as the first member of every pair.
4. Report paired risk differences with the sign `Full H1 - comparator` and
   meter-nested cluster-bootstrap 95% percentile intervals. Preserve each
   pair's two detector outcomes during resampling.
5. Treat an effect as statistically supported only when its predeclared
   Holm-adjusted exact p-value is below 0.05, the matching cluster-bootstrap
   interval excludes zero in the prespecified direction, and the direction is
   not contradicted by a meter stratum with adequate assigned pairs.
6. Apply Holm separately to the five primary component-ablation recovery
   hypotheses and separately to the five primary component-ablation controlled
   benign-escalation hypotheses. The Z1 comparator, mechanism-only variants,
   interactions, score endpoints, and strata are descriptive or secondary and
   receive no confirmatory necessity claim.
7. Report every frozen ablation, every assigned operator, every meter stratum,
   and all exclusions. Do not choose pairs, operators, variants, directions, or
   confidence intervals after inspecting results.

