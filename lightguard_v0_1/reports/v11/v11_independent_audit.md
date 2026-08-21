# LightGuard v0.11 Independent Audit

## Outcome

**PASS WITH WARN against the v0.11 stopping rule.** The corrected workspace has a deterministic 149-file raw audit and an honest 36-case H1-aware blind packet. Unavailable strata are explicitly recorded rather than fabricated.

Route C remains the correct scientific route: 149 audited inventory files, usable Gold `0`, usable Silver Operational `0`, and no verified cabinet-meter-operational-outcome mapping. The result is a proxy anomaly-sign analysis, not a field fault evaluation.

## Validation evidence

The requested independent narrow command returned:

```text
python3 scripts/test_v11_artifacts.py
{"status": "PASS", "files": 149, "score_rows": 29181, "review_cases": 36}
```

This PASS confirms the implemented artifact contract, including Route C values, the April/May-June windows, the score SHA seal, six matched controls, hidden blind fields, and protected-path assertions. Together with the corrected current reports and supplied full preflight result, it supports the PASS WITH WARN stopping-rule decision.

The corrected-workspace preflight result supplied for this re-audit reports artifact PASS, Flutter analyze with no issues, 24 tests passed, web build passed, and Android APK build passed at 52.2 MB. No Flutter or standalone Git command was run by Agent D.

## Gate summary

| Gate | Result | Audit conclusion |
|---|---|---|
| Raw coverage | PASS | Inventory and full label audit agree on 149 files, 1,165,875 rows/profile roots, and 4,460 columns/JSON paths. |
| Non-tabular coverage | WARN | The declared audit is machine-readable CSV/JSON/XLSX coverage; non-tabular PDF/DOCX/HWP/ZIP content is not semantically profiled. |
| Field evidence | PASS | No field-confirmed Gold or independent operational Silver record was found or manufactured. |
| Mapping | PASS with limitation | Meter-level overlap is only PARTIAL; the cabinet and operational chain is unavailable. This supports Route C, not outcome evaluation. |
| Gold/Silver/Proxy/Unlabeled separation | PASS | Gold `0`, Silver `0`, proxy inputs/signs retained as proxy, and unlabeled records not treated as normal truth. |
| H1/proxy circularity | PASS with limitation | Proxy scoring excludes H1 and canonical data until the score seal. D1, D2, D3 and H1 still share raw AMI-derived information, so their overlap is not independent corroboration. |
| April versus May-June | PASS | April is calibration/reference; May-June is confirmatory scoring. |
| Canonical join order | PASS | Score SHA is sealed before the six canonical rows are joined. |
| Controls | PASS | Fixed-hash controls use meter/month/time-slot matching and event exclusion without detector-score selection. They are unlabeled background, not true negatives. |
| Blind hidden fields | PASS | Model group, H1 decision, detector score, canonical-six status, stratum, detector names, exact timestamp, and meter ID are absent from the human HTML packet. Relative traces, anonymized alias, baseline, phase values, and missingness are visible as permitted. |
| Blind availability | PASS WITH WARN | Requested/available/selected is explicit: H1+Proxy High `6/15/6`, H1-only `0/15/0`, Proxy High-only `759/15/15`, matched random `29181/15/15`. The authoritative HTML/template contain 36 actual cases. No unavailable H1-only cases are fabricated. |
| Human truth boundary | PASS WITH WARN | Reviewer labels are not collected, and any future label is an anomaly-sign opinion rather than field-confirmed fault truth. |
| v11 UI wording | PASS with limitation | The v11 card correctly says Route C, Gold/Silver zero, anomaly-sign, and no actual fault accuracy/rate. Other legacy UI cards still show generic normal/fault/FPR/Recall vocabulary and require version-scoped interpretation. |
| v0.10 freeze | PASS | Frozen release reference is `d34d8323b3742c9116060d9548bd29c18750cb1f`; freeze integrity passed. |
| Secret/raw/Office/harness tracking | PASS | `.gitignore` covers `.env`, raw official sources, harness docs, and Office extensions; the validator’s protected tracking assertion passed. |
| Flutter/Test/Web/Android completion | PASS | Current supplied full preflight reports clean analyze, 24 passing tests, successful web build, and successful 52.2 MB APK build. Not re-run by Agent D. |

## Specific technical note on D3

The earlier one-phase concern is not present in the current B-line source. B-L-13 has null i2 and i3 values across its 8,688 audited April-June rows, and the detector’s `phase_count == 3` eligibility excludes it. B-L-12 and B-L-35 show the same null-channel one-phase pattern. This gate is PASS for the current source encoding.

## Release disposition

The v0.11 stopping rule can be marked complete with WARN status at the Route C evidence boundary. The remaining work is evidence acquisition, not silent relabeling: obtain verified cabinet-meter mapping and operational/field outcomes, then collect blind expert labels without tuning the detector on those labels.

## Allowed claims

The current artifacts support proxy anomaly-sign density, same-source detector concordance, detector-independent descriptive enrichment, and future expert-reviewed anomaly-sign reporting.

They do not support actual fault rate, field accuracy, fault recall, precision, FPR, specificity, confirmed cause, or independent validation from agreement among detectors sharing the same AMI stream.
