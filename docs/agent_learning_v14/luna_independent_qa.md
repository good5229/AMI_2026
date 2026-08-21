# LUNA Independent QA Learning Record

## Role

LUNA independent QA auditor. The audit was performed after experiment execution and without changing models, thresholds, raw data, result rows, configs, or reporting inputs.

## Actual Model

GPT-5 (Codex), acting as the independent LUNA reviewer.

## Sources Reviewed

- `lightguard_v0_1/data/validation/v14/v13_freeze_manifest.json`
- `lightguard_v0_1/data/validation/v14/v14_dataset_registry.json`
- `lightguard_v0_1/data/validation/v14/v14_raw_external_manifest.json`
- `lightguard_v0_1/data/validation/v14/v14_physical_feature_mapping.json`
- `lightguard_v0_1/data/validation/v14/v14_track_a_config.json`
- `lightguard_v0_1/data/validation/v14/v14_track_b_config.json`
- `lightguard_v0_1/data/validation/v14/v14_track_c_config.json`
- `lightguard_v0_1/data/validation/v14/v14_case_evidence_matrix.csv`
- `lightguard_v0_1/reports/v14/v14_london_results.csv`
- `lightguard_v0_1/reports/v14/v14_codex_vfd_results.csv`
- `lightguard_v0_1/reports/v14/v14_sustdata_results.csv`
- `lightguard_v0_1/reports/v14/v14_cross_dataset_mechanism_matrix.csv`
- `lightguard_v0_1/reports/v14/v14_mad_predecessor_context.md`
- `lightguard_v0_1/reports/v14/v14_final_summary.md`
- `lightguard_v0_1/reports/v14/reproducibility_manifest.json`
- `lightguard_v0_1/reports/v13/reproducibility_manifest.json`
- `scripts/test_v14_artifacts.py`
- Dataset provenance recorded from the London Met repository, KU Leuven RDR CoDEx-VFD record, SustDataED2 paper/OSF/IEEE PES registry, and Zenodo 3PhaseInsight record.

## Dataset Type

- London Met: real measured but derived industrial distribution power-quality candidate; execution blocked by provenance.
- CoDEx-VFD: real controlled laboratory VFD disturbance experiment; only 16 MiB partial prefixes were evaluated.
- SustDataED2: real household electrical monitoring; appliance transitions are positive controls, not fault labels.
- 3PhaseInsight: public specification/report only; reference-only and not an executable labelled benchmark.

## License

- London Met: explicit reusable data licence remains unknown, so primary scoring is blocked.
- CoDEx-VFD: registry records CC BY 4.0.
- SustDataED2: registry records CC BY 4.0.
- 3PhaseInsight: the reviewed public artefact does not establish a reusable labelled raw-data benchmark licence.

## Label Provenance

- London disturbance-label generation remains insufficiently documented; no score is allowed.
- CoDEx labels identify controlled injected disturbance presence. They are not field-fault labels.
- SustData labels are human-corrected appliance transitions. They are not electrical faults.
- 3PhaseInsight has no public outcome/event labels suitable for evaluation.

## Physical Provenance

- CoDEx contains two named current channels, not complete three-phase phasors. All 40 evaluated files are partial run prefixes of exactly 16,777,216 bytes.
- SustData is single-household electrical monitoring. The 18 evaluated units are day/appliance positive-control clusters.
- `PMC-3` cannot support phase-sequence, symmetrical-component, or fault-type inference in these evaluated tracks.
- Independent inference units are measurement runs or day/appliance clusters, never waveform or CSV rows.

## Risks

- **RESOLVED:** all 59 raw-manifest entries now contain a non-empty, valid HTTPS source URL tied to the frozen acquisition config; CoDEx is complete at 40/40 entries and SustData at 19/19 entries.
- **RESOLVED:** `LIMITED_MECHANISM_SIGN` is prohibited by regression test and is absent from the cross-dataset matrix.
- **RESOLVED:** CoDEx `PMC-3` is `NOT_AVAILABLE`, SustData `PMC-3` is `N/A`, and neither is reported as evaluated.
- **RESOLVED:** the final summary explicitly records CoDEx `0/30` as not replicated and SustData `2/18` as inconclusive positive-control evidence.

## Adopted Rules

- Performance cannot repair a provenance failure.
- A partial prefix must never be described as a complete measurement run.
- Outcome claims must be derived from independent units, not row counts.
- CoDEx `0/30` injection-positive partial prefixes escalated means `NOT_REPLICATED`, not a limited positive mechanism sign.
- SustData `2/18` positive-control clusters escalated means `INCONCLUSIVE`, not fault detection and not a separately identified PMC-2/4/5 sign.
- `PMC-3` is unavailable for confirmatory reporting in the evaluated v0.14 tracks.
- External scores are never streetlight field accuracy, municipal performance, or actual fault probability.
- A passing artifact-contract script does not override a contradictory generated report.

## Conclusion

`PASS`. The reporting overclaims and raw-source provenance warning are resolved. The strengthened artifact regression test passes, all 59 raw entries have valid HTTPS sources, all 11 reproducibility hashes match, and all audited integrity, provenance, independent-unit, and claim-boundary checks pass without a remaining warning.
