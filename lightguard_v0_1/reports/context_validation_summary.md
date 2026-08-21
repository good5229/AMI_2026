# LightGuard v0.3 Context-Aware Controlled Validation

This is controlled validation, not field accuracy.

- Frozen set: 204 cases (46 injected anomalies, 158 normal controls)
- Frozen SHA-256: `935bc5ea7d70e878f15113dc08d11dfee7ebcbb350d90d421f46a7704cf27368`
- Official KASI available: True
- Official KMA available: True
- M0 inspection candidates: 66
- M3 inspection candidates: 56
- Potential dispatch-cost conversion: prohibited until a sourced per-dispatch cost exists.

## Results

| Model | Status | Anomaly recall | Normal FPR | P@10 | P@20 | R@10 | R@20 |
|---|---|---:|---:|---:|---:|---:|---:|
| M0 | available | 1.0 | 0.12658227848101267 | 0.0 | 0.25 | 0.0 | 0.10869565217391304 |
| M1 | available | 1.0 | 0.0949367088607595 | 0.0 | 0.5 | 0.0 | 0.21739130434782608 |
| M2 | available | 1.0 | 0.06329113924050633 | 0.5 | 0.75 | 0.10869565217391304 | 0.32608695652173914 |
| M3 | available | 1.0 | 0.06329113924050633 | 0.5 | 0.75 | 0.10869565217391304 | 0.32608695652173914 |

## Interpretation

M1-M3 are intentionally unavailable when official snapshots cannot be collected. No internal or synthetic value is substituted for official context.
Weather is implemented as a ranking confidence modifier; it never clears the M2 inspection-candidate decision.
