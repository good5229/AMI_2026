# v0.6 Academic Basis and Gap Closure Plan

## Applied basis

- Hyndman and Athanasopoulos, time-series cross-validation: training observations must precede each rolling origin. https://otexts.com/fpp3/tscv.html
- Politis and Romano, stationary bootstrap: dependent stationary observations require dependence-preserving resampling for uncertainty. https://doi.org/10.1080/01621459.1994.10476870
- Wilson, score interval: a point estimate such as 6/6 must retain small-sample uncertainty. https://doi.org/10.1080/01621459.1927.10502953
- Kim et al., rigorous TAD evaluation: point-adjustment can overstate anomaly performance, so this project uses event overlap without point-adjusted recall. https://doi.org/10.1609/AAAI.V36I7.20680
- Goswami et al., unlabeled model selection: synthetic injection is a surrogate when labels are scarce, not a substitute for field truth. https://openreview.net/forum?id=gOZ_pKANaPW
- NIST factorial effects: two-factor effects should be measured explicitly rather than inferred from OAT neighbors. https://www.itl.nist.gov/div898/handbook/pri/section5/pri597.htm
- NIST information quality policy: quantitative results should carry uncertainty and reproducibility evidence. https://www.nist.gov/director/nist-information-quality-standards

## Closure decisions

- Candidate coverage receives Wilson 95% intervals and is never renamed recall.
- Daily candidate density receives a deterministic stationary-bootstrap interval with meter-local ordering preserved.
- A 2^4 factorial diagnostic measures main and two-factor effects at frozen weights x 0.9/1.1; no run selects a new configuration.
- Known failure envelopes produce an explicit abstention instead of interpolation or a normal classification.
- Field accuracy remains unavailable until blinded inspections populate the versioned outcome schema.
