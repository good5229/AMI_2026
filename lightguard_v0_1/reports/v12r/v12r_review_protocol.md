# v0.12R Blinded Human Review Protocol

Pre-registered before literature screening and before any human label.

## Primary question

Do literature-supported and algorithm-convergent trace strata receive higher blinded human anomaly-sign ratings than fixed-hash matched background?

This is not a fault-accuracy or prevalence study.

## Packet strata

- S1: every available H1 + Proxy High case with Literature A/B.
- S2: up to 18 Proxy High + Literature A/B + H1-negative cases.
- S3: up to 18 Proxy singleton/medium + Literature B/C cases.
- S4: up to 20 detector-independent meter/month/time-slot matched background cases.

Shortfalls remain shortfalls. Cases are never fabricated or relabeled to fill a stratum. Selection seed and IDs are frozen before review; post-label replacement is prohibited.

## Blinding

Hide stratum, H1 action, all proxy flags/scores, Literature Grade, canonical-six membership, rank, and candidate label. Show only anonymized meter alias, relative time, I1/I2/I3 trace, past-only local baseline band, missingness, and a uniform event window.

## Reviewers and labels

- Minimum 2 human reviewers; preferred 3.
- Agents may prepare packets and analysis code but may not enter labels.
- Labels: `STRONG_ANOMALY_SIGN`, `POSSIBLE_ANOMALY_SIGN`, `LOW_CONCERN`, `INSUFFICIENT_DATA`.
- Confidence: integer 1 through 5.
- Reasons: unexpected_level, unexpected_duration, phase_pattern, abrupt_change, baseline_deviation, data_quality, unclear, other.

An expert-reviewed anomaly sign is not a confirmed fault.

## Frozen analysis

- Ordinal coding: insufficient excluded from ordinal contrast but reported as missing/indeterminate; low=0, possible=1, strong=2.
- Review-positive: possible or strong.
- Two reviewers: quadratic-weighted Cohen kappa plus raw percent agreement.
- Three or more reviewers: multi-rater ordinal agreement selected and documented before import.
- Primary contrast: S1+S2 versus S4 using a fixed-seed label permutation at case level.
- Report review-positive rate, ordinal median, effect size, exact/permutation p-value, and case-cluster bootstrap 95% interval.
- Secondary contrasts: Literature A/B versus C, H1-positive versus H1-negative, Proxy High versus lower evidence.

The packet is purposefully enriched and cannot estimate population prevalence.

## Status policy

Until real reviewers submit schema-valid files:

- `PHASE_A_LITERATURE_COMPLETE`
- `PHASE_B_REVIEW_READY`
- `HUMAN_REVIEW_PENDING`

No human concordance, kappa, T3 classification, or Level-4 claim is emitted before review results are sealed.
