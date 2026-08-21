# v0.8 Confirmatory Uncertainty

- Holdout SHA-256: `71a4d7099be61f073f8411acd3b0af999dd672060dde9621513e0505e32c1a1d`
- Cases: 432 controlled generated scenarios
- Bootstrap: 1000 cell-and-class-stratified resamples, seed 20260820

## Wilson 95% intervals

- frozen_v04: recall [0.43845732, 0.57064014]; FPR [0.25657163, 0.37952976]
- C1: recall [0.66871275, 0.78616051]; FPR [0.07581156, 0.16000137]
- C2: recall [0.66871275, 0.78616051]; FPR [0.07581156, 0.16000137]
- C3: recall [0.63486619, 0.75632481]; FPR [0.06822738, 0.14939063]

## Bootstrap delta 95% intervals vs frozen v0.4

- C1: {'recall': [0.17592593, 0.27777778], 'fpr': [-0.28240741, -0.125], 'average_precision': [0.18034158, 0.26772648]}
- C2: {'recall': [0.17592593, 0.27777778], 'fpr': [-0.28240741, -0.125], 'average_precision': [0.12130475, 0.24149164]}
- C3: {'recall': [0.14814814, 0.24537037], 'fpr': [-0.28715278, -0.13888889], 'average_precision': [0.14045979, 0.25501761]}

These intervals quantify controlled generated-case uncertainty, not field AMI uncertainty.
