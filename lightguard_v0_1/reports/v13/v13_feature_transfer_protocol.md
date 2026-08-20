# v0.13 Feature Transfer Protocol

**Owner:** TERRA B Feature Transfer Methodologist  
**Status:** PRE_OUTCOME_FROZEN  
**Date:** 2026-08-21

## Question

Can a small transparent signal core using only source-native electrical measurements distinguish externally labeled electrical anomaly records? This is external mechanism validation, not LightGuard streetlight field performance, fault recall, fault probability, or H1 production detection.

## Exclusions and availability

KASI solar, astronomical or streetlight expected state, municipal policy, rated load, lamp or asset count, cabinet mapping, synthetic streetlight fields, class-derived variables, and external test labels in preprocessing or selection are prohibited. Each record requires ordered time, a stable sample ID, source feature names, and a non-label missingness mask. Missing values are not imputed. An unavailable component stays unavailable.

Three-phase evidence needs documented A/B/C currents, aligned times, documented phase identities, and common physical units or a documented common affine transform. RMS magnitudes do not encode phase angle. A magnitude difference is therefore never called negative sequence, zero sequence, or a symmetrical component.

## Frozen signal definitions

For channel `v`, record `i`, and ordered time `t`, use `m_iv = median_t(x_itv)`, `s_iv = max(1.4826 * median_t(abs(x_itv-m_iv)), epsilon_v)`, and `r_itv = clip((x_itv-m_iv)/s_iv, -8, 8)`. `epsilon_v` is the calibration fifth percentile of positive channel MAD values. A channel with no positive scale is unavailable.

| Signal | Frozen score | Ceiling |
| --- | --- | --- |
| LG-S1 | Median over available channels of temporal 95th percentile of `abs(r_itv)`. | Meter-relative only with retained meter identity/history; otherwise within-record deviation sign. |
| LG-S2 | Median over channels of longest run where `abs(r_itv) >= 2.0`, divided by valid time points. | Persistent temporal departure sign. |
| LG-S3 | Temporal median of `(max(I_A,I_B,I_C)-min(I_A,I_B,I_C))/max(median(abs(I_A,I_B,I_C)), epsilon_I)`. | Phase-current magnitude asymmetry observation only. |
| LG-S4 | Maximum absolute two-sided CUSUM of `median_v(r_itv)`, with `k=0.5`, `h=5.0`. | Abrupt/structural-change sign. |
| LG-S5 | Equal-weight mean of calibration empirical-percentile ranks of available LG-S1 to LG-S4 scores. | Transparent multivariate electrical evidence only. |

## Candidates and calibration

`SC1` is LG-S1. `SC2` is the equal-weight percentile-rank mean of LG-S2 and LG-S3, eligible only when both are available. `SC3` is LG-S5, eligible only with at least two components and requiring LG-S3 for any phase-specific analysis. The comparator is the temporal 95th percentile of maximum absolute ordinary z-score, with mean/standard deviation fit on fit partition only. No fourth candidate, deep model, learned representation, class-specific preprocessing, or source-specific expansion is permitted.

Use only author training records. The deterministic calibration partition is `sha256(sample_id + ':v13-calibration') mod 5 == 0`; if immutable IDs are unavailable, deterministically shuffle author-train order with seed `20260821` and allocate 80/20 fit/calibration. Threshold candidates are calibration score percentiles `0.80`, `0.85`, `0.90`, `0.95`, `0.975`, and `0.99`. Select threshold by calibration balanced accuracy, with ties to the higher threshold. Select candidate by calibration balanced accuracy; exact ties select SC3, SC2, then SC1.

## Confirmatory metric and immutable rule

Primary evaluation is **External MAD Binary Balanced Accuracy** on the immutable author test split, with class `0` normal and classes `1` through `6` anomalous. Success is only: eligible SC3, test balanced accuracy at least `0.70`, and at least `0.05` above the calibration-selected z-score comparator. If SC3 is ineligible, report `NOT_EVALUABLE`; do not substitute another candidate.

After test access, feature mapping, gates, normalization, preprocessing, component definitions, candidates, thresholds, tie rules, label grouping, primary metric, and success criterion are immutable. A pass supports named-dataset external electrical anomaly discrimination only. It never establishes LightGuard streetlight accuracy, field recall, asset condition, or fault probability.
