# v0.8 False-Positive Taxonomy for v0.9 Forensics

## Scope and frozen boundary

This is a deterministic, row-level audit of the frozen v0.8 calibration and
confirmatory sets. It replays only the frozen C1/C2/C3 configurations at their
frozen threshold of `0.55`. It does not edit the detector, v0.8 data,
or v0.8 results, and it does not select or tune a v0.9 candidate.

- Calibration source SHA-256: `b9825d7b8d336de9421a5941d2c7f069202b3f402fa4090b2837abb7d3a38b2f`
- Confirmatory source SHA-256: `71a4d7099be61f073f8411acd3b0af999dd672060dde9621513e0505e32c1a1d`
- Candidate-freeze SHA-256: `12fdb827f3b3d553707b616425bbc9721405df7623d40c79a87169589eed2b35`
- Calibration/confirmatory case counts: `288` / `432`
- Inventory definition: original label `normal` and frozen model decision `anomaly`
- The inventory retains original case, asset, factor-tuple, signal-parameter, and seed identifiers.

The resulting calibration false-positive count is expected to be zero under the
frozen selected C1/C2/C3 configurations. Confirmatory false positives are
failure-analysis evidence only; they are not available for v0.9 tuning.

## Primary-family rule

Each inventory row has exactly one primary family so counts are additive. Fixed
priority is: solar boundary, weather context, missing load/phase, persistence,
near-threshold load variation, then other. `evidence_flags` in the CSV preserves
all overlapping evidence, so a primary solar-boundary row can still be counted as
weather-context or missing-feature evidence below.

Definitions:

- `solar_boundary_normal`: `near_solar_boundary=true` from the frozen scenario.
- `weather_context_normal`: weather is available and frozen regime is `high_cloud`, `overcast`, or `rainfall`.
- `missing_load_phase_normal`: frozen `load_mismatch` or `phase_selectivity` is absent; absence is retained, never imputed.
- `persistence_artifact_normal`: non-transient, non-policy normal with duration at least 60 minutes.
- `near_threshold_load_variation`: available load mismatch in `(0, 0.06]` and score margin in `[0, 0.10]`.
- `other_evidence_grounded_normal`: no preceding observable rule applies.

## Additive primary-family counts

| split | model | primary family | false positives |
| --- | --- | --- | --- |
| calibration | C1 | solar_boundary_normal | 0 |
| calibration | C1 | weather_context_normal | 0 |
| calibration | C1 | missing_load_phase_normal | 0 |
| calibration | C1 | persistence_artifact_normal | 0 |
| calibration | C1 | near_threshold_load_variation | 0 |
| calibration | C1 | other_evidence_grounded_normal | 0 |
| calibration | C2 | solar_boundary_normal | 0 |
| calibration | C2 | weather_context_normal | 0 |
| calibration | C2 | missing_load_phase_normal | 0 |
| calibration | C2 | persistence_artifact_normal | 0 |
| calibration | C2 | near_threshold_load_variation | 0 |
| calibration | C2 | other_evidence_grounded_normal | 0 |
| calibration | C3 | solar_boundary_normal | 0 |
| calibration | C3 | weather_context_normal | 0 |
| calibration | C3 | missing_load_phase_normal | 0 |
| calibration | C3 | persistence_artifact_normal | 0 |
| calibration | C3 | near_threshold_load_variation | 0 |
| calibration | C3 | other_evidence_grounded_normal | 0 |
| confirmatory | C1 | solar_boundary_normal | 24 |
| confirmatory | C1 | weather_context_normal | 0 |
| confirmatory | C1 | missing_load_phase_normal | 0 |
| confirmatory | C1 | persistence_artifact_normal | 0 |
| confirmatory | C1 | near_threshold_load_variation | 0 |
| confirmatory | C1 | other_evidence_grounded_normal | 0 |
| confirmatory | C2 | solar_boundary_normal | 24 |
| confirmatory | C2 | weather_context_normal | 0 |
| confirmatory | C2 | missing_load_phase_normal | 0 |
| confirmatory | C2 | persistence_artifact_normal | 0 |
| confirmatory | C2 | near_threshold_load_variation | 0 |
| confirmatory | C2 | other_evidence_grounded_normal | 0 |
| confirmatory | C3 | solar_boundary_normal | 22 |
| confirmatory | C3 | weather_context_normal | 0 |
| confirmatory | C3 | missing_load_phase_normal | 0 |
| confirmatory | C3 | persistence_artifact_normal | 0 |
| confirmatory | C3 | near_threshold_load_variation | 0 |
| confirmatory | C3 | other_evidence_grounded_normal | 0 |

## Overlapping evidence-flag counts

| split | model | evidence flag | false positives |
| --- | --- | --- | --- |
| calibration | C1 | solar_boundary | 0 |
| calibration | C1 | weather_context | 0 |
| calibration | C1 | missing_load | 0 |
| calibration | C1 | missing_phase | 0 |
| calibration | C1 | persistence | 0 |
| calibration | C1 | near_threshold_load_variation | 0 |
| calibration | C1 | other | 0 |
| calibration | C2 | solar_boundary | 0 |
| calibration | C2 | weather_context | 0 |
| calibration | C2 | missing_load | 0 |
| calibration | C2 | missing_phase | 0 |
| calibration | C2 | persistence | 0 |
| calibration | C2 | near_threshold_load_variation | 0 |
| calibration | C2 | other | 0 |
| calibration | C3 | solar_boundary | 0 |
| calibration | C3 | weather_context | 0 |
| calibration | C3 | missing_load | 0 |
| calibration | C3 | missing_phase | 0 |
| calibration | C3 | persistence | 0 |
| calibration | C3 | near_threshold_load_variation | 0 |
| calibration | C3 | other | 0 |
| confirmatory | C1 | solar_boundary | 24 |
| confirmatory | C1 | weather_context | 17 |
| confirmatory | C1 | missing_load | 12 |
| confirmatory | C1 | missing_phase | 4 |
| confirmatory | C1 | persistence | 13 |
| confirmatory | C1 | near_threshold_load_variation | 0 |
| confirmatory | C1 | other | 0 |
| confirmatory | C2 | solar_boundary | 24 |
| confirmatory | C2 | weather_context | 17 |
| confirmatory | C2 | missing_load | 12 |
| confirmatory | C2 | missing_phase | 4 |
| confirmatory | C2 | persistence | 13 |
| confirmatory | C2 | near_threshold_load_variation | 0 |
| confirmatory | C2 | other | 0 |
| confirmatory | C3 | solar_boundary | 22 |
| confirmatory | C3 | weather_context | 15 |
| confirmatory | C3 | missing_load | 12 |
| confirmatory | C3 | missing_phase | 3 |
| confirmatory | C3 | persistence | 13 |
| confirmatory | C3 | near_threshold_load_variation | 0 |
| confirmatory | C3 | other | 0 |

## Interpretation boundary

The taxonomy identifies controlled hard-negative mechanisms represented in the
frozen v0.8 design. It is not a fault label, municipal AMI estimate, or proof of
field behavior. The KMA regime is retained as experiment context; v0.8's
non-promoted weather candidate remains context-only and this audit makes no
weather-policy claim.
