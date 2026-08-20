# TERRA A: External Dataset Methodology

## Role

TERRA A External Dataset Methodologist for v0.13. The assignment is to qualify external datasets for electrical anomaly-mechanism transfer only. It does not establish streetlight field accuracy, a streetlight-fault label, or a fault probability. This revision reconciles the pre-confirmatory gates using frozen source facts supplied by the main agent; no test labels were accessed.

## Actual Model

GPT-5 Codex, operating under the TERRA A assignment.

## Sources Reviewed

1. [MAD repository](https://github.com/IISGLab/MeteringAnomalyDiagnosis), including its README and `LICENSE` file.
2. Sun et al., [Few-Shot Metering Anomaly Diagnosis with Variable Relation Mining](https://doi.org/10.3390/en17050993), *Energies* 2024, 17, 993. This is an author-associated primary paper, but it reports a data version that differs from the current MAD repository.
3. University of Strathclyde, [Annotated load anomalies from the REFIT Dataset](https://pureportal.strath.ac.uk/en/datasets/annotated-load-anomalies-from-the-refit-dataset/), DOI [10.15129/9729a2a0-11ce-4cce-b0d0-144c483fcb33](https://doi.org/10.15129/9729a2a0-11ce-4cce-b0d0-144c483fcb33).
4. Rashid et al., [Evaluation of non-intrusive load monitoring algorithms for appliance-level anomaly detection](https://ieeexplore.ieee.org/document/8683792/), ICASSP 2019. The University of Strathclyde record provides an accepted-manuscript link and the paper's scope; its PDF endpoint was access-restricted during this review.
5. UCR, [Time Series Anomaly Archive 2021 official download](https://www.cs.ucr.edu/~eamonn/time_series_data_2018/UCR_TimeSeriesAnomalyDatasets2021.zip), specifically `210`, `211`, and `212` Italianpowerdemand files.
6. Wu and Keogh, [Current Time Series Anomaly Detection Benchmarks are Flawed and are Creating the Illusion of Progress](https://doi.org/10.1109/TKDE.2021.3112126), *IEEE Transactions on Knowledge and Data Engineering*.
7. Zenodo, [Smart Meter Anomaly Detection Dataset Pseudo Labelled via Ensembled ML Models](https://doi.org/10.5281/zenodo.18670956).

The first four are the assigned original dataset/paper sources. Items 5-7 are additional authoritative official or primary sources. Main downloaded the official releases into ignored storage and supplied only release metadata; this review did not inspect `y_test` or run a metric.

## Dataset and Method Relevance

| Dataset | Evidence class | Quality grade | Mechanism relevance | Eligibility |
|---|---|---|---|---|
| MAD | Actual 3P4W AMI; field/manual or professional anomaly provenance is claimed by the repository | DG-A | Strong for multivariate voltage/current/power/power-factor and phase-current mechanism checks | Released only as narrowly qualified Track A: author-split, sample-level, binary `0` versus `1..6` confirmatory benchmark |
| REFIT annotated anomalies | Real, human-annotated appliance load anomalies from five homes | DG-B | Moderate for meter-relative baseline and persistence only | Secondary, gated on machine-readable label-rule verification and a pre-test split |
| UCR Anomaly Archive Italianpowerdemand | Curated anomaly intervals whose boundaries are encoded in official filenames | DG-C | Generic univariate temporal anomaly detection only | Optional secondary temporal stress test after explicit licence confirmation; excluded from electrical mechanism/fault metrics |
| Zenodo pseudo-labelled smart meters | Model-generated labels from XGBoost/LightGBM ensemble trained on a different dataset | DG-D | Can test pipeline behavior only | Excluded from Gold, professional-label, and confirmatory claims |

### MAD verification

The current repository README states: actual deployed AMI; 504 three-phase four-wire meters; 382 normal meters; 122 manually inspected on-site or professionally labelled anomalous meters; 30-minute cadence; 48 points per daily sample; 7,733 usable daily samples; and author-provided `x_train`, `y_train`, `x_test`, `y_test` partitions of 2,319 and 5,414 samples. It defines class `0` as normal and classes `1`-`6` only as `Abnormal-1` through `Abnormal-6`; the README does not define those six mechanisms.

The associated 2024 paper is not interchangeable with that package: it describes 15-minute cadence, 96 points/day, 7,421 retained samples, and six named classes (loss of voltage, loss of current, current unbalance, voltage unbalance, false connection, factor fault). It also reports 14 electrical variables: phase A/B/C voltage, phase A/B/C current, total and phase active power, and total and phase power factor. Those class names and counts must not be silently transferred to the 2025 repository package.

The repository contains `LICENSE`, verified as CC BY-ND 4.0. It permits sharing the unmodified licensed material with attribution but forbids sharing adapted material. Raw data and transformed feature datasets must remain outside Git. Source code and aggregate metrics need a separate compliance check before publication; this record is not legal advice.

The frozen current release is repository commit `a83de7ec7399d71c9eb81e0284fce0526b2b9887`; `MAD.npz` SHA-256 is `84dff6d73d671e29b4147fd49962a41a22ea9d6bcfadb205782971af4f86a497`; and the predeclared array shapes are `x_train [2319,14,48]` and `x_test [5414,14,48]`. These facts resolve the package identity and make a narrow author-split Track A reproducible without reading `y_test` in advance.

Track A is released with these fixed restrictions: binary target `0` versus opaque `1..6`; author-provided sample partitions only; no claim of meter-disjointness, temporal holdout, or individual-meter generalization; no class-mechanism analysis; no use of class names from the incompatible 2024 paper; and every metric prefixed `External MAD author-split sample-level`. This narrow result can test whether pre-frozen signal-level features discriminate the package's normal versus repository-labelled anomalous samples. It is sufficient for a qualified DG-A external metering benchmark, but not for causal mechanism confirmation across physical meters.

Track B remains `NOT_ASSESSABLE`: the release has no meter IDs, timestamps, split construction, or meter-to-day mapping, so a meter-disjoint split cannot be constructed or audited. No release DOI is present. The lack of Track B does not prohibit Track A when the scope is honestly sample-level and author-split.

### REFIT verification

The Strathclyde dataset record states that anomalies were obtained by sifting the REFIT data; labels are governed by the accompanying ICASSP 2019 paper; five of 20 houses (1, 10, 16, 18, 20) were selected for the most detected anomalies; the anomalies are real, not simulated; and the appliance groups are refrigerator, freezer, fridge-freezer, dishwasher, washing machine, tumble dryer, electrical heater, and microwave. The repository record licenses both the annotation README and `REFIT_anomalies.csv` as CC BY 4.0.

The paper is a supervised appliance-level anomaly-detection/NILM study based on real aggregate and submetered two-year REFIT measurements. It supports the relevance of baseline learning and persistent abnormal appliance behavior. It does not make the data a three-phase AMI or streetlight-fault dataset. The source page says the detailed rules are in the ICASSP paper, but the primary manuscript endpoint returned access restriction during review; exact operational label rules, annotation counts, and a prescribed train/test split are therefore unverified and must be frozen before use.

### UCR Anomaly Archive Italianpowerdemand verification

The relevant source is the UCR Time Series Anomaly Archive, not the 2018 classification archive. Its official 2021 archive includes `210_UCR_Anomaly_Italianpowerdemand`, `211_UCR_Anomaly_Italianpowerdemand`, and `212_UCR_Anomaly_Italianpowerdemand`; their filenames encode the train end and anomaly start/end. Main froze the official archive SHA-256 as `ac4b991c701e620ae9cc5ebd57ae45593a36cc9c0b6ed5e3c4b7e466cf4783d4` without exposing test values to this reviewer. The source is therefore a labeled anomaly benchmark, not a classification-label proxy.

It is DG-C because it is univariate and does not offer phase, meter, field-inspection, or electrical fault-cause evidence. The reviewed official archive and its paper do not state an explicit dataset licence, so licence remains `UNKNOWN`, not inferred from public access. It may become an optional secondary temporal stress test after explicit licence confirmation, using its provided train boundary and encoded anomaly interval; it is never eligible for phase/current, electrical-cause, streetlight, or fault-probability claims.

### Zenodo pseudo-label exclusion

The Zenodo record explicitly says its hourly readings from 74 smart meters are pseudo-labelled by an XGBoost/LightGBM ensemble trained on LEAD data from 200 buildings. Its DOI is [10.5281/zenodo.18670956](https://doi.org/10.5281/zenodo.18670956). The reviewed record does not supply a licence, so the licence is `UNKNOWN`; independently, model-generated labels make it DG-D. It is prohibited from external Gold/professional-label and confirmatory use.

## Risks

- A MAD repository/paper version mismatch can invalidate class names, sampling assumptions, counts, and split analysis; Track A avoids this by using only the frozen repository package and opaque labels.
- Daily samples from one physical MAD meter may cross partitions; Track A is intentionally sample-level and Track B remains NOT_ASSESSABLE.
- MAD labels are metering-anomaly labels, not maintenance-closed-loop, luminaire, cabinet, or streetlight-fault labels.
- REFIT captures domestic appliance behavior. It has no three-phase phase-current evidence and low streetlight operational similarity.
- UCR Anomaly Archive Italianpowerdemand has anomaly-interval labels, but it is generic univariate temporal ground truth rather than electrical mechanism or field-fault ground truth.
- Pseudo-labels assess agreement with their generating models, not independent field truth.
- A public download page is not a licence. `UNKNOWN` blocks inclusion until an explicit applicable licence is verified.

## Adopted Rules

1. Use `EXTERNAL_GOLD_OR_PROFESSIONAL_LABEL` only for a DG-A source and name the domain: `External MAD metering anomaly`, never `LightGuard` or streetlight fault accuracy.
2. Freeze the exact dataset release, checksum, label map, split, and permitted feature mapping before labels are evaluated.
3. Release MAD Track A only as `External MAD author-split sample-level binary 0-vs-1..6`; use the frozen commit, file SHA-256, and `[2319,14,48]`/`[5414,14,48]` shapes. Do not read test labels for tuning.
4. Keep MAD Track B `NOT_ASSESSABLE` until meter identifiers, timestamps, split construction, and meter-to-sample mapping permit a genuine meter-disjoint audit.
5. Use MAD's repository classes as opaque unless their release-specific class definition is verified. Do not borrow classes from the 2024 paper.
6. Use REFIT only for predeclared LG-S1 baseline-deviation and LG-S2 persistence checks after label-rule and split freezing; its raw source status is `BLOCKED_EXTERNAL_DATA`; do not test LG-S3 phase asymmetry on it.
7. Treat UCR Anomaly Archive Italianpowerdemand as optional DG-C temporal stress testing only after explicit licence verification; exclude it from electrical mechanism/fault metrics and all phase claims.
8. Exclude Zenodo pseudo-labels from all confirmatory, Gold, and professional-label analyses.
9. Never convert external mechanism discrimination into streetlight field accuracy, field recall, fault probability, or a Suyeong/Busan/Gangneung/Chungju claim.
