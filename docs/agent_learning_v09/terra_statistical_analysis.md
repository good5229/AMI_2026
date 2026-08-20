# TERRA v0.9 statistical analysis learning note

## Scope and decision

This work treats v0.9 as a frozen, controlled, episode-separated confirmatory analysis. The selected candidate is `H1`; the frozen configuration SHA-256 is `b536f8ca68222662c717cd27a6af4c3c64a3330782b0545503df6e4aff3e6232`. No result here is field AMI accuracy, a fault-truth assertion, or a basis for post-holdout retuning.

The appropriate dependence unit is the episode, not a synthetic case: multiple cases share an official date, regional/seasonal context, and episode-level construction. Accordingly, the bootstrap samples entire confirmatory episodes with replacement (24 draws per resample), using 2,000 resamples and fixed seed `20260901`.

## Applied research guidance

- [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/) supports repository-local, legible artifacts and mechanical invariants. This analysis therefore validates the frozen SHA, selection, scenario counts, source boundary, and decision coverage before writing a report.
- [Introducing the Codex app](https://openai.com/index/introducing-the-codex-app/) and [OpenAI Codex](https://openai.com/codex/) inform the use of explicit artifacts and auditable task boundaries rather than unstated state.
- [GitHub agent instructions](https://github.com/github/awesome-copilot/blob/main/instructions/agents.instructions.md) describes constrained tool access, explicit inputs/outputs, and sequential dependency checks. The scripts only read the frozen inputs and write their named reports.
- [NIST confidence-interval guidance](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm) informs reporting binomial uncertainty. Wilson 95% intervals are included whenever a subgroup has the required denominator; undefined denominators are intentionally blank rather than fabricated.
- [NIST bootstrap reference](https://www.itl.nist.gov/div898/handbook/eda/section3/eda366.htm) supports resampling to characterize sampling variation. The implementation states the resampling unit, repetition count, seed, and percentile interval rule.
- [scikit-learn grouped validation guidance](https://scikit-learn.org/stable/modules/cross_validation.html) explains why dependent groups must not be split as if samples were independent. The v0.9 calibration/holdout split and the analysis bootstrap preserve episode grouping.

Sources were consulted on 2026-08-20. Statistical references guide uncertainty reporting only; they do not turn controlled scenarios into real-world AMI evidence.

## Reporting policy carried into v0.9

- Report normal FPR and hard-negative FPR separately; a low aggregate FPR can conceal a problem family.
- Stratify solar evidence by the exact fixed bins `0-15`, `15-30`, `30-60`, `60-120`, and `>120` minutes, retaining sunrise/sunset side.
- Keep feature availability explicit as `full`, `load_missing`, `phase_missing`, or `both_missing`; no rated-load imputation is permitted.
- Treat region, season, weather regime, episode, and region-season rows as descriptive effects. Weather remains context-only and has weight `0.0` in the frozen configuration.
- Compare H1/H2/H3 with `threshold_only` through frozen decision rows. No bootstrap result may select a different candidate or alter a threshold.
