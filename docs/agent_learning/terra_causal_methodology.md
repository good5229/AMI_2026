# LightGuard v0.5 Causal Methodology Note

## Role and scope

This is the design-only causal-validation note for LightGuard v0.5. It
defines leakage-free actual-AMI replay, robustness reporting, and local
parameter sensitivity. It does not authorize changes to detector/scoring
code, source AMI rows, or frozen v0.3/v0.4 artifacts.

Actual AMI contains known detector candidates, not independently confirmed
field faults. It can describe replay behavior and data stability only. It
must not be reported as field accuracy, recall, precision, false-positive
rate, AP, NDCG, fault rate, municipal performance, or economic impact.

## Model actually used

The exact runtime assignment for this retry is "gpt-5.6-terra". This is the
model identifier recorded for this methodological output. The identifier was
checked against the OpenAI API model documentation on 2026-08-20:

- URL: https://developers.openai.com/api/docs/models/gpt-5.6-terra
  - Institution/author: OpenAI.
  - Key point: the published model identifier is "gpt-5.6-terra".
  - Applied rule: record the assigned runtime exactly; do not substitute a
    generic GPT-5 label or infer a different identifier from local variables.

## Sources reviewed

All sources below were accessed on 2026-08-20. The first nine are the
required v0.5 methodology sources. The final two are additional authoritative
sources used to independently check rolling-origin and local-sensitivity
boundaries.

- URL: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html
  - Institution/author: scikit-learn developers.
  - Key point: time-series splits are ordered and training sets accumulate
    earlier observations.
  - Applied rule: every decision uses records available strictly before that
    decision, with no shuffled row split.

- URL: https://scikit-learn.org/stable/modules/cross_validation.html
  - Institution/author: scikit-learn developers.
  - Key point: ordinary shuffled cross-validation assumes independent,
    identically distributed rows and is unsuitable for autocorrelated data.
  - Applied rule: preprocessing, baselines, cadence estimates, and candidate
    decisions are constructed inside each past-only origin.

- URL: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html
  - Institution/author: scikit-learn developers.
  - Key point: AP consumes true labels and prediction scores.
  - Applied rule: AP is only for labelled controlled validation, never actual
    AMI.

- URL: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html
  - Institution/author: scikit-learn developers.
  - Key point: NDCG evaluates predicted ordering against true relevance.
  - Applied rule: NDCG is only for labelled controlled validation, never
    actual AMI.

- URL: https://www.nist.gov/publications/nistsematech-engineering-statistics-handbook-chapter-2-measurement-process
  - Institution/author: NIST/SEMATECH.
  - Key point: measurement characterization includes repeatability,
    reproducibility, stability, and uncertainty.
  - Applied rule: report availability, duplicates, gaps, cadence, timestamp
    semantics, and channel state with detector outputs.

- URL: https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-appendix-d1-terminology
  - Institution/author: National Institute of Standards and Technology.
  - Key point: repeatability/reproducibility need explicitly stated
    conditions, including changed conditions for reproducibility.
  - Applied rule: every robustness transform records seed, level, source
    manifest, changed condition, and output manifest.

- Required publisher URL: https://www.sciencedirect.com/science/article/pii/S0020025511006773
  - Accessible institutional record reviewed:
    https://research.monash.edu/en/publications/on-the-use-of-cross-validation-for-time-series-predictor-evaluati/
  - Institution/author: Christoph Bergmeir and Jose M. Benitez, Information
    Sciences, 2012.
  - Key point: temporal dependence can invalidate ordinary
    cross-validation; blocked time-series evaluation preserves structure.
  - Applied rule: no random train/test assignment and no feature, event, or
    label window may cross the availability boundary.

- URL: https://arxiv.org/abs/1905.11744
  - Institution/author: Vitor Cerqueira, Luis Torgo, and Igor Mozetic,
    Machine Learning, 2020.
  - Key point: temporal performance estimates vary materially with the
    estimation procedure; order-preserving out-of-sample methods perform best
    in the paper's non-stationary real-world settings.
  - Applied rule: report all 7/14/30-day and expanding variants rather than
    select a retrospective winner.

- URL: https://www.itl.nist.gov/div898/handbook/mpc/section5/mpc56.htm
  - Institution/author: NIST/SEMATECH Engineering Statistics Handbook.
  - Key point: a sensitivity coefficient relates an individual component to
    the reported result.
  - Applied rule: retain the complete surface for every predeclared individual
    parameter perturbation.

- Additional source URL: https://otexts.com/fpp3/tscv.html
  - Institution/author: Rob J. Hyndman and George Athanasopoulos,
    Forecasting: Principles and Practice, 3rd edition.
  - Key point: rolling forecasting origin uses observations strictly prior to
    each test observation and excludes early origins with inadequate history.
  - Applied rule: score every eligible origin and explicitly report
    insufficient-history origins rather than filling a fallback baseline.

- Additional source URL: https://www.itl.nist.gov/div898/handbook/pri/section3/pri3345.htm
  - Institution/author: NIST/SEMATECH Engineering Statistics Handbook.
  - Key point: factorial designs are needed when interaction effects or
    response surfaces are in scope; main-effect screening is narrower.
  - Applied rule: v0.5 one-at-a-time sensitivity is local and descriptive. It
    cannot claim parameter interactions were tested or optimized.

## Independent validation conclusions

| Topic | Validated conclusion | Required control |
|---|---|---|
| Walk-forward evaluation | 7/14/30-day plus expanding comparison is valid only when each candidate is scored at its own availability-time origin. A daily table is not a decision boundary. | Keep one past-only decision trace per source observation or other predeclared scoreable unit; use daily grouping only for reporting. |
| History eligibility | Elapsed window length alone does not prove usable history. Sparse, missing, or unresolved-timestamp history cannot silently become a baseline. | Freeze meter-local row-count and availability requirements before execution; otherwise mark the origin unavailable or not_evaluable_warmup. |
| Actual-AMI metrics | The six intervals are fixed replay anchors, not truth labels. | Report coverage, overlap, density, drift, and stability with denominators; prohibit label-dependent field metrics. |
| Robustness | A degradation result needs named changed conditions and reproducible transforms. | Run each stress level independently from a pristine immutable input with fixed seed/level manifests and unavailable counts. |
| Sensitivity | Threshold and individual-weight perturbations characterize local response but cannot identify interactions or select production settings. | Change exactly one parameter per run, preserve all other frozen values, publish all grid points, and prohibit winner selection. |

## Non-negotiable causal rules

1. Decision time is the candidate observation's availability time. The
   candidate's own raw values may be scored then, but historical feature
   inputs must have availability time strictly earlier than that decision.
2. Equal-availability rows are contemporaneous. None may become historical
   input to another row in the same group.
3. A feature requiring a future neighbor, full-period statistic, global
   normalization, post-hoc duplicate choice, or event-derived alignment is
   noncausal and fails the run.
4. Canonical intervals load only after scoring for fixed overlap calculations.
   They may not tune a threshold, merge width, baseline, feature, or
   sensitivity range.
5. The v0.4 configuration remains frozen. Weather remains 0.0/context_only.
   Sensitivity is descriptive evidence, never a production-selection method.
6. If a stability or knife-edge criterion was not frozen before outputs are
   viewed, publish the full surface without either adjective. Do not create a
   numeric threshold after seeing results.
