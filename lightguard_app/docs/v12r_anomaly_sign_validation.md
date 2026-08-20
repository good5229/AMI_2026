# LightGuard v0.12R Literature-Grounded Anomaly-Sign Validation

## 1. Freeze
- v0.11 SHA: b25b168250ede29b5c5bbcadab918c455d61ba74
- H1 and v0.11 proxy scores: unchanged
- Route C; Gold 0, Silver Operational 0

## 2. Literature Review
- frozen query families: 11
- unique included sources: 21
- A-grade: 19
- B-grade: 2
- direct/mechanism L2-L3: 16

## 3. Evidence by Pattern
| pattern | direct support | mechanism support | final grade |
|---|---|---|---|
| daytime full activation | road-lighting expected-state/current studies | persistence and measurement controls | EVIDENCE_A |
| persistent partial | load-profile and CUSUM evidence | causal meter-relative baseline | EVIDENCE_B |
| phase selective | phase-asymmetry electrical diagnostics | RMS-only transfer limit | EVIDENCE_B |
| baseline deviation | general benchmark/measurement support | past-only meter baseline | EVIDENCE_C |

## 4. Claim Boundary
- Literature supports anomaly mechanisms and inspection prioritization.
- Literature does not confirm a LightGuard event, provide fault probability, or replace Gold/Silver.
- RMS phase currents are phase-current asymmetry observations, not negative-sequence measurements.

## 5. Canonical Six
- Six previously identified anomaly-sign candidates mapped after literature grades were frozen.
- Each retains field confirmation unavailable.

## 6. Proxy Population
- High-confidence proxy mapped: 765
- Literature grade is pattern-based and independent of H1/proxy scores.

## 7. Human Review
- reviewers: 0
- packet: 62 unique cases
- blinding: PASS
- status: HUMAN_REVIEW_PENDING

## 8. Human Enrichment
- Not calculated. AI-generated reviewer labels are prohibited.

## 9. Inter-rater Agreement
- Not calculated; minimum two human reviewers required.

## 10. Multi-Layer Triangulation
- Current maximum claim ladder: Level 3
- Level 4 requires sealed blinded human review.
- Level 5/6 unavailable because Silver/Gold are absent.

## 11. Claims Allowed
- literature-supported anomaly sign
- algorithm concordance and matched-background enrichment
- review-ready blinded trace packet

## 12. Claims Prohibited
- actual fault probability or rate
- field accuracy, fault recall, precision, FPR, specificity
- negative-sequence fault from RMS-only phase currents

## 13. Gold Data Gap
- cabinet-meter/phase mapping
- controller ON/OFF and override log
- maintenance outcome and inspection disposition
- time-bounded fault cause adjudication

## 14. QA / Build
- independent QA: PASS
- v12r preflight: PASS
- Flutter analyze/test/web/android: PASS

## 15. Next Step
- two or more real human reviewers complete the frozen packet
- seal and analyze reviews without packet replacement
- prospective field pilot if verified Gold/Silver data become available
