# LightGuard v0.22 Regional Public-Data Value Validation

## Decision

- Overall: **MEANINGFUL_WITH_ROLE_SEPARATION**
- OPERATIONS evidence: Daegu, Buyeo, Ulsan Nam-gu + Yangju + Michuhol = 5 municipalities.
- ASSET/SIGNAL applicability: Suyeong + Daejeon + Gangneung = 3 municipalities.
- Predictive retuning: 0; municipal data are not AMI fault labels.

## Yangju — EVENT_OPERATION

- Events / management IDs: 11,892 / 9,409
- Assets with multiple distinct receipt dates: 1,711
- Distinct-date recurrence: 30d 3.36%, 90d 7.46%, 365d 18.50%
- Value: repeated complaint history and recorded action support inspection-priority context.
- Boundary: no completion date; no resolution-latency claim.

## Michuhol — AGGREGATE_OPERATION

- Complete months: 34 (2023-01 to 2025-10); incomplete rows excluded: 2
- Complaints / IoT self-repairs: 2,890 / 1,127
- IoT share of recorded complaint+IoT work: 28.06%
- Value: independent machine-originated observations already form a material operating channel.
- Boundary: monthly aggregates cannot support event-level ranking or causal effect.

## Daejeon — ASSET_SPATIAL

- Assets / unique IDs: 43,082 / 43,082
- Valid coordinates: 100.00%
- Positive lamp-count coverage: 1.90%
- Usable controller-ID coverage: 40.38%
- Value: city-scale spatial inventory and stable asset identifiers support rollout screening.
- Boundary: rated load cannot be reconstructed; controller placeholders must remain unavailable.

## Gangneung — CABINET_ASSET_LOAD

- Assets / cabinet keys: 5,667 / 339
- Coordinate / rated-capacity coverage: 100.00% / 99.63%
- Nominal capacity sum: 1,251.195 kW, conditional on the public field representing watts.
- Value: the LightGuard cabinet → asset → expected-load object contract is directly reproducible outside Suyeong.
- Boundary: nominal asset capacity is not AMI measurement or detector accuracy.

## Claim-safe conclusion

LightGuard has meaningful value across the four added regions, but through different evidence roles. Yangju and Michuhol strengthen the operational need and discovery-channel case; Daejeon supports city-scale spatial deployment screening; Gangneung strongly replicates the cabinet/asset/rated-load data contract. These results support a modular regional rollout, not a nationwide uncalibrated model or a field-fault accuracy claim.
