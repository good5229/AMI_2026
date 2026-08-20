# LightGuard v0.11 Agent C: Raw Data Forensics

## Scope and decision

This is an independent, read-only audit of the locally available CSV, JSON,
and XLSX sources and the raw/official paths referenced by the repository. It
does not create detector outputs, relabel existing rows, alter v0.10, or treat
an anonymized AMI pattern as a field fault.

The verified route is **Route C: proxy anomaly-sign grouping with truth
acquisition pending**.

There is no locally verified Gold or Silver Operational label source that can
be joined to a municipal cabinet, meter, and event time. The available data
support asset metadata, measurement quality, operational-pattern candidates,
and controlled scenario labels only. v0.10 H1 and its real-background claims
must therefore remain frozen and must not be recalibrated from these sources.

## Audit coverage

The independent inventory covered 149 relevant files after excluding generated
`build/`, `.dart_tool/`, and `.git/` duplicates:

| Format | Count | Main locations |
|---|---:|---|
| CSV/TSV | 67 | `lightguard_app/assets/data/`, `lightguard_v0_1/data/`, validation and reports |
| JSON | 78 | app seeds, data, validation manifests and reports |
| XLSX | 4 | `official_docs/AMI Data Sample/` |
| Total | 149 | all relevant local paths, including ignored official XLSX |

The four XLSX files are the 1-1 summary and the A, B, and C feeder MDMS
samples. Non-tabular PDF/DOCX/HWP/ZIP files were not parsed because this Agent
C task is restricted to CSV/XLSX/JSON profiling. They were left untouched.

The existing v0.11 inventory provides the same 149-file scope and records 67
CSV, 78 JSON, and 4 XLSX sources. The current local hashes independently
confirmed for high-value sources include:

| Source | SHA-256 | Rows or records |
|---|---|---:|
| `official_docs/AMI Data Sample/1-1_총괄 데이터 표_가명화_AMI_★.xlsx` | `57c127c6752b996a6109080a5b6b16cbced599b3113ee21126687b05aa16cf3d` | 129 data rows |
| `official_docs/AMI Data Sample/2-1_MDMS자료(AMI 데이터)_A선로_가명화_★.xlsx` | `6be7be49c531aa00616056d25dd255effbeae3ad3d9a7b75bdaddfeeeae61b5f` | 535,166 data rows |
| `official_docs/AMI Data Sample/2-2_MDMS자료(AMI 데이터)_B선로_가명화_★.xlsx` | `c18b49022d1c7dee2117a8d65a07d71351fb1aea8538751b7032867e4081b7d0` | 280,836 data rows |
| `official_docs/AMI Data Sample/2-3_MDMS자료(AMI 데이터)_C선로_가명화_★.xlsx` | `b8a9cbdeb97c8bd69482d0e352621951e44b8e3d1636f94332f515edd112acdd` | 258,647 data rows |
| `lightguard_v0_1/data/ami_cabinet_mappings.csv` | `b52e876a18051865ffda49f85ee71955be02276b7bf4faca1076b55443efb7da` | 0 data rows |
| `lightguard_v0_1/data/ami_events.csv` | `c131fd7d635788b7ab71d50d31bff1abd91a3b492d57bae9b0a0a3ee7fed88d8` | 6 event rows |
| `lightguard_app/assets/data/suyeong_v02_objects.json` | `3554627e2b4344e0b3f5cb5dd846b47b705037eb0c5c069174539961f0add264` | 204 objects |

The repository's older `lightguard_v0_1/source_manifest.json` declares a
different hash for `suyeong_v02_objects.json` (`808a49...`). This is a
reproducibility warning, not evidence of a label. The manifest was not edited
in this audit.

## Label and sign field audit

The following are the observed categorical values in the full local profiles.
They are classified by meaning, not by field name alone.

| Field or field family | Observed values | Interpretation |
|---|---|---|
| `fault_status` in AMI event tables | `unverified inspection candidate` | Workflow candidate status; explicitly not a confirmed fault |
| Scenario `fault_status` | `validation_candidate` | Controlled injection output; not field truth |
| `event_type` | `daytime_full_activation`, `daytime_partial_activation`, `daytime_phase_selective_activation`, `partial_dimming` | Proxy anomaly signs derived from current behavior |
| Scenario `label` | `injected_anomaly`, `normal_control`; elsewhere `normal`, `abnormal` | Synthetic or controlled labels with known scenario construction |
| `ami_state` | `unlinked`, and in the legacy Gangneung seed `linked` | Link-state metadata, not a fault/maintenance outcome |
| `state` | `as_observed`, `load_unavailable`, `phase_unavailable`, `weather_unavailable`; v0.10 also `evaluable`, `not_evaluable_warmup` | Evidence availability and warm-up state |
| `decision` / `action` | `normal`, `anomaly`, `abstain`; `inspect`, `observe`, `data_check_required` | Detector decisions or operational actions, not adjudicated truth |
| `rule_ids` | `scenario_injection`, `daytime_partial_activation`, `post_sunrise_persistence_90m`, signal/high-score/normal rules | Explainable rules used to generate or interpret candidates |
| `field_truth_label` | `unavailable`; v0.10 rows also state `field_truth_available=False` | Direct evidence that field truth is unavailable |
| Controller metadata | Suyeong `양방향식`; Gangneung controller types including `GMC-200S`, `GMC-200N`, `GMC-200`, `타이머`, `단방향`, `PMC-200` and other legacy values | Asset/controller descriptors; no repair, complaint, or failure outcome |

No profiled CSV, JSON, or XLSX contains a verified field-level categorical
label for maintenance completion, repair, complaint resolution, outage/fault
code, or inspection adjudication joined to a target cabinet and event time.
The controller values are real-looking asset metadata, but they do not change
that conclusion.

## Region and AMI mapping evidence

### Suyeong

- 204 cabinet objects are present with asset, fixture, spatial, schedule, and expected-load fields.
- All 204 objects have `ami_state=unlinked` and `has_real_ami=false`.
- 46 objects have `signal_source=scenario_injection` and 158 have `signal_source=none`.
- All 204 carry the explicit mapping-visibility reason that an official Suyeong AMI-to-cabinet mapping is absent.
- `lightguard_v0_1/data/ami_cabinet_mappings.csv` has a header and zero rows.
- The 46/158 scenario labels are valid controlled-validation labels, not Suyeong field outcomes.

### Chungju

- 871 cabinet objects are present.
- All 871 have `ami_state=unlinked` and `has_real_ami=false`.
- Controller link status is cabinet-only and controller type is blank across the seed.
- Generated anomaly evidence contains expected/observed duration and peak fields and normal/signal rule IDs, but no field event, maintenance, complaint, or inspection record.
- This is an asset-only and scenario/proxy source, not a labeled AMI source.

### Gangneung

- 339 cabinet objects, 786 controller rows, and 5,667 fixture rows are present.
- The legacy seed reports 338 `linked` and 1 `unlinked` AMI state, with 338 `has_real_ami=true` values.
- The project provenance note explicitly says these legacy fields express controller-linked structure and are not approved as actual AMI. The external readiness note also records that no public cabinet-linked interval AMI was found and requests an authorized mapping, interval series, quality flags, and maintenance labels.
- Therefore the 338 legacy links are not Gold/Silver truth and do not override the missing raw interval and field-outcome join.

### Anonymized AMI and v0.10

- The six event rows and six replay windows use anonymized meter IDs and current/energy behavior only.
- All event rows retain `unverified inspection candidate` rather than a fault label.
- `ami_monthly_transitions.csv` has 15 rows covering five meters over three months and is schedule-behavior evidence only.
- v0.10 shadow replay has 455 rows, all `field_truth_available=False`; its paired background is not a normal label.
- v0.10 documentation explicitly states that the anonymized AMI has no municipal asset, rated-load, KMA, KASI, maintenance, or repair join.

## Official XLSX findings

The 1-1 summary has one sheet, `총괄표_게시용`, 129 data rows, and 11 columns.
It exposes asset/contract-like fields such as `순번(계기번호)`, `수전전력`, and
`산업분류`. Two industry-category values were observed, but there is no
time-aligned fault, maintenance, complaint, controller-state, or cabinet-to-
meter outcome join.

The A, B, and C feeder sheets each have one sheet, 16 columns, two header rows,
and respectively 535,166, 280,836, and 258,647 data rows. Their headers and
values are measurement-oriented: time, generation/power, voltage, current,
active/apparent/reactive energy, and phase-current channels with feeder or
meter grouping. A full shared-string scan found zero occurrences of the
fault, maintenance, repair, complaint, controller-state, anomaly-label, or
mapping terms in all three files.

These XLSX sources are therefore usable as measurement input or a candidate
proxy background after a permitted identity/time join. They are not Gold or
Silver labels by themselves. The Office files remain local and excluded from
Git as required.

## Existing v0.11 inventory cross-check

The pre-existing v0.11 audit inputs were also inspected as evidence, without
modifying them:

- `v11_raw_source_inventory.csv`: 149 source rows, covering 67 CSV, 78 JSON, and 4 XLSX files.
- `v11_label_source_inventory.csv`: 301 candidate field rows, classified as 141 `S2_PROXY_INPUT`, 97 `S1_CANDIDATE`, and 63 `U`; every row has `usable=False`.
- `v11_label_mapping_audit.csv`: 96 mapping rows; 32 use exact target-meter values and 64 are field-name-only. Mapping confidence is `PARTIAL` for 32 and `UNAVAILABLE` for 64; usable Gold is 0 and usable Silver is 0.

The presence of a join key or a time-like field is not sufficient. The audit
requires identity provenance, event-time semantics, target-cabinet mapping,
and an adjudicated outcome before promotion to Gold or Silver.

## Evidence classification

| Class | Local result | Promotion decision |
|---|---|---|
| Gold | 0 verified sources | Not available |
| Silver Operational | 0 verified sources | Not available |
| Proxy Anomaly Sign | Current/energy patterns, transition timing, phase selectivity, load/phase availability, and controlled scenario signs | Keep as candidate evidence only |
| Unlabeled | Unmodified anonymized AMI, asset-only rows, legacy link metadata, and detector outputs without field adjudication | Do not use as normal or fault truth |

The most useful proxy sign groups for later blinded review are:

1. Persistent post-sunrise activation and daytime activation.
2. Partial or phase-selective activation.
3. Load-mismatch and rated-load availability conditions.
4. Measurement-channel gaps and contradictory evidence.
5. Solar-boundary and schedule-transition proximity.

These groups describe what the meter signal looks like. They do not name the
physical cause and must not be displayed as confirmed failure categories.

## Route C recommendation

Route C is required because no source satisfies the minimum truth contract:

`cabinet_uid + meter_id + event_start/end + operational/fault outcome + source provenance + verified join`

The next v0.11 work should therefore:

- Freeze April detector configuration before any May-June scoring.
- Preserve v0.10 H1, raw/Office files, and all existing provenance hashes unchanged.
- Group proxy anomaly signs with explicit `proxy_only` and `mapping_confidence` fields.
- Keep unmodified AMI as unlabeled paired background, never as normal truth.
- Use a blinded review sample to collect field outcomes without tuning on the review result.
- Request a minimum operational truth extract containing `cabinet_uid`, `meter_id`, controller ID where applicable, event start/end, fault/alarm code, maintenance or work-order ID, complaint/dispatch ID, inspection outcome, resolution time, quality flag, and source-system provenance.
- Promote a record to Silver only when identity and time alignment are verified and the operational event is independently attributable to the target cabinet/meter.
- Promote a record to Gold only when a field inspection or equivalent adjudication confirms the outcome and its timestamp window.
- Keep the claim boundary at proxy/controlled validation until the above evidence is received.

## Omissions and limitations

- No external data request or API call was made; this is a local forensic audit only.
- No `.env`, API key, Office source, `official_docs/`, or `harness_docs/` file was modified.
- The large XLSX files were profiled structurally and by full shared-string scan; their numeric measurements were not converted into detector outputs.
- PDF/DOCX/HWP/ZIP contents were not parsed in this Agent C deliverable.
- Existing generated v0.11 inventory files are useful cross-checks but are not independent field truth.
- The stale `source_manifest.json` hash for the Suyeong object artifact should be reconciled in a later reproducibility task, not silently corrected here.

## Boundary statement

This document is an audit note only. It does not assert actual fault recall,
maintenance recall, complaint recall, field precision, regional AMI accuracy,
or production readiness. No detector outputs were created.
