# Agent Learning Note

## Role

Subagent A, Detector Failure Forensics for LightGuard v0.8. The task is to decompose the frozen v0.7 controlled-scenario detector outcomes before any candidate detector is designed. It is not a field-AMI accuracy study.

## Model actually used

`gpt-5.6-terra`

## Sources

### scikit-learn metrics and scoring

- URL: https://scikit-learn.org/stable/modules/model_evaluation.html
- Institution/author: scikit-learn developers
- Checked: 2026-08-20
- Finding: evaluation can use separate metrics and scorers; a thresholded classification outcome and its underlying score must be kept distinct.
- LightGuard application: preserve per-row score, decision, threshold margin, and grouped recall rather than reducing the audit to a single macro value.

### scikit-learn precision-recall curve

- URL: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_curve.html
- Institution/author: scikit-learn developers
- Checked: 2026-08-20
- Finding: precision and recall are evaluated across decision thresholds from a continuous score.
- LightGuard application: record margins to the frozen threshold so future work can study score separation without silently lowering the threshold.

### scikit-learn average precision

- URL: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html
- Institution/author: scikit-learn developers
- Checked: 2026-08-20
- Finding: average precision summarizes precision-recall operating points from scores and is not the same as a linearly interpolated PR area.
- LightGuard application: any later ranking evaluation should report AP from frozen scores and keep it separate from the present binary failure audit.

### NIST Smart Grid Framework, Release 4.0

- URL: https://www.nist.gov/publications/nist-framework-and-roadmap-smart-grid-interoperability-standards-release-40
- Institution/author: National Institute of Standards and Technology; Gopstein, Nguyen, O'Fallon, Hastings, Wollman
- Checked: 2026-08-20
- Finding: smart-grid functionality depends on interoperable, testable measurement and communication systems.
- LightGuard application: retain explicit source, feature-availability, and claim-boundary fields; scenario records cannot substitute for deployed AMI interoperability or field validation.

### Advanced Metering for Phase Identification, Transformer Identification, and Secondary Modeling

- URL: https://doi.org/10.1109/TSG.2012.2219081
- Institution/author: T. A. Short, IEEE Transactions on Smart Grid / Electric Power Research Institute
- Checked: 2026-08-20
- Finding: AMI voltage and energy measurements can support phase and transformer analysis, but the work reports limited circuit coverage and calls for additional field verification; data duration and seasonal effects matter.
- LightGuard application: treat `phase_selectivity` as a controlled feature only. Do not turn it into a real phase-current assertion without meter/feeder mapping, measurement semantics, and field confirmation.

### Application of Advanced Metering

- URL: https://www.nrel.gov/docs/fy22osti/83877.pdf
- Institution/author: National Renewable Energy Laboratory
- Checked: 2026-08-20
- Finding: AMI voltage time series can support automated phase mapping, while preprocessing and time-window selection are integral to the application.
- LightGuard application: duration-sensitive and phase-aware future candidates require frozen window rules and independently verified input availability, rather than a generic global-current assumption.

## Risks

- The v0.7 rows are scenario injections, not actual AMI or confirmed field-fault labels.
- The same scenario specification is repeated over every region-season cell, so uniform scores do not establish real geographic or seasonal invariance.
- The frozen detector does not score weather, rated load, lamp count, region, or season; adding causal interpretations to those stored fields would be unsupported.
- Chungju's unavailable rated-load information must stay unavailable; numerical imputation would create false certainty.
- Retuning after inspecting the 96 cases would contaminate the frozen v0.7 baseline.

## Adopted rules

1. Audit stored scores and decisions against the frozen formula before interpreting misses.
2. Keep score components, feature availability, missingness, and threshold margin in every row-level audit record.
3. Name only the observed controlled failure types; do not infer field fault prevalence or actual AMI detection performance.
4. Preserve `rated_load_kw` missingness as a mask, not as zero or a cross-region estimate.
5. Generate and freeze a disjoint calibration set before any candidate scoring rule is selected; keep confirmatory holdout untouched until candidate parameters are fixed.
