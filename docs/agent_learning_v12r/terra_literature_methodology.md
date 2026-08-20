# v0.12R Literature Evidence Methodology

**Role:** Subagent A, Literature Evidence Methodologist  
**Date:** 2026-08-21  
**Frozen protocol:** [v12r_literature_search_protocol.md](../../lightguard_v0_1/reports/v12r/v12r_literature_search_protocol.md)  
**Companion log:** [v12r_literature_search_log_terra.csv](../../lightguard_v0_1/reports/v12r/v12r_literature_search_log_terra.csv)

## Scope and rules of inference

This review answers the frozen v0.12R questions. I did not read, rank, filter,
or use an H1 score, proxy score, canonical membership, human rating, v0.11
result, or raw AMI value. The literature appraisal is independent of detector
outcomes.

An anomaly sign is a measured departure from an explicit reference state. A
fault is an operationally verified failure. These are not interchangeable. No
source supplies a LightGuard fault probability or converts an unlinked AMI
record into a Suyeong-gu lighting-asset label.

The fixed protocol query families were searched on 2026-08-21 in publisher/full
text, arXiv, IEEE/Digital Bibliography metadata, and NIST. The CSV records every
query, included source, excluded source, access limit, and reason. Core support
needed a recoverable target, measurement, anomaly or label definition, and
method. Quality A means peer-reviewed or government primary evidence, B means
an official technical publication with inspectable method, and C is discovery
support only. L3 is direct street-light current/expected-state support, L2 is
electrical/AMI support from another outcome, L1 is general evaluation or
measurement support, and L0 is no usable support.

## Starting reference appraisal

### S1. Calamaro, Beck, Ben Melech, and Shmilovitz, 2021

**Verified record.** *An Energy-Fraud Detection-System Capable of Distinguishing
Frauds from Other Energy Flow Anomalies in an Urban Environment*, Sustainability
13(19), 10696, DOI [10.3390/su131910696](https://doi.org/10.3390/su131910696).
The primary full text identifies Netzah Calamaro, Yuval Beck, Ran Ben Melech,
and Doron Shmilovitz and publication on 2021-09-26.

**Research logic.** The target is electricity-fraud screening in a local DSO,
not lighting failure. Fraud is energy hidden from a meter. The paper explicitly
distinguishes data-chain mismatch, preventive-maintenance anomalies, cyber
events, PV, and altered customer cycles as non-fraud alternatives. It describes
an anonymous locally tagged training set, a 200-meter DSO test set whose
suspects were field-tested, and field emulations of magnetic tampering, phase
disconnect, and phase reversal. The design derives 256 load-profile features,
filters by correlation, applies PCA/high-dimensional signatures, compares
classical classifiers, and adds 10% Gaussian noise to verified fraud data until
about 200 fraud meters. Metrics include confusion matrices, accuracy, precision,
and F1.

**Methodological judgement.** Root-cause separation plus field validation is
internally reasonable. Selected-model performance is not portable: matrices are
small, selected trials and synthetic augmentation are used, and the accessible
paper does not prove a leakage-safe meter/time-disjoint holdout for every
result. Grade A, L2. LightGuard may transfer the alternative-root and
data-quality workflow, never fraud labels, accuracy/F1, augmentation, or
thresholds. Schedule, dimming, photoperiod, and AMI transport failures can
mimic a persistent load departure.

### S2. Si et al., 2024, TimeSeriesBench

**Verified record.** Haotian Si, Jianhui Li, Changhua Pei, Hang Cui, Jingwen
Yang, Yongqian Sun, Shenglin Zhang, Jingjing Li, Haiming Zhang, Jing Han, Dan
Pei, and Gaogang Xie, *TimeSeriesBench: An Industrial-Grade Benchmark for Time
Series Anomaly Detection Models*, ISSRE 2024, 61-72, DOI
[10.1109/ISSRE62328.2024.00017](https://doi.org/10.1109/ISSRE62328.2024.00017);
primary manuscript [arXiv:2402.10802](https://arxiv.org/abs/2402.10802).

**Research logic.** The target is industrial/online TSAD, principally service
metrics. An anomaly is a point or sequence departing from customary patterns,
not a root cause. The benchmark combines labeled real-world data, synthetic
data, and an industrial set annotated with business experts. It compares over
168 settings spanning per-series, all-in-one, and zero-shot/new-curve learning.
Metrics include F1, AUPRC, event-oriented measures, and latency constraints. It
demonstrates that point adjustment can inflate scores for long events.

**Methodological judgement.** Unseen-curve and all-in-one settings are
reasonable generalization stress tests; event/latency measures are better alert
measures than single point F1. It remains a benchmark, not field-intervention
evidence. Grade A, L1. LightGuard may require time-forward meter-disjoint
evaluation after labels exist, event-level reporting, and inspection latency.
It cannot support a present fault-precision claim. New meter profiles, control
programs, and threshold tuning on an evaluation period remain failure modes.

### S3. Wu and Keogh, 2020/2023

**Verified record.** Renjie Wu and Eamonn J. Keogh, *Current Time Series Anomaly
Detection Benchmarks are Flawed and are Creating the Illusion of Progress*, IEEE
Transactions on Knowledge and Data Engineering 35(3), 2421-2429 (2023), DOI
[10.1109/TKDE.2021.3112126](https://doi.org/10.1109/TKDE.2021.3112126). Primary
preprint: [arXiv:2009.13807](https://arxiv.org/abs/2009.13807), 2020. The ICDE
2022 extended abstract DOI is
[10.1109/ICDE53745.2022.00116](https://doi.org/10.1109/ICDE53745.2022.00116).

**Research logic and judgement.** This benchmark audit identifies triviality,
unrealistic anomaly density, mislabeled ground truth, and run-to-failure bias,
then offers the UCR archive. It is a valid warning that label construction or
event placement can make high F1 non-operational; it does not invalidate every
benchmark. Grade A, L1. LightGuard must seal origin-level splits before joins,
preserve label provenance, and keep injected signals separate from field-fault
evaluation. Scenario leakage, origin duplication, and blind packet text that
reveals stratum/detector source are failure modes.

### S4. Croarkin, 2003, NIST measurement-process characterization

**Verified record.** C. M. Croarkin, *NIST/SEMATECH Engineering Statistics
Handbook, Chapter 2: Measurement Process Characterization* (NIST, 2003, updated
2017), [NIST record](https://www.nist.gov/publications/nistsematech-engineering-statistics-handbook-chapter-2-measurement-process)
and [chapter](https://www.itl.nist.gov/div898/handbook/mpc/mpc.htm). The NIST
record assigns no DOI.

**Research logic and judgement.** This government method covers reference
bases/check standards, bias, repeatability, reproducibility, stability,
calibration, gauge R&R, Type A/Type B uncertainty, and error budgets. It is
internally foundational but does not define AMI anomalies. Grade A, L1.
LightGuard must retain meter identity, phase availability, sampling, missingness,
clock alignment, channel scale, and drift. An unexplained current departure
cannot be attributed to an asset fault without a measurement/uncertainty
boundary.

## Added primary smart-meter/load-profile evidence

### S5. Śmiałkowski and Czyżewski, 2022

**Verified record.** Tomasz Śmiałkowski and Andrzej Czyżewski, *Detection of
Anomalies in the Operation of a Road Lighting System Based on Data from Smart
Electricity Meters*, Energies 15(24), 9438 (2022), DOI
[10.3390/en15249438](https://doi.org/10.3390/en15249438).

**Research logic.** This direct road-lighting deployment has more than 4,200
wirelessly managed LED lamps, 80 three-phase cabinet meters, 60-second sampling,
and 48 million records. Measurements are per-phase voltage, current, active and
apparent power, and power factor. The target includes lamp failures, schedule
deviations, and energy theft. SARIMA and LSTM forecast expected behavior for
online candidate screening.

**Methodological judgement.** This is reasonable cabinet-level anomaly screening
because the physical lighting system, control context, and per-phase measures
are known. It does not prove a forecast error is a lamp failure, and cabinets
serve many lamps. Grade A, L3. LightGuard may call an expected-state/current
mismatch an inspection candidate only with verified controller/twilight input,
cabinet-line mapping, phase layout, and AMI provenance. It cannot justify
individual asset attribution without that topology. Dimming, planned overrides,
seasonal photoperiod, and meter granularity are failure modes.

### S6. Śmiałkowski et al., 2025

**Verified record.** Tomasz Śmiałkowski and colleagues, *Anomaly detection in
urban lighting systems using autoencoder and transformer algorithms*, Scientific
Reports (2025), DOI
[10.1038/s41598-025-19414-8](https://doi.org/10.1038/s41598-025-19414-8).

**Research logic and judgement.** Cabinet smart-meter power is analysed with an
LSTM autoencoder, transformer, and energy-comparison baseline. The design uses
rolling normal-history training, prediction/reconstruction-error thresholds,
ROC/PRC choices, and confusion-matrix metrics. It explicitly restarts training
after an anomaly to avoid contaminating the baseline and states that
multi-anomaly sequences were not studied. Frozen baseline and contamination
control are reasonable. Grade A, L3. Its F1 cannot transfer from the local
installation, threshold-selection data, and single-anomaly tests. LightGuard may
use the logic for a frozen proxy-sign experiment, not a fault-accuracy claim.

### S7. Buzau et al., 2019

**Verified record.** Madalina-Mihaela Buzau, Javier Tejedor-Aguilera, Pedro
Cruz-Romero, and Antonio Gómez-Expósito, *Detection of Non-Technical Losses
Using Smart Meter Data and Supervised Learning*, IEEE Transactions on Smart Grid
10(3), 2661-2670 (2019), DOI
[10.1109/TSG.2018.2807925](https://doi.org/10.1109/TSG.2018.2807925).

**Research logic and judgement.** This non-technical-loss model combines energy,
alarms, electrical magnitudes, geographic/technological metadata, and about
57,000 Endesa on-field inspection outcomes. It trains, validates, and tests
classifiers, with extreme gradient boosted trees the best reported comparator.
Using inspection outcomes as external labels is reasonable. Grade A, L2. It
supports the requirement for timestamped work-order/inspection outcomes joined
to asset and meter before Gold/Silver claims. Theft class balance, thresholds,
and performance do not transfer; inspection-selection bias is a failure mode.

### S8. Jokar, Arianpoo, and Leung, 2016

**Verified record.** Paria Jokar, Nasim Arianpoo, and Victor C. M. Leung,
*Electricity Theft Detection in AMI Using Customers' Consumption Patterns*, IEEE
Transactions on Smart Grid 7(1), 216-226 (2016), DOI
[10.1109/TSG.2015.2425222](https://doi.org/10.1109/TSG.2015.2425222).

**Research logic and judgement.** The target is theft, using
normal/malicious-customer predictability and distribution-transformer meters to
shortlist areas. A meter-relative baseline is reasonable when meter identity,
stability, and outcome definition are known. Grade A, L2. Only the narrow
per-meter, time-of-day/seasonal reference transfers. A high/low lighting load is
not a failed lamp; unobserved control logic and load changes confound it.

### S9. Singh and Gill, 2018

**Verified record.** Dheerendra Singh and Sukhpal Singh Gill, *Entropy-based
electricity theft detection in AMI network*, IET Cyber-Physical Systems: Theory
& Applications 3(2), 76-84 (2018), DOI
[10.1049/iet-cps.2017.0063](https://doi.org/10.1049/iet-cps.2017.0063).

**Research logic and judgement.** Relative-entropy distances between adjacent
consumption steps are thresholded from history and evaluated on 5,000 consumers.
The paper flags appliance, season, and resident changes as non-malicious
false-positive causes. The mechanism is plausible as a signal detector, not as
a portable theft/fault label. Grade A, L2. It supports explicit seasonal and
operational alternatives and prohibits treating persistence/entropy alone as a
confirmed fault.

### S10. Ayaz et al., 2017

**Verified record.** Murat Ayaz, Koray Erhan, İ. Malik Kundakci, and H. Metin
Ertunc, *Automation System Design for Fault Detection in Street Lighting*, The
Eurasia Proceedings of Science Technology Engineering and Mathematics 1,
111-115 (2017), [authoritative record](https://dergipark.org.tr/en/pub/epstem/article/364353).
The journal supplies no DOI.

**Research logic and judgement.** Transformer-center line currents, known
columns-per-line, and equivalent resistance estimate faulty counts and spatial
groups. The accessible article record does not show a blinded field-outcome
trial or enough performance detail for an accuracy claim. Its aggregation logic
is conditionally reasonable. Grade B, L3. It supports cabinet/line group
prioritization only with authoritative cabinet-line-asset mapping and component
characteristics. It cannot infer an individual light from an unlinked meter.
LED dimming, mixed loads, bypasses, and wrong counts break the inference.

### S11. Lee and Huang, 2015

**Verified record.** Huang-Chen Lee and Huang-Bin Huang, *A Low-Cost and
Noninvasive System for the Measurement and Detection of Faulty Streetlights*,
IEEE Transactions on Instrumentation and Measurement 64(4), 1019-1031 (2015),
DOI [10.1109/TIM.2014.2361551](https://doi.org/10.1109/TIM.2014.2361551).

**Research logic and judgement.** Instead of inferring condition from electrical
load, this proof of concept uses vehicle-mounted light meters and GPS to compare
illumination maps. The closer service-outcome measurement and complementary
inspection role are reasonable. Grade A, L3. An AMI candidate needs independent
field, optical, or controller confirmation before it can be named an outage.
Weather, adjacent luminaires, GPS/path, and calibration still prevent optical
screening alone from being a Gold label without an inspection protocol.

## Synthesis: what transfers and what does not

| Review question | Supported limited claim | Prohibited claim |
| --- | --- | --- |
| Persistent meter-relative departure | Stable per-meter references can create a proxy anomaly sign. | Confirmed luminaire fault or fault probability. |
| Expected-state/current mismatch | Candidate signal only with independently evidenced controller/twilight state. | Daytime-on from astronomical time alone. |
| Phase-selective departure | Cabinet/line sign when phase topology is verified. | Which pole/lamp failed from imbalance alone. |
| Required validation | External work order, inspection, optical, or controller evidence supplies labels. | Labels made by detector, injection, or unblinded review. |
| Evaluation limits | Report proxy concordance/enrichment and limitations. | FPR, recall, accuracy, or generalization without linked Gold/Silver outcomes. |

The combined method is conditionally reasonable for Route C proxy-sign
triangulation only if outputs remain named proxy anomaly sign or inspection
candidate; meter/phase/time/baseline/missingness/seal provenance is retained;
expected-state claims use actual controller/light-input evidence; topology is
authoritative before spatial attribution; calibration/evaluation is
time-forward and origin-disjoint; controls are detector-independent; and Gold
or Silver labels precede any operational accuracy claim.

The method is not sufficient to validate an individual Suyeong-gu streetlight
fault now. The missing evidence is a timestamped, auditable join among AMI
meter, cabinet/line/asset, controller state, and field inspection/work-order
outcome. Literature cannot fill that join.

## Included, excluded, and stopping

S1-S11 are included: six peer-reviewed direct streetlight/AMI sources
(S1, S5-S9, S11), one topology source (S10), two benchmark sources (S2-S3), and
one government measurement source (S4). This exceeds the protocol target
without importing weak matches. The log excludes simulated-current studies,
opaque datasets, synthetic-attack-centered studies, and generic IoT prototypes
that lack recoverable labels or leakage-safe evaluation. Search stops because
all five review questions have L3 evidence, counterexamples, external-label
methodology, benchmark-validity guidance, and a measurement framework.

## Primary and authoritative sources

1. [Calamaro et al., 2021](https://www.mdpi.com/2071-1050/13/19/10696)
2. [Si et al., 2024](https://arxiv.org/abs/2402.10802)
3. [Wu and Keogh, 2020](https://arxiv.org/abs/2009.13807)
4. [NIST measurement process characterization](https://www.nist.gov/publications/nistsematech-engineering-statistics-handbook-chapter-2-measurement-process)
5. [Śmiałkowski and Czyżewski, 2022](https://www.mdpi.com/1996-1073/15/24/9438)
6. [Śmiałkowski et al., 2025](https://www.nature.com/articles/s41598-025-19414-8)
7. [Buzau et al., 2019](https://doi.org/10.1109/TSG.2018.2807925)
8. [Jokar et al., 2016](https://doi.org/10.1109/TSG.2015.2425222)
9. [Singh and Gill, 2018](https://doi.org/10.1049/iet-cps.2017.0063)
10. [Ayaz et al., 2017](https://dergipark.org.tr/en/pub/epstem/article/364353)
11. [Lee and Huang, 2015](https://doi.org/10.1109/TIM.2014.2361551)

