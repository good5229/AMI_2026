# v0.3 Ranking Error Audit

- Frozen SHA-256: `935bc5ea7d70e878f15113dc08d11dfee7ebcbb350d90d421f46a7704cf27368`
- Top-20 normal rows audited across M2/M3: 10
- Bottom-15 anomalies audited across M2/M3: 30
- Main false-positive groups: {'C_adverse_weather': 10}
- Case-level decomposition shows that high activation/duration controls can outrank moderate anomalies when policy, transient, phase, and mismatch evidence are not sufficiently separated.
- Weather diagnosis: A: modifier nearly identical; insufficient discrimination
