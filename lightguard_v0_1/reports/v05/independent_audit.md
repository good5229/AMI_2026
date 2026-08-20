# LightGuard v0.5 Independent QA Audit

Date: 2026-08-20 Asia/Seoul
Auditor: gpt-5.6-luna, fresh independent auditor; no delegation or subagents
Scope: complete current working tree and git diff

## Release decision

- Overall verdict: FAIL.
- Unresolved critical findings: 2.
- Commit/push allowance: NO.
- No implementation file was changed by this audit. Tests and builds were not rerun. The analyze/test/web/Android results below are orchestrator-stated only.

## Findings

### Critical

1. C-01 FAIL: the causal implementation is not source-observation causal. The protocol requires source-row availability time, timezone, cadence, strict less-than cutoff, and origin-level consumed-history evidence at lightguard_v0_1/reports/v05/experiment_protocol.md:40-60 and :80-117. lightguard_v0_1/scripts/run_v05_causal.py:63-116 parses mostly naive datetimes, has no source availability field or timezone normalization, and filters by interval dates. run_v05_causal.py:171-232 passes all rows for the evaluation day into detection, while :289-324 evaluates each day at midnight but still scores the full day. Later same-day readings can affect an earlier decision. The causal_rule text is an assertion, not an enforced observation cutoff.

2. C-02 FAIL: robustness replay peeks at the canonical event. lightguard_v0_1/scripts/run_v05_robustness.py:160-187 selects the perturbed group closest to expected_start, where expected_start comes from the canonical event, before metrics are calculated at :196-219. This oracle-aided selection can hide missed or shifted detections and makes coverage/IoU optimistic.

### High

1. H-01 FAIL: OAT execution and no-retuning are present, but the sensitivity conclusion is post hoc and the required activation +20% instability is not surfaced. run_v05_robustness.py:250-290 classifies after observing results. parameter_sensitivity_summary.md:3-9 reports “Knife-edge or locally sensitive”; activation +20% has FPR 0.069620 versus baseline 0.018987 and candidate count 56 versus 48. The result is absent from the product summary and Flutter UI.

2. H-02 FAIL: deterministic perturbation scaffolding is incomplete. The seed and frozen weights are explicit in run_v05_robustness.py:22-27, but actual random missingness removes rows at :118-142 instead of preserving the timestamp lattice as unavailable. Only exact duplicates are injected; conflicting duplicates are not exercised. Deduplication at :145-149 is first-wins and silently discards conflicts. Per-transform hashes, conflict counts, and full unavailable denominators are not persisted.

3. H-03 FAIL: the Flutter repository converts absent numeric CSV fields to 0.0. lightguard_app/lib/data/repositories/lightguard_repository.dart:47-70 defaults activation, current, baselines, and estimated energy to zero, conflicting with nullable replay fields in lightguard_app/lib/data/models/context_models.dart:156-184.

4. H-04 FAIL: reproducibility is not release-complete. lightguard_v0_1/reports/v05/reproducibility_manifest.json:3-12 records a prior revision and only three analysis commands, while lightguard_v0_1/scripts/v05_preflight.sh:18-30 compares frozen_configuration although the manifest key is frozen_config. Its output hashes at :38-58 predate this audit and do not cover the audit reports.

5. H-05 FAIL: lightguard_v0_1/lightguard_v0_1.sqlite is tracked and contains operational inventory, controller, meter-profile, and event tables without a current documented privacy/data-release review. .gitignore:1-38 excludes common secret and Office/source classes and no token/private-key pattern was found in tracked text, but database governance remains unresolved.

### Medium

1. M-01 PARTIAL: the five B-line meters and Apr-Jun window are present. experiment_protocol.md:15-19 and meter_generalization.md:1-17 identify B-L-9, B-L-12, B-L-13, B-L-14, and B-L-35 with 15-minute data from Apr 1 through Jun 30. Stability evidence is descriptive rather than a common-lattice comparison with explicit denominators and uncertainty; B-L-13 and B-L-35 are one-phase/sparse.

2. M-02 PARTIAL: Flutter claims and wiring are mostly honest. ami_validation_screen.dart:12-13 disclaims field confirmation, and :114-163 labels V05 evidence as candidate/no confirmed fault. context_models.dart:112-184 and local_asset_source.dart:37-39 wire V05 data. The UI omits activation +20% FPR, meter scope, unavailable denominators, and evidence levels. v05_validation_test.dart:8-25 checks model claims only, not null/unavailable rendering or widgets.

3. M-03 PARTIAL: the orchestrator states analyze had no issues, 18 tests passed, a web release was built, and an APK release was built. v05_preflight.sh:33-46 contains the commands. This audit did not rerun them; the local harness log is older and records 17 tests/debug builds.

4. M-04 PARTIAL: final_v05_summary.md:39-41 still says independent QA is pending and docs/goal_progress_v05.md:31-41 is stale. The requested audit reports now record the gate, but implementation artifacts were not regenerated under the three-file-only constraint.

### Low

1. L-01 PASS: GitHub Pages wiring matches the requested shape. .github/workflows/flutter-pages.yml:3-10 targets main, :21-38 builds with base href /AMI_2026/, and :39-57 deploys the Flutter web root. lightguard_app/web/index.html:14-17 supports the injected base href.

## Area disposition

- Frozen v0.3/v0.4 hashes, weights, threshold, and weather=0: PASS. baseline_integrity.json:3-18 records v0.3 SHA 935bc5ea7d70e878f15113dc08d11dfee7ebcbb350d90d421f46a7704cf27368, v0.4 calibration SHA 8fe85425f6ca3b9bc2517a137da96d3edc22bbf387209b53efd933364496032e, v0.4 holdout SHA 1be716621da5b53bce11a748d9b05e63d4aa329e7d62b8f16e606b2ccff09831, frozen weights .6/.25/.25/.2/.2/.2/.2, threshold .55, and weather 0.
- AMI semantics: PASS. experiment_protocol.md:5-13 and final_v05_summary.md:45-46 define six anonymized detector candidates, not field truth, recall, or accuracy.
- Peak forensics: PASS. final_v05_summary.md:10-12 and peak_consistency_adjudication.md:5-24 preserve legacy 2/6, adjudicated aggregate 6/6, primary root cause AGGREGATION_DEFINITION, secondary missing data, and no field-accuracy claim.
- Warmup/unavailable: PARTIAL. run_v05_causal.py:289-307 preserves warmup as not evaluable with no fallback, but source-availability leakage remains C-01.
- Robustness/no null-to-zero: FAIL overall. Python stress paths do not substitute zero, but row deletion and Flutter zero defaults violate the unavailable-data contract.
- OAT/no retuning: PARTIAL. The grid and no-retune rule exist, but post hoc classification and hidden activation instability fail the requested evidence.
- B-line temporal/meter stability: PARTIAL. Scope is present, but stability evidence is descriptive and sparse meters limit generalization.
- Operational/economic evidence: PASS with claim limits. final_v05_summary.md:36-46 separates evidence levels and prohibits Suyeong ROI, savings, payback, and field-accuracy claims.
- Flutter claims/data/UI/tests: PARTIAL. Disclaimer and candidate model are wired, but null-to-zero parsing, omitted instability details, and shallow tests remain.
- Reproducibility: FAIL. Manifest/preflight key and provenance mismatch is unresolved.
- Secret/excluded-file safety: PARTIAL. .gitignore excludes .env, harness_docs, official_docs, Office files, and caches; static token/private-key scan was clean, but tracked SQLite governance is unresolved.
- Analyze/test/build evidence: NOT INDEPENDENTLY VERIFIED. Orchestrator-stated result is analyze clean, 18 tests pass, web release pass, APK release pass.
- Pages workflow/base href: PASS, subject to the build-evidence caveat.

## Residual risks

- AMI has no field-confirmed labels, repair outcomes, or truth mapping; six candidates are not a recall denominator.
- missing20 is 0.833333, gap120 is 0, and downsample60 IoU is 0.444; these are stress observations, not field reliability.
- Activation +20% raises FPR from 0.018987 to 0.069620.
- The ignored source workbook has unresolved timestamp semantics; B-L-13 and B-L-35 are sparse/one-phase.
- Official operational material supports deployment context only, not Suyeong-specific ROI, savings, payback, field accuracy, or fault rates.

## Sources

- OpenAI model: https://developers.openai.com/api/docs/models/gpt-5.6-luna
- OpenAI guidance: https://developers.openai.com/api/docs/guides/latest-model
- TimeSeriesSplit: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html
- Cross-validation: https://scikit-learn.org/stable/modules/cross_validation.html
- Average precision: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html
- NDCG: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html
- NIST measurement process: https://www.nist.gov/publications/nistsematech-engineering-statistics-handbook-chapter-2-measurement-process
- NIST terminology: https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-appendix-d1-terminology
- NIST measurement systems: https://www.itl.nist.gov/div898/handbook/mpc/section5/mpc56.htm
- Rolling-origin evaluation: https://otexts.com/fpp3/tscv.html
- NIST experimental design: https://www.itl.nist.gov/div898/handbook/pri/section3/pri3345.htm
- Bergmeir and Benitez: https://www.sciencedirect.com/science/article/pii/S0020025511006773
- Institutional record: https://research.monash.edu/en/publications/on-the-use-of-cross-validation-for-time-series-predictor-evaluati/
- Cerqueira et al.: https://arxiv.org/abs/1905.11744
- Official data portal: https://www.data.go.kr/data/15032441/fileData.do
- Official data portal: https://www.data.go.kr/data/15059623/fileData.do
- Official data portal: https://www.data.go.kr/data/15117413/fileData.do
- Official data portal: https://www.data.go.kr/data/15041822/fileData.do
- Suyeong: https://www.suyeong.go.kr/index.suyeong?menuCd=DOM_000000119001001000
- Busan: https://www.busan.go.kr/bhtelinfo02/?curPage=2254
- G2B notice: https://www.g2b.go.kr/pn/pnp/pnpe/UntyAtchFile/downloadFile.do?bidPbancNo=R26BK01450767&bidPbancOrd=000&fileSeq=6&fileType=&prcmBsneSeCd=07
- Korea Energy: https://min24.energy.or.kr/gb/public/dashboard/dashboard.do
- KEPCO: https://home.kepco.co.kr/kepco/front/html/WZ/2024_01/light.html

## Remediation re-audit

Date: 2026-08-20 Asia/Seoul. This addendum supersedes the prior severity for the remediated findings. No implementation files were edited. No tests/builds were rerun; the regenerated artifact contract, flutter analyze with 0 issues, and 18 passing tests are recorded as orchestrator-stated evidence.

### New release decision

- Overall verdict: FAIL.
- Unresolved critical findings: 0.
- Commit/push allowance: NO.
- The prior critical causal and robustness findings are fixed. The release remains blocked by unresolved High findings H-02 and H-05, plus a Medium manifest/hash caveat after this authorized report update.

### Prior finding disposition

1. C-01 RESOLVED AS CRITICAL; PASS WITH LIMITATION. scripts/run_v05_causal.py:27, :106-107, :180-190, and :246-250 now use Asia/Seoul interval-end timestamps as the explicit availability proxy, require availability_time < decision_time, and decide after the next-day 00:15 boundary for the 15-minute source. Warm-up rows at :325-344 remain explicitly unavailable without synthetic baselines. The artifact states that source receipt time is unavailable. This supports an honest claim of past-only replay under the interval-end proxy; it is not receipt-time causality. No additional receipt timestamps are required for this disposition.

2. C-02 RESOLVED; PASS. scripts/run_v05_robustness.py:160-219 now returns all detected intervals. actual_metrics computes the maximum IoU against the expected fixed interval only after detection. The canonical event no longer selects the candidate group by expected start.

3. H-01 RESOLVED; PASS WITH DISCLOSURE. parameter_sensitivity_summary.md:3-9 now states a precommitted neighbor criterion and diagnostic-only/no-retuning policy. lightguard_app/assets/data/context/v05_validation_summary.json:45-52 and the V05 model/UI expose activation +20%: normal FPR 0.018987 to 0.069620 and candidate count 48 to 56, with frozen_config_changed false. The observed Knife-edge or locally sensitive classification is supported by the stated criterion; no promotion or retuning is claimed.

4. H-03 RESOLVED; PASS. lightguard_app/lib/data/repositories/lightguard_repository.dart:47-70 now requires numeric fields and throws FormatException when absent or invalid. The prior null-to-zero conversion is gone. Remaining test coverage is a low residual because the cited 18-test result is not rerun in this audit.

5. H-04 DOWNGRADED TO MEDIUM. scripts/v05_preflight.sh:18-30 now compares frozen_config, and :33-46 contains the artifact-contract, analyze, test, web-release, and Android-release gates. The orchestrator reports the regenerated contract passed, analyze had 0 issues, and 18 tests passed. reproducibility_manifest.json:9-12 still lists only the three data-pipeline commands, not the full preflight command set. Its output hash for independent_audit.md was generated before this addendum, and the top-level audit report is not in that manifest. This is a provenance caveat, not a remaining critical correctness defect.

6. H-02 REMAINS HIGH. The remediation did not establish the full deterministic stress contract required by experiment_protocol.md:178-191. Actual random missingness still removes rows rather than preserving a timestamp lattice marked unavailable; duplicate handling remains exact-duplicate/first-wins rather than demonstrated conflict quarantine; per-transform source/output hashes and complete unavailable denominators remain absent from the published stress artifacts.

7. H-05 REMAINS HIGH. lightguard_v0_1/lightguard_v0_1.sqlite remains tracked and contains operational inventory, controller, meter-profile, and event data without a documented current privacy/data-release review. The prior static token/private-key scan and .gitignore exclusions remain reassuring but do not replace governance evidence.

### Updated area disposition

- Causal past-only cutoff: PASS WITH LIMITATION. The proxy and delayed decision make the qualified claim honest. Do not call it source receipt-time causal.
- Robustness candidate selection: PASS. All intervals are returned and the expected event is used only for fixed IoU scoring.
- OAT sensitivity/no retuning: PASS. The activation +20% FPR instability is disclosed in JSON/docs/Flutter and no retuning or promotion occurs.
- Flutter required numeric handling: PASS. Missing required numeric evidence raises FormatException; it is not zero-filled.
- Artifact contract/preflight key: PASS as orchestrator-stated; manifest completeness remains Medium.
- AMI candidate-only semantics, peak 2/6 plus adjudicated 6/6/root causes, B-line scope, operational/economic claim limits, secret exclusions, and Pages main/root/base-href controls: unchanged PASS or qualified PASS from the prior audit.
- Build/test evidence: PASS AS REPORTED, NOT INDEPENDENTLY RERUN. The stated evidence is analyze 0 issues, 18 tests, web release, and Android APK release.

### Residual risks

- Interval-end availability is a proxy; late source delivery, backfill, or correction after interval end is not observable. The explicit limitation prevents overclaiming but leaves this measurement risk.
- Robustness stress results remain technical replay behavior, not field recall/accuracy. Missing20 coverage is 0.833333, gap120 is 0, and downsample60 IoU is 0.444.
- Activation +20% FPR remains materially unstable at 0.069620 versus 0.018987; disclosure is correct, but this is not a reason to retune the frozen configuration.
- AMI has no field-confirmed labels, repair outcomes, or truth mapping. B-L-13 and B-L-35 remain sparse/one-phase.
- Updating this authorized report after manifest generation makes the recorded audit output hash stale until a future permitted regeneration. Commit/push remains disallowed.

## Final remediation re-audit

Date: 2026-08-20 Asia/Seoul. This section supersedes the prior gate. No implementation files were edited, and no tests/builds were rerun. The artifact-integrity result is recorded as orchestrator-stated evidence.

### Final release decision

- Overall verdict: PASS WITH RESIDUAL RISKS.
- Unresolved Critical findings: 0.
- Unresolved High findings: 0.
- Commit/push allowance: YES.

### H-02 final disposition

H-02 RESOLVED; PASS. scripts/run_v05_robustness.py:118-172 and :218-259 now preserve the source timestamp lattice while setting unavailable channels to null for random missingness, contiguous gaps, and downsampling. Exact duplicate and conflicting duplicate stresses are separate at :140-149. Conflicts are quarantined as unavailable by nulling all phases and counted by timestamp. Each result records actual_unavailable_sample_count, actual_total_sample_count, actual_duplicate_conflict_count, and per-event actual_transform_hashes. The generated robustness_results.csv contains 15 stress conditions, including baseline, three missingness rates, three gaps, two downsampling levels, three phase dropouts, exact duplicate, conflicting duplicate, and measurement-channel missing. The stress artifacts remain technical robustness evidence only, not field recall or accuracy.

### H-05 final disposition

H-05 RESOLVED; PASS. git index inspection shows no tracked SQLite files while lightguard_v0_1/lightguard_v0_1.sqlite remains local. .gitignore:6-7 covers *.sqlite and *.sqlite3, lightguard_v0_1/README.md:11 marks the database local-only, and lightguard_v0_1/reports/v05/data_release_governance.md records the reviewed schema, modem/address/location sensitivity, public release boundary, prohibited contents, and named re-entry gate. This is an appropriate conservative release boundary.

### Final area disposition

- Deterministic stress suite and artifact contract: PASS AS REPORTED. Fifteen stress conditions and the required null/conflict/count/hash fields are present; the contract was reported passed but not rerun in this audit.
- Database secret/exclusion/release safety: PASS. The database is local-only and untracked, with governance and re-entry controls.
- All prior Critical and High findings: RESOLVED.
- Prior Medium manifest caveat: remains a residual packaging note because an authorized edit to an audit report can change an output hash after manifest generation. It does not block commit/push under the zero-Critical/zero-High gate, but release packaging should regenerate the manifest after final report content is fixed.

### Residual risks

- Interval-end availability remains a proxy rather than source receipt-time evidence; the limitation is explicit and the causal claim must remain qualified.
- Actual AMI remains six unlabeled detector candidates, never field recall or accuracy.
- Stress outcomes remain technical replay evidence. Missing20 coverage is 0.833333, gap120 coverage is 0, and downsample60 IoU is 0.444.
- Activation +20% FPR remains materially unstable at 0.069620 versus 0.018987; it is disclosed and diagnostic-only with no retuning.
- B-L-13 and B-L-35 remain sparse/one-phase, and public evidence does not support Suyeong ROI, savings, payback, or field accuracy.
