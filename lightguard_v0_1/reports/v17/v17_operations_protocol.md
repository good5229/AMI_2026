# v0.17 Municipal Operations Protocol

## Frozen scope

- D1 latest local snapshot is the only canonical fault-event table. Historical snapshots are not stacked.
- Resolution is `처리일 - 접수일` in calendar days. Missing, invalid, and negative durations are separate quality states.
- A repeat is another recorded event for the same exact management ID within 7, 30, 90, or 365 days. It is not a confirmed same-cause fault.
- D1-D2 spatial use requires an exact normalized ID and exactly one valid coordinate. Fuzzy road/section joins are prohibited.
- D3 measurements remain descriptive because units and an applicable official threshold were not verified.
- D4 and D5 are aggregate workload context. They have no event join key and support no cost-savings calculation.

## Interpretation

Asset clustering and repeated records mean rows are not independent fault-probability samples. Metrics are descriptive and stratified by asset, district, channel, year, and month. Daegu is an operational Evidence Layer, separate from competition B-line AMI, Suyeong scenarios, and Gangneung/Chungju assets.
