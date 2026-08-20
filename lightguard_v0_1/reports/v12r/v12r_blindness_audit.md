# v0.12R Blindness Audit

- Packet cases: 62
- Unique cases: 62
- Group availability: {"S1_ALGORITHM_LITERATURE": 6, "S2_PROXY_LITERATURE": 759, "S3_SINGLETON_LITERATURE": 6568, "S4_MATCHED_RANDOM": 20}
- Group selected: {"S4_MATCHED_RANDOM": 20, "S2_PROXY_LITERATURE": 18, "S1_ALGORITHM_LITERATURE": 6, "S3_SINGLETON_LITERATURE": 18}
- Hidden-field leakage found: []
- Reviewer labels collected: no
- Status: PASS

Matched random selection uses meter, month, and time slot plus a fixed hash. Detector flags and literature grades do not enter random-case selection.
