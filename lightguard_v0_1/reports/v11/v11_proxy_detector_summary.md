# v0.11 H1-Independent Proxy Detector Run

## Scope

- Route: `C`; full label audit sealed usable Gold=`0`, usable Silver=`0`.
- Input: raw B-line `i1/i2/i3` currents only.
- Excluded by design: H1, solar, weather, asset attributes, scenarios, prior detector output, and operational outcomes.
- Calibration: `2026-04-01` through `2026-04-30`.
- Scoring: `2026-05-01` through `2026-06-30`.
- v0.10 preservation reference: `d34d8323b3742c9116060d9548bd29c18750cb1f`.

## Seal order

1. Freeze file SHA-256: `09d7858b1c98a4380638a44c956d17f10c18858517096dc06bbb8321d9cdc454`.
2. Independent May-June score SHA-256: `f29224de1ba7f10f463930a5bc05eda17664e060ca9bbe89bda4bf59a2d5e16a`.
3. Only after step 2, join the six canonical rows and construct controls.

## Produced coverage

- Score rows: `29181`.
- Three-phase eligible score rows: `17531`.
- Bootstrap: `2000` meter-day cluster resamples with seed `202611`.
- Blinded packet availability: `{"S0_NO_PROXY": {"available": 21848, "requested": 15, "selected": 15}, "S1_RESIDUAL": {"available": 568, "requested": 15, "selected": 15}, "S2_PERSISTENCE": {"available": 6322, "requested": 15, "selected": 15}, "S3_PHASE_PATTERN": {"available": 443, "requested": 15, "selected": 15}}`.

## Interpretation guard

Every output is a raw-current proxy anomaly-sign artifact. Detector overlap, matched-control contrast, and bootstrap intervals describe internal measurement behavior only. No field-outcome evaluation is available in this route.
