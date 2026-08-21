# LightGuard v0.5 Independent QA Learning Record

## Pre-change record

- Date: 2026-08-20 Asia/Seoul.
- Assignment: independent QA audit of the complete current LightGuard v0.5 working tree and git diff.
- Auditor assignment: `gpt-5.6-luna` (fresh independent auditor; no delegation).
- Scope: frozen artifacts, AMI semantics, peak forensics, causal evaluation, robustness, OAT sensitivity, B-line stability, evidence claims, Flutter evidence, reproducibility, security, build evidence, and GitHub Pages deployment.
- Deliverables authorized by the request: this learning report, `lightguard_v0_1/reports/v05/independent_audit.md`, and `lightguard_v0_1/reports/v05_independent_audit.md` only.
- Method record: inspect the current tree and diff, compare claims with repository evidence, browse required official sources plus at least two independent primary methodological/procurement sources, and classify findings by Critical/High/Medium/Low.

## Final audit record

- Exact assignment: gpt-5.6-luna, fresh independent QA auditor for LightGuard v0.5; audit the complete current working tree and git diff; do not delegate or spawn subagents.
- Overall result: FAIL. Unresolved critical findings: 2. Commit/push: NOT ALLOWED.
- No implementation file was changed by this audit. Tests and builds were not rerun; orchestrator claims are labeled as claims rather than independently reproduced evidence.
- Critical lesson 1: a protocol assertion is not causal evidence. Source availability timestamps, timezone semantics, strict cutoffs, and origin-level consumed-row traces must be implemented, not merely described.
- Critical lesson 2: robustness matching cannot select a perturbed result using the canonical event start. That is oracle-aided evaluation even when AMI data are only detector candidates.

## Sources consulted

- OpenAI model record: https://developers.openai.com/api/docs/models/gpt-5.6-luna
- OpenAI model guidance: https://developers.openai.com/api/docs/guides/latest-model
- scikit-learn TimeSeriesSplit: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html
- scikit-learn cross-validation: https://scikit-learn.org/stable/modules/cross_validation.html
- scikit-learn average precision: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html
- scikit-learn NDCG: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html
- NIST measurement process: https://www.nist.gov/publications/nistsematech-engineering-statistics-handbook-chapter-2-measurement-process
- NIST terminology: https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-appendix-d1-terminology
- NIST measurement systems analysis: https://www.itl.nist.gov/div898/handbook/mpc/section5/mpc56.htm
- Rolling-origin evaluation: https://otexts.com/fpp3/tscv.html
- NIST experimental design: https://www.itl.nist.gov/div898/handbook/pri/section3/pri3345.htm
- Bergmeir and Benitez primary paper: https://www.sciencedirect.com/science/article/pii/S0020025511006773
- Bergmeir and Benitez institutional record: https://research.monash.edu/en/publications/on-the-use-of-cross-validation-for-time-series-predictor-evaluati/
- Cerqueira, Torgo, and Mozetic: https://arxiv.org/abs/1905.11744
- Official Korean public-data source: https://www.data.go.kr/data/15032441/fileData.do
- Official Korean public-data source: https://www.data.go.kr/data/15059623/fileData.do
- Official Korean public-data source: https://www.data.go.kr/data/15117413/fileData.do
- Official Korean public-data source: https://www.data.go.kr/data/15041822/fileData.do
- Suyeong official site: https://www.suyeong.go.kr/index.suyeong?menuCd=DOM_000000119001001000
- Busan official site: https://www.busan.go.kr/bhtelinfo02/?curPage=2254
- G2B procurement notice: https://www.g2b.go.kr/pn/pnp/pnpe/UntyAtchFile/downloadFile.do?bidPbancNo=R26BK01450767&bidPbancOrd=000&fileSeq=6&fileType=&prcmBsneSeCd=07
- Korea Energy dashboard: https://min24.energy.or.kr/gb/public/dashboard/dashboard.do
- KEPCO official lighting page: https://home.kepco.co.kr/kepco/front/html/WZ/2024_01/light.html

The Bergmeir/Benitez paper, Cerqueira/Torgo/Mozetic study, NIST experimental-design material, and G2B notice are additional independent primary sources beyond the required official references.

## Remediation re-audit

Date: 2026-08-20 Asia/Seoul. No browsing, implementation edits, or test/build reruns were performed.

- New overall verdict: FAIL.
- New unresolved critical count: 0.
- Commit/push: NOT ALLOWED.
- Prior C-01 is resolved as a critical defect and downgraded to a documented Medium residual. The implementation now uses Asia/Seoul interval-end timestamps as an explicit availability proxy, a next-day 00:15 decision for the 15-minute data, and strict availability_time < decision_time. It explicitly says source receipt time is unavailable. This makes the narrow claim honest: past-only under the interval-end availability proxy. It does not prove receipt-time causality, and the audit does not demand unavailable receipt timestamps.
- Prior C-02 is resolved. Robustness now returns all detector intervals and uses the canonical event only for post-score fixed-interval IoU; it no longer selects a candidate by canonical event start.
- Prior H-01 is resolved. The precommitted OAT criterion remains visible, no-retuning remains explicit, and activation +20% is now exposed in product JSON, docs, and Flutter: normal FPR 0.018987 to 0.069620, candidate count 48 to 56, frozen_config_changed false.
- Prior H-03 is resolved. Required numeric ValidationEvent fields now throw FormatException rather than converting unavailable values to zero.
- Prior H-04 is downgraded to Medium. v05_preflight.sh now compares frozen_config, the regenerated artifact contract is reported passed, and the orchestrator reports analyze with 0 issues and 18 tests passed. The manifest still records only the three data-pipeline commands, and this authorized report update changes the canonical audit hash after manifest generation.
- Prior H-02 remains High: the current stress implementation still needs stronger conflicting-duplicate quarantine and complete per-transform provenance/unavailable-denominator reporting.
- Prior H-05 remains High: tracked lightguard_v0_1.sqlite still requires a documented privacy/data-release review even though the static secret scan and exclusion rules were clean.
- The B-line scope, candidate-only AMI wording, peak 2/6 and adjudicated 6/6 forensics, operational evidence limits, and Pages wiring remain as previously recorded.

The explicit proxy and delayed decision are acceptable for a qualified technical replay claim. All summaries must retain the qualifier and must not silently upgrade it to source receipt-time causality or field recall/accuracy.

## Final remediation re-audit

Date: 2026-08-20 Asia/Seoul. No browsing, implementation edits, or test/build reruns were performed.

- Final verdict: PASS WITH RESIDUAL RISKS.
- Unresolved Critical findings: 0.
- Unresolved High findings: 0.
- Commit/push: ALLOWED by the QA severity gate.
- Prior H-02 is resolved. The current robustness implementation preserves every timestamp and nulls unavailable channels for random missingness, contiguous gaps, and downsampling; exact and conflicting duplicate stresses are separate; conflicts are made unavailable; results record unavailable samples, total samples, conflict counts, and per-event transform SHA-256 values. The generated suite contains 15 stress conditions.
- Prior H-05 is resolved. No SQLite file is indexed, the local database remains preserved, *.sqlite and *.sqlite3 are ignored, README marks the database local-only, and data_release_governance.md records schema/privacy review, operational sensitivity, public release boundaries, and a re-entry gate.
- Artifact integrity is PASS as orchestrator-stated for the 15-condition stress suite. The audit did not rerun the contract.
- Residual: the reproducibility manifest can require a post-audit refresh when an authorized audit report itself is included in output hashes. This is a packaging/provenance note, not an unresolved Critical or High product defect.
