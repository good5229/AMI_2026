# LightGuard v0.11 Full Label Audit

## Coverage

- Files audited: 149
- Sheets/root objects: 149
- Rows/profile roots: 1165875
- Columns/JSON paths: 4460
- Inventory method: full local CSV/JSON/XLSX value scan; raw sources remained read-only

## Label Evidence

| level | fields | usable records | interpretation |
|---|---:|---:|---|
| Gold candidate | 0 | 0 | field-confirmed and target-mapped only |
| Silver Operational candidate | 97 | 0 | independent operational discrepancy only |
| Proxy Pattern input | 141 | 0 | measurement input, not truth |
| Unlabeled keyword evidence | 63 | 0 | insufficient time/mapping evidence |

## Route Decision

- Selected route: **Route C**
- Gold usable for target AMI: 0
- Silver Operational usable for target AMI: 0
- Route C means proxy concordance and enrichment only. It does not support fault accuracy, recall, precision, FPR, or specificity claims.

## Mapping

- Target meter values appear in raw AMI sources, but no verified target meter-to-cabinet-to-maintenance/controller chain was found.
- Field-name similarity is not accepted as a verified mapping.

## Claim Boundary

The audit does not manufacture human truth. A keyword, status field, measurement channel, synthetic scenario, or model output is not a confirmed fault.
