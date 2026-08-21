# LightGuard v0.3 context data provenance

## Source separation

- Municipal assets are public-data inventory records. Suyeong has 204 cabinets.
- Scenario signals are controlled validation inputs for 46 Suyeong cabinets; 158 cabinets have no signal.
- Municipal AMI mappings remain zero in Suyeong, Gangneung, and Chungju.
- Competition AMI is anonymized and is never joined to Suyeong assets, Busan KASI, or Busan KMA context.

## KASI solar context

- Provider: Korea Astronomy and Space Science Institute.
- API: `RiseSetInfoService/getLCRiseSetInfo`.
- Purpose: location-based sunrise, sunset, morning civil twilight, and evening civil twilight.
- Dates: 2026-01-14, 2026-04-15, 2026-07-15, 2026-10-15.
- Location: arithmetic mean of all 204 cabinet coordinates; latitude 35.16065889316176, longitude 129.1153977335784.
- Mapping: `sunrise -> sunrise`, `sunset -> sunset`, `civilm -> civil_twilight_start`, `civile -> civil_twilight_end`.
- Snapshot: `lightguard_v0_1/data/context/kasi_solar_context_2026.json`.
- Failure handling: bounded retry, serialized error code, null official fields, `context_source = unavailable`; no internal-formula fallback.

## KMA weather context

- Provider: Korea Meteorological Administration.
- API: `AsosHourlyInfoService/getWthrDataList`.
- Station: 159, Busan.
- Dates: 2026-01-14, 2026-04-15, 2026-07-15, 2026-10-15.
- Mapping: `tm -> timestamp`, `ta -> temperature`, `rn -> precipitation`, `hm -> humidity`, `dc10Tca -> cloud_amount`, `ss -> sunshine`, `icsr -> solar_radiation`, `vs -> visibility`, `ws -> wind_speed`.
- Missing observations remain null. Future dates remain explicitly unavailable.
- Snapshot: `lightguard_v0_1/data/context/kma_asos_busan_2026.json`.
- Failure handling: bounded retry and explicit unavailable errors; synthetic weather is never substituted.

## Current retrieval state

The 2026-08-20 retrieval collected all four KASI dates and 72 KMA hourly observations for the three elapsed representative dates. The KMA service is active after renewal. The 2026-10-15 observation remains explicitly unavailable because it is a future date. API keys are never written to source, snapshots, logs, documentation, commits, or PR text.

## Controlled validation

- Frozen set: 46 injected anomalies and 158 normal controls from the same 204-cabinet inventory.
- Hard negatives: solar-boundary activation, sunrise residual, adverse-weather context, controlled normal partial operation, and transient spike.
- M0-M3 use one canonical case-content SHA-256. Missing official snapshots make dependent models unavailable rather than triggering synthetic substitution.
- Weather is a ranking confidence modifier. It cannot clear an inspection candidate by itself.
- In this run M3 produced the same FPR and Top-K metrics as M2; no additional weather benefit is claimed.

## Anonymized competition AMI replay

- Source: ignored B-line MDMS workbook supplied for the competition.
- Extraction: event start minus two hours through event end plus two hours.
- Fields: timestamp, meter ID, I1, I2, I3, active energy, and original workbook row number.
- Blanks and duplicate source timestamps are preserved; interpolation and fabricated rows are prohibited.
- The committed manifest stores the source workbook SHA-256, source sheet, extraction bounds, and row ranges, but not the workbook.
