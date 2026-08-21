# v0.13 External Dataset Review: TERRA A

## Decision

MAD Track A is released for a narrowly qualified confirmatory run: fixed-repository, author-split, sample-level binary classification of normal `0` versus opaque repository-labelled `1..6`. It is a DG-A external metering benchmark only. Track B is `NOT_ASSESSABLE` because no meter IDs, timestamps, split construction, or meter-to-sample mapping exist for a meter-disjoint audit. REFIT remains a DG-B candidate but raw availability is `BLOCKED_EXTERNAL_DATA`. UCR Anomaly Archive Italianpowerdemand is DG-C optional temporal stress testing, gated by its still-unknown licence. Zenodo pseudo-labels remain excluded from confirmatory electrical anomaly claims.

This is a dataset-methodology gate, not an efficacy result. External electrical anomaly mechanism validity remains distinct from streetlight field accuracy and fault probability.

## Source findings

| Candidate | Primary source finding | Licence | Label provenance | Grade | Inclusion decision |
|---|---|---|---|---|---|
| MAD repository | Frozen commit `a83de7ec7399d71c9eb81e0284fce0526b2b9887`; 504 actual deployed 3P4W AMI meters; 382/122 provenance; 30-minute 48-point daily samples; 7,733 samples; `[2319,14,48]`/`[5414,14,48]` author arrays | CC BY-ND 4.0, verified from repository `LICENSE` | Repository claim: manual on-site inspection or skilled professional labels | DG-A | Included primary only for narrow Track A |
| MAD 2024 paper | 504 meters, 382/122; 15-minute, 96-point daily samples; 7,421 samples; named metering classes | Paper copyright is not dataset licence | Field/manual or skilled-expert labels reported | Supporting primary paper only | Cannot define current repository labels without release linkage |
| REFIT annotated | Five selected homes; real, non-simulated appliance anomalies; eight appliance groups | CC BY 4.0, explicit at official record | Human annotation rules delegated to ICASSP 2019 paper | DG-B | GATED secondary |
| UCR Anomaly Archive Italianpowerdemand | Frozen official 2021 archive SHA-256 `ac4b991c701e620ae9cc5ebd57ae45593a36cc9c0b6ed5e3c4b7e466cf4783d4`; files 210/211/212 encode train end and anomaly start/end | UNKNOWN | Official anomaly-interval labels, not classification labels | DG-C | Optional secondary temporal stress test only after licence confirmation |
| Zenodo pseudo-labelled | 74 meters, hourly data, labels produced by XGBoost/LightGBM ensemble trained on LEAD | UNKNOWN | Model-generated pseudo-labels | DG-D | EXCLUDED from Gold/professional/confirmatory use |

## MAD reconciliation: Track A release and Track B stop

The frozen [MAD repository](https://github.com/IISGLab/MeteringAnomalyDiagnosis) commit is `a83de7ec7399d71c9eb81e0284fce0526b2b9887`; `MAD.npz` is SHA-256 `84dff6d73d671e29b4147fd49962a41a22ea9d6bcfadb205782971af4f86a497`. It makes the requested 504/382/122/7,733 claims and exposes `x_train [2319,14,48]` and `x_test [5414,14,48]`. It supplies 14 normalized variables: phase voltage/current; total and phase active power; total and phase power factor. Its labels are exact only at the coarse level: `0 = normal`, `1..6 = Abnormal-1..6`.

The author-associated [2024 paper](https://doi.org/10.3390/en17050993) instead reports 15-minute/96-point samples, 7,421 retained samples, and a named six-class taxonomy. The difference is material. The v0.13 registry therefore records the repository release as `version_mismatch_pending` and does not transfer paper class names, sample counts, or preprocessing assumptions to it.

MAD satisfies the source definition of field/professional labelled actual AMI, so Track A is released as `EXTERNAL_GOLD_OR_PROFESSIONAL_LABEL` for smart-grid metering anomalies only. Its binary normal-versus-labelled-anomaly framing does not require an unverified mapping from opaque labels to physical classes. Feature mapping, threshold choice, and preprocessing must be frozen without inspecting `y_test`; every result must be named `External MAD author-split sample-level binary 0-vs-1..6`. This is not a meter-disjoint performance estimate, an AMI maintenance outcome result, streetlight Gold, streetlight accuracy, or a fault probability.

Track B is stopped as `NOT_ASSESSABLE`, not failed: no meter IDs, timestamps, split construction, release DOI, or meter-to-sample mapping exist in the frozen source. The concrete consequence is that no one can establish or audit whether a physical meter occurs in both partitions. Never report an author-split Track A result as an independent-meter holdout result.

## REFIT gate

The official [REFIT annotation record](https://doi.org/10.15129/9729a2a0-11ce-4cce-b0d0-144c483fcb33) explicitly licenses the annotation materials CC BY 4.0 and calls them real rather than simulated. Repeated official-file downloads returned 403, so raw availability is `BLOCKED_EXTERNAL_DATA`. It retains DG-B provenance but is ineligible to run until access is restored. When available, it is eligible only for secondary, pre-registered checks of temporal baseline departure and persistence. It lacks three-phase channels, so phase-current asymmetry is inapplicable.

## Exclusions

The relevant source is the [UCR Time Series Anomaly Archive 2021](https://www.cs.ucr.edu/~eamonn/time_series_data_2018/UCR_TimeSeriesAnomalyDatasets2021.zip), introduced by [Wu and Keogh](https://doi.org/10.1109/TKDE.2021.3112126), rather than the classification archive. It contains `210`, `211`, and `212` Italianpowerdemand anomaly files whose names encode train end and anomaly start/end. This is labelled anomaly ground truth, but only for generic univariate temporal detection. The reviewed official materials provide no explicit dataset licence, so it remains `UNKNOWN` and optional secondary stress testing is blocked until licence confirmation. It is excluded from phase/current, electrical-cause, streetlight, and fault-probability claims.

The [Zenodo record](https://doi.org/10.5281/zenodo.18670956) says its labels are generated by an XGBoost/LightGBM ensemble. It is DG-D and excluded even if an explicit licence becomes available. It may only be considered for a separately labelled weak-label stress test, never for Gold, professional-label, calibration, threshold choice, or confirmatory performance.

## Preconditions to lift a gate

1. For MAD Track A: keep commit `a83de7ec7399d71c9eb81e0284fce0526b2b9887`, SHA-256 `84dff6d73d671e29b4147fd49962a41a22ea9d6bcfadb205782971af4f86a497`, opaque binary label rule, author split, and LG-S feature contract fixed before reading `y_test`; review CC BY-ND 4.0 compliance for any shared derived artifact.
2. For MAD Track B: stop until source metadata permits a meter-disjoint audit.
3. For REFIT: resolve `BLOCKED_EXTERNAL_DATA`, obtain the exact annotation rule and label-window semantics, and freeze a house-disjoint or time-forward split before looking at test metrics.
4. For UCR: obtain explicit licence evidence before any secondary temporal stress test.
5. For all included data: keep raw data in ignored storage and prefix every resulting metric with the dataset/domain name.

## Sources

- [MAD repository](https://github.com/IISGLab/MeteringAnomalyDiagnosis)
- [Sun et al. 2024](https://doi.org/10.3390/en17050993)
- [REFIT annotated dataset](https://doi.org/10.15129/9729a2a0-11ce-4cce-b0d0-144c483fcb33)
- [Rashid et al. ICASSP 2019](https://ieeexplore.ieee.org/document/8683792/)
- [UCR archive](https://www.cs.ucr.edu/~eamonn/time_series_data_2018/)
- [Dau et al. 2019](https://doi.org/10.1109/JAS.2019.1911747)
- [Zenodo pseudo-labelled record](https://doi.org/10.5281/zenodo.18670956)
