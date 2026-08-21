# LightGuard v0.17 Municipal Operational Evidence Expansion

## Sources

| source | provider | rows | role |
|---|---|---:|---|
| D1 | 대구공공시설관리공단 | 101,843 | primary operational outcome |
| D2 | 대구공공시설관리공단 | 71,973 | asset location |
| D3 | 대구공공시설관리공단 | 105,449 | safety inspection context |
| D4 | 대구공공시설관리공단 | 614,241 | aggregate maintenance workload only |
| D5 | 대구공공시설관리공단 | 2,519 | aggregate project context only |

## Fault Management Dataset

- Rows: 101,843; unique assets: 40,148; period: 2020-01-02 to 2025-08-09.
- Closed with valid nonnegative duration: 101,839; unresolved: 0; negative-duration quality cases: 4.

## Resolution Time

- Median: 0 days; p90: 8 days.
- Same day: 72.3%; over 3 days: 17.5%; over 7 days: 10.8%.

## Detection Channel

- Routine inspection: 93,647 (92.0%).
- Staff report: 2,129 (2.1%).
- Citizen complaint: 5,314 (5.2%).

## Repeat Events

- Assets with repeats on distinct days: 23,815; median positive gap: 248 days.
- 30-day: 10,287/99,722 eligible episodes (10.3%); 90-day: 17,222/96,751; 365-day: 33,838/83,535.

## Spatial Join

- ID compatibility: `PARTIAL_JOIN`; matched: 39,974; ambiguous: 137; unmatched: 174.
- 100,561 event rows have exact, unambiguous candidate coordinates, but the result is `NO_SPATIAL_JOIN` and no hotspot is published because semantic identity is not verified.

## Safety Inspection

- Rows: 105,449; field actions other than `이상없음`: 9,879; review actions other than `이상없음`: 1,987.
- Electrical measurements are distribution-only because unit and official threshold applicability are unverified.

## Maintenance Context

- Material rows: 614,241, versus 145,365 advertised; D4 is `HOLD_PROFILE_ONLY` pending provider confirmation.
- Construction/project rows: 2,519; D5 type codes are not relabeled without a codebook.
- No event join key, unit price, expenditure, or cost savings is inferred.

## Operational Need Grade

**ON-A**: large actual event volume, multiple receipt routes, processing-time tail, repeated records, and safety/maintenance workload are all observed.

## LightGuard Service Mapping

- `DATA_QUALITY_REVIEW`: date, ID, coordinate, and source-snapshot exceptions.
- `REMOTE_MONITOR`: repeated-record and aging context for remote recheck.
- `FIELD_INSPECTION_CANDIDATE`: explainable queue using repeat, age, citizen report, and safety-action context.

## Competition Value

- 국민체감: citizen-report share, response-time tail, and repeated records are visible without claiming prevention.
- 활용목적: existing AMI is positioned as a triage aid for a demonstrated municipal workflow.
- 유형효과: the app separates signal evidence, controlled validation, literature, and actual operational burden.
- 개발용이성: the three-lane object maps to observed intake, monitoring, and field-action concepts.
- 범용성: other municipal schemas are candidates, not force-merged evidence.

## Claim Boundary

Daegu supports operational need only. It does not validate competition AMI fault accuracy, Suyeong field performance, prevented complaints, causal response-time improvement, or savings.

## QA / Build

Artifact QA is enforced by `scripts/test_v17_artifacts.py`; Flutter analyze/test/Web/Android are enforced by `scripts/v17_preflight.sh`.

## Next Step

Use newly linked field outcomes or new independent AMI for detector validation. Do not tune again on the frozen five-meter corpus.
