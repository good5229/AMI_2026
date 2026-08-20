# LightGuard v0.7 regional-seasonal validation

## Result

- Scope: 3 regions x 4 seasons = 12 controlled cells, 96 scenarios
- Macro recall: 0.5000
- Macro FPR: 0.0000
- Worst cell: chungju_autumn (recall 0.5000, FPR 0.0000)
- Official context: KMA ASOS stations 159, 105, 127 and KASI area solar times
- Detector: v0.4 frozen threshold/configuration, weather weight 0.0

## Interpretation boundary

This is controlled cross-context invariance evidence. It does not demonstrate
field performance or external AMI generalization in Gangneung or Chungju.
Each cell has four anomaly and four normal cases, so Wilson intervals remain
wide and point estimates must not be presented without their intervals.
