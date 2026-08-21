# v0.18 Feature Leakage Audit

- D1 SHA-256: `a21d87de8da61d5793fd87655efbd857be5990e7188aaec8d913c4ced788cbd0`
- Feature rows: 101,843; outcome rows: 101,843
- Availability boundary: start of receipt day; every dependency receipt date is strictly earlier.
- Same-day order synthesized: `NO`
- Prior completed-duration history requires `processing_date < current receipt date`: `PASS`
- Open prior case requires `receipt_date < d <= processing_date`: `PASS`
- Current processing date/duration in feature table: `NO`
- Future repeat outcome in feature table: `NO`
- Asset ID, D2/D3/D4/D5, AMI, staffing feature usage: `NO`
- Management-number memorization: `NO`; pseudonym is audit-only and excluded from matrix.
- Repeat-30 censoring after 2025-07-10: `PASS`
- Temporal order: development < validation < confirmatory: `PASS`
