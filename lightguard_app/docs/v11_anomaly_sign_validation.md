# LightGuard v0.11 Full Label Audit & Proxy Anomaly-Sign Validation

## 1. Dataset Audit
- files audited: 149
- rows/profile roots: 1,165,875
- columns/JSON paths: 4,460

## 2. Label Evidence
| level | usable |
|---|---:|
| Gold | 0 |
| Silver Operational | 0 |
| Proxy Pattern input fields | 141 |
| Unlabeled/insufficient fields | 63 |

## 3. Mapping
- AMI to cabinet: PARTIAL meter identity only; no verified cabinet chain
- cabinet to maintenance/controller outcome: UNAVAILABLE

## 4. Selected Route
- Route C: no usable Gold or Silver Operational record.

## 5. Terminology
- Fault-performance terms allowed: no
- Default: anomaly sign, inspection candidate, field confirmation required

## 6. Proxy Definition
- P1 robust residual; P2 causal persistence; P3 three-phase pattern
- High confidence: two or more rule families

## 7. Independent Detector Results
- May-June score rows: 29181
- High-confidence proxy origins: 765 (2.6216%)

## 8. H1 / Proxy Concordance
- H1-positive origins: 6
- H1 + Proxy High origins: 6
- Same-stream concordance only; not accuracy.

## 9. Canonical Six
- Six previously identified anomaly-sign candidates joined only after score SHA seal.

## 10. Random-Control Enrichment
- Paired proxy-family uplift: 1.3333
- Exact sign-flip p-value: 0.031250

## 11. Blind Review
- Packet cases: 36
- Requested 15 per group; only 6 H1+Proxy High and 0 H1-only origins existed, so unavailable cases were not fabricated.
- Reviewer labels collected: no

## 12. Missing Gold Data
- cabinet-meter mapping, controller history, maintenance closeout, complaint/inspection disposition

## 13. QA / Build
- Independent QA: PASS WITH WARN (shared AMI dependence; reviewer labels pending)
- v11 preflight: PASS
- Flutter analyze: no issues
- Flutter tests: 24 passed
- Web release build: PASS
- Android release APK: PASS (52.2 MB)

## 14. Claims Allowed
- Proxy anomaly-sign density, concordance, overlap, enrichment, and expert-reviewed anomaly sign after review.

## 15. Claims Prohibited
- Actual fault rate, field accuracy, fault recall, precision, FPR, specificity, or confirmed cause.

## 16. Next Step
- Collect blinded expert review, then obtain verified mapping and prospective field outcomes.
