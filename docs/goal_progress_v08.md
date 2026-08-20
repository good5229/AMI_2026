# LightGuard v0.8 Goal Progress

## Current Phase

Checkpoint 1 and Checkpoint 2 complete. Checkpoint 3 calibration generation and
candidate detector implementation is next.

## Concrete Deliverable

Frozen v0.7 regression baseline plus independently researched failure matrix,
fractional/blocked v0.8 design, and Chungju official load-data recovery decision.

## Completed Evidence

- `./scripts/v07_preflight.sh`: PASS
- Artifact contracts: v0.5, v0.6, v0.7 PASS
- Flutter analyze: no issues
- Flutter tests: 20 passed
- Web release build: PASS
- Android release APK: PASS, 52.2MB
- v0.7 baseline commit: `383c91e2c22d9364232c80683b6f8e4b6dc09d35`
- v0.7 freeze manifest created with key artifact SHA-256 values

## Active Agents

None. Wave 1 workers completed and were closed.

## Blockers

None. Actual Gangneung/Chungju field AMI remains unavailable by known evidence,
but does not block controlled confirmatory validation.

## Frozen Artifacts

- `lightguard_v0_1/data/validation/v08/v07_freeze_manifest.json`
- v0.7 96 scenarios are regression-only and prohibited from v0.8 tuning.
- `lightguard_v0_1/data/validation/v08_design_matrix.csv`
  SHA-256 `9fba439a9bd22d184e6a705af559a9b43a39fb4b9498cfa3d3a50c2f5853dbb0`.

## Last Successful Command

`python3 scripts/build_v08_design.py --check`

## Next Execution Step

Commit the frozen Wave 1 evidence, generate the calibration set from the design
matrix, freeze its SHA-256, and tune at most C1/C2/C3 without reading confirmatory
outcomes.
