# LightGuard v0.11 Agent D Independent QA

- Date: 2026-08-21
- Role: Agent D / LUNA Independent QA
- Route: C
- Scope: v0.11 raw audit, label evidence, mapping, proxy detector artifacts, controls, blind packet, Flutter v11 wording, v0.10 freeze, and protected-file contract
- Write scope: this file and `lightguard_v0_1/reports/v11/v11_independent_audit.md` only

## Decision

Overall QA status: **PASS WITH WARN** against the v0.11 stopping rules.

The prior release-blocking inconsistencies are corrected. The deterministic audit is now consistently 149 files, 1,165,875 rows/profile roots, and 4,460 columns/JSON paths. The legacy 60-case proxy-family CSV/key are no longer part of the authoritative review set. The authoritative H1-aware packet reports only its 36 actually selected cases and does not fill unavailable strata with fabricated cases.

This PASS is a Route C evidence-governance PASS. It is not a field-fault accuracy or production truth certification.

## Independent command

The requested narrow validation was run:

```text
python3 scripts/test_v11_artifacts.py
{"status": "PASS", "files": 149, "score_rows": 29181, "review_cases": 36}
```

No standalone Git command or Flutter command was run in this Agent D re-audit. The full escalated `./scripts/v11_preflight.sh` result supplied for the corrected workspace reports artifact PASS, `flutter analyze` with no issues, 24 tests passed, web build passed, and Android APK build passed at 52.2 MB. Those are recorded as current preflight evidence, not re-executed here.

## Gate results

| Gate | Status | Evidence and finding |
|---|---|---|
| Raw inventory uniqueness | PASS | `v11_raw_source_inventory.csv` contains 149 unique paths; the validator checks this exact count. |
| Full raw-audit consistency | PASS | The current inventory and full label audit agree: 149 files, 1,165,875 rows/profile roots, and 4,460 columns/JSON paths. |
| Non-tabular raw coverage | WARN | The forensic scope covers 67 CSV, 78 JSON, and 4 XLSX files. PDF/DOCX/HWP/ZIP contents were not semantically parsed, so “all raw data” is not fully demonstrated. |
| Field-evidence validity | PASS | No local field-confirmed outcome was promoted. Keyword/status fields, scenario labels, detector outputs, and measurements remain non-Gold evidence. |
| Gold/Silver distinction | PASS WITH WARN | Usable Gold is 0 and usable Silver Operational is 0. This is correctly disclosed and forces Route C, but it means no field-outcome performance claim is available. |
| Mapping validity | PASS WITH WARN | Target meter values exist, but no verified meter-to-cabinet-to-operational-outcome chain exists. Mapping is PARTIAL or UNAVAILABLE and is not promoted to truth. |
| H1/proxy circularity | PASS | The independent detector boundary excludes H1, context, assets, scenarios, prior decisions, and outcomes. The score seal precedes canonical joining. |
| Shared-feature independence | WARN | D2 is a persistence transform of D1’s raw-current residual, D3 uses the same raw current stream, and H1 comparison shares AMI-derived information. Agreement is same-source proxy concordance, not independent corroboration. |
| Shared-feature accuracy claims | PASS | Reports and the v11 UI explicitly deny fault accuracy, fault rate, recall, precision, FPR, and specificity claims for Route C. |
| April calibration split | PASS | Freeze artifact fixes 2026-04-01 through 2026-04-30 as calibration. |
| May-June confirmatory split | PASS | Score artifact fixes 2026-05-01 through 2026-06-30; score rows are 29,181. |
| Score seal before canonical join | PASS | `v11_proxy_score_seal.json` says `sealed_before_canonical_join: true`, and the validator checks the score SHA-256. |
| D3 one-phase eligibility | PASS | Current B-line data encode B-L-13 i2/i3 as null for all 8,688 audited rows, so `phase_count != 3` excludes it. B-L-12 and B-L-35 are likewise one-phase/null-channel profiles. The earlier concern about B-L-13 being included is not reproduced against the current raw source. |
| Detector-independent controls | PASS | Controls match meter, month, and time slot, exclude event buffers, and use fixed-hash selection. The selection policy states detector scores are not used. |
| Control interpretation | PASS | Controls are explicitly unlabeled background, not confirmed normal outcomes. The enrichment is descriptive proxy-score contrast only. |
| Blind packet hidden fields | PASS | The HTML packet hides H1 group, H1 decision, detector scores, canonical-six status, stratum, detector names, exact timestamp, and meter ID. It shows only anonymized alias, relative trace, phase trace, local baseline, and missingness. |
| Blind availability and no fabrication | PASS WITH WARN | The authoritative manifest requests 15 per group and records actual availability/selection: H1+Proxy High `6/15/6`, H1-only `0/15/0`, Proxy High-only `759/15/15`, and matched random `29181/15/15`. The HTML/template contain 36 actual cases. H1-only is unavailable and is not fabricated. |
| Human-review state | WARN | `reviewer_labels_collected` is false. Any later expert label is an anomaly-sign opinion only, not a fault truth label without field confirmation. |
| Agent not substituting human truth | PASS | The audit labels proxy signs and controlled scenarios as non-truth evidence and keeps field confirmation pending. |
| v11 terminology in its own card | PASS | `v11_anomaly_sign_card.dart` uses Route C, Gold/Silver zero, anomaly-sign wording, and an explicit denial of actual fault accuracy/rate. |
| Cross-UI terminology consistency | WARN | Surrounding legacy screens still expose generic `정상`, `faultStatus`, FPR/Recall, and “Actual AMI Case Study” language. Those are not v11 Route C truth claims, but the shared UI can still make the boundary ambiguous without version-scoped labeling. |
| v0.10 freeze | PASS | `v10_freeze_manifest.json` retains release `d34d8323b3742c9116060d9548bd29c18750cb1f` and reports `frozen_h1_modified: false`; the validator passes the freeze check. |
| Protected tracking | PASS | `.gitignore` excludes `.env`, `harness_docs/`, `official_docs/`, and Microsoft Office extensions. The validator’s protected-path assertion passed. No protected-file content was read or changed for this QA. |
| Full preflight | PASS | Current supplied preflight evidence reports artifact PASS, Flutter analyze clean, 24 tests passed, web build passed, and Android APK 52.2 MB passed. Agent D did not re-run these commands by instruction. |

## Required disposition

The following are remaining WARN limitations, not release-blocking inconsistencies:

1. Obtain cabinet-meter mapping and controller, maintenance, complaint, or inspection outcomes.
2. Collect blinded expert review labels without using them to tune the detector.
3. Keep H1/proxy overlap labeled as same-source concordance until an independently produced outcome source exists.
4. Preserve the current 36-case availability record; do not backfill the unavailable H1-only stratum with fabricated rows.

## Claim boundary

Allowed: proxy anomaly-sign density, same-source detector overlap, detector-independent descriptive control enrichment, and later expert-reviewed anomaly-sign labels.

Not allowed: actual fault rate, field accuracy, fault recall, precision, FPR, specificity, confirmed physical cause, or a claim that shared-AMI detector agreement is independent validation.
