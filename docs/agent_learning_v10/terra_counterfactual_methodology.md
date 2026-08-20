# v0.10 real-background counterfactual methodology learning note

## Provenance and scope

- Requested model: `terra`.
- Actual runtime model: GPT-5/Codex. `terra` was not selectable in this session.
- Sources read: 2026-08-20, Asia/Seoul.
- Permitted local evidence: `lightguard_v0_1/data/validation/v10/v10_raw_ami_manifest.json` and the frozen v0.9 design/freeze contracts only. No detector scores, labels, configuration, outcomes, raw workbooks, or external context were inspected.

The raw manifest fixes five anonymized B-line meters (`B-L-9`, `B-L-12`, `B-L-13`, `B-L-14`, `B-L-35`) from 2026-04-01 through 2026-06-30 at a nominal 15-minute cadence. It establishes native current channels and prohibits energy reconstruction. It does not provide field-fault labels. Accordingly, v0.10 can estimate response to stipulated current perturbations on these recorded backgrounds, not normal-versus-fault accuracy in the field.

## What the sources require of this protocol

| Source | Methodological consequence frozen for v0.10 |
| --- | --- |
| Carmona et al., [NCAD](https://arxiv.org/abs/2107.07702) (2021) | Synthetic anomaly injection can supply a controlled anomaly class when labels are absent, but its label is the injection definition, not a discovered field-fault truth. |
| Si et al., [TimeSeriesBench](https://arxiv.org/abs/2402.10802) (2024) | Evaluation must represent deployment constraints, unseen conditions, event latency, and false alerts; point-adjustment can distort event scoring. |
| Wu and Keogh, [Current Time Series Anomaly Detection Benchmarks are Flawed](https://arxiv.org/abs/2009.13807) (2020) | Benchmark artifacts can create illusory gains; background selection, labels, and scoring must be fixed before outcomes. |
| NIST/SEMATECH, [Measurement Process Characterization](https://www.itl.nist.gov/div898/handbook/mpc/section1/mpc1.htm) | Separate the measurement process, reference base, bias/accuracy, and variability. An injected series is a measurement counterfactual, not a calibrated physical truth. |
| NIST/SEMATECH, [Autocorrelation](https://www.itl.nist.gov/div898/handbook/eda/section3/eda35c.htm) | Equally spaced time-series observations can be autocorrelated; interval rows are not automatically independent replicates. |
| NIST/SEMATECH, [Autocorrelation Plot](https://www.itl.nist.gov/div898/handbook/eda/section3/autocopl.htm) | Randomness is an assumption behind ordinary uncertainty calculations, not something to presume from many timestamps. |
| NIST/SEMATECH, [Analysis of paired observations](https://www.itl.nist.gov/div898/handbook/prc/section3/prc311.htm) | Compare each treated series with its naturally matched original through within-background differences, then quantify uncertainty over independent sampling units. |
| Zhang et al., [AURORA](https://pubmed.ncbi.nlm.nih.gov/34177356/) (2021) | Real time-series backgrounds can be retained while point or contextual perturbations are injected; the injection mechanism and positions must be explicit. |
| Goswami et al., [Unsupervised Model Selection for Time-series Anomaly Detection](https://arxiv.org/abs/2210.01078) (2023) | Performance on injected anomalies is a surrogate for model selection, not a substitute for labelled field validation; it must not by itself authorize deployment claims. |
| Kim et al., [Towards a Rigorous Evaluation of Time-series Anomaly Detection](https://arxiv.org/abs/2109.05257) (2021) | Do not use lenient point adjustment as the primary result; define event timing and score the stipulated window directly. |

## Consequences

1. The preserved raw meter-day is the experimental context. No synthetic seasonal, meteorological, astronomical, municipal, or load context is added.
2. The paired unmodified meter-day is a counterfactual reference only. It is explicitly not labelled normal, safe, fault-free, negative, or a false-positive denominator.
3. The injection label applies only to the exact modified current interval. It is not evidence that the corresponding physical fault occurred in the source data.
4. A meter-day, not a 15-minute row, is the basic paired replicate. Meter is the top-level dependence cluster.
5. Event detection, latency, paired alert contrast, and post-event recovery are all defined before any detector output is read. No point adjustment, threshold tuning, or gate revision is allowed after outcomes.

## Frozen design constants

The complete constants, operator equations, eligibility, analysis, and transport gate are frozen in [v10_counterfactual_protocol.md](/Users/bellhundred/git-repo/AMI_2026/lightguard_v0_1/reports/v10/v10_counterfactual_protocol.md). The essential constants are:

| Constant | Value |
| --- | --- |
| Background unit | one meter-local calendar day: 96 contiguous 15-minute interval-end rows |
| Eligible meters | the five meter IDs fixed by the raw v0.10 manifest |
| Preamble / injection / recovery | 32 / 32 / 32 intervals (8 hours each) |
| Hash namespace | `LG-v10-CF-20260820` using SHA-256 |
| Operator set | common-mode uplift 1.50, common-mode attenuation 0.50, deterministic single-phase attenuation 0.10, deterministic held-current sensor state |
| Event detection deadline | first four injected intervals (one hour) |
| Recovery criterion | first four consecutive non-alert intervals after restoration; 32-interval censoring horizon |
| Uncertainty | 10,000 replicate hierarchical meter-then-background cluster bootstrap, seed `20261020`; leave-one-meter-out sensitivity |
| Field transport status | `BLOCKED` regardless of detector outcome |

## Explicit prohibitions

The following are protocol violations: treating unmodified as normal truth; H1-dependent background selection; energy reconstruction; municipal/KMA/KASI joins; post-outcome gate changes; tuning an operator, its severity, selection, or recovery definition after detector outcomes; and converting injected-response results into field sensitivity, specificity, accuracy, reliability, or fault-prevalence claims.
