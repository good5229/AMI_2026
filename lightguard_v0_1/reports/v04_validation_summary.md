# LightGuard v0.4 Ranking & Weather Holdout Validation

## Baseline
- v0.3 SHA: `935bc5ea7d70e878f15113dc08d11dfee7ebcbb350d90d421f46a7704cf27368`
- v0.3 is regression-only; no threshold or weight was tuned on it.

## Error Audit
- Top-20 false-positive rows: 10
- Lowest-ranked anomaly rows: 30
- Main causes: high activation/duration hard negatives and insufficient policy/phase/load separation.

## Weather Sensitivity
- Modifier range: 0.028000 to 0.028000
- Rank changes: 0
- v0.3 diagnosis: A: modifier nearly identical; insufficient discrimination

## Calibration
- SHA: `8fe85425f6ca3b9bc2517a137da96d3edc22bbf387209b53efd933364496032e`
- Cases: 180
- Objective: recall >= 0.98; minimize normal FPR; maximize P@10 then P@20 then NDCG@10; minimize candidates and complexity
- Frozen weights: `{"activation": 0.6, "duration": 0.25, "load": 0.25, "phase": 0.2, "policy_penalty": 0.2, "solar_penalty": 0.2, "threshold": 0.55, "transient_penalty": 0.2, "weather": 0.0}`

## Confirmatory Holdout
- SHA: `1be716621da5b53bce11a748d9b05e63d4aa329e7d62b8f16e606b2ccff09831`
- Abnormal: 46
- Normal: 158

| model | recall | FPR | P@5 | P@10 | P@20 | R@10 | R@20 | AP | NDCG@10 | candidates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| v0.3 M2 | 1.000000 | 0.316456 | 1.000000 | 0.900000 | 0.800000 | 0.195652 | 0.347826 | 0.805087 | 0.936379 | 96 |
| v0.4 | 0.978261 | 0.018987 | 1.000000 | 1.000000 | 1.000000 | 0.217391 | 0.434783 | 0.996510 | 1.000000 | 48 |

## Weather Decision
- Decision: context_only
- Basis: No independent holdout ranking improvement; weather retained as reference context only.

## Actual AMI Replay
- Six anonymized competition replay windows remained separate from Busan KASI/KMA and Suyeong assets.
- Interval consistency: 6/6
- Peak consistency: 2/6
- Phase consistency: 6/6

## Inspection List
- v0.3 M0 reference: 66 candidates / 20 false positives (reference only; not used for v0.4 reduction)
- Holdout M0 candidates: 140
- Best model candidates: 48
- Holdout false positives: 94 to 3
- All v0.4 reductions compare models on the same confirmatory holdout.
- Cost conversion: prohibited without sourced dispatch cost.

## Claims and Limits
- Claimable: controlled validation shows whether context improves ranking on an independent deterministic holdout.
- Not claimable: field accuracy, municipal AMI performance, dispatch-cost savings, or causal weather benefit beyond this suite.
