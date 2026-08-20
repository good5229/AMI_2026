# v0.10 AMI physical plausibility learning note

## Review identity and scope

- Requested model: `luna`.
- Actual runtime model: GPT-5/Codex. This note must not be attributed to `luna`.
- Reviewer role: Subagent C, v0.10 AMI physical plausibility review.
- Review date: 2026-08-20.
- Scope: current-only grafting of real AMI current channels into controlled data. Energy channels, detector behavior, application code, and raw official-doc rows are out of scope.
- Local evidence inspected: `lightguard_v0_1/data/validation/v10/v10_raw_ami_manifest.json`, `lightguard_v0_1/data/ami_data_quality.csv`, and `lightguard_v0_1/data/ami_meter_profiles.csv` only.

## Primary technical learning

The following official or technical sources were consulted. They establish the data semantics and physical guardrails; they do not provide a substitute rating or baseline for a local meter.

| Source | Learning used by this review |
| --- | --- |
| [KEPCO AMI overview](https://home.kepco.co.kr/kepco/front/html/WZ/2025_01/light.html) | KEPCO distinguishes AMI meter generations and describes collection of line voltage, outages, phase information, and higher-resolution readings. Capability is not evidence that this source window is 1-minute; the manifest's observed cadence remains authoritative. |
| [Itron Gen5 Riva Polyphase Meter specification](https://na.itron.com/documents/44647/3789608/101839SP-01_Gen5%2BRiva%2BPolyphase%2BMeter%2BSpec%2BSheet_Web.pdf/1a65d350-ebe9-9521-db87-bd00f8f08a5c?t=1719428479994&version=1.2) | A polyphase meter can expose total and per-phase energy, per-phase voltage/current waveforms, sub-second RMS current, and separately configured 5/10/15/30/60-minute profiles. Signal type and profile cadence must therefore be retained as separate provenance fields. |
| [Itron ACE6000 technical data](https://na.itron.com/documents/44647/3819706/F15212-4454-ACE6000-DC4-Brochure_Eng_v1.pdf/51c1586c-8c1f-e9c1-2a75-74bf88d21def?t=1711249298528&version=1.2) | Manufacturer-specific minimum and rated currents differ by meter form. The meter exposes per-phase current and phase-failure status, with 5/10/15/30/60-minute sub-interval choices. A generic meter specification must not be used as the local meter's rating. |
| [Green Button ESPI interval and unit semantics](https://www.greenbuttonalliance.org/poweroftenmultiplier) | `intervalLength`, phase, unit, multiplier, and accumulation behavior are semantic fields. Delta interval energy is not interchangeable with instantaneous current; Wh and multiplier must not be rewritten when grafting current. |
| [DLMS/COSEM core specifications overview](https://www.dlms.com/core-specifications/) | OBIS/COSEM identify the measured quantity and its integration/tariff context. A current channel and an integrated active-energy register are different objects and must remain independently traceable. |
| [U.S. DOE EMIS capabilities](https://www.energy.gov/cmei/femp/energy-management-information-system-capabilities) | Expected-usage models are meter-specific and use historical behavior. AMI gap backfill is modeled data and should be tagged as such; it is not measured current and cannot be silently substituted into a graft. |
| [U.S. DOE DTE SmartCurrents final report](https://www.energy.gov/sites/prod/files/2016/10/f33/DTE-SmartCurrents_FINAL_Report_08152014_2.pdf) | The utility study used 15-minute AMI intervals, flagged communication/missing values, retained unrecovered gaps as blank, and excluded incomplete energy totals rather than inventing observations. This supports explicit missingness and no fill. |
| [Schneider Electric current phase-loss guide](https://www.productinfo.schneider-electric.com/tesys_tera_ug/tesys-tera-motor-management-system-user-guide/EN/TeSys-Tera-User-Guide-DOCA0257-01.xml/$/CurrentPhaseLoss-E13EF62F) | A phase-loss alarm is based on a phase current falling below a configured fraction of a full-load current. A blank channel is not that condition, and a threshold cannot be imported without the applicable device rating. |
| [Schneider Electric phantom-voltage FAQ](https://www.se.com/ng/en/faqs/FAQ000133551/) | A high-impedance meter may show phantom voltage after phase loss. Voltage presence alone cannot prove a live phase; missing or suspicious phase channels require explicit quality handling. |
| [Fluke three-phase measurement guidance](https://www.fluke.com/en/learn/blog/clamps/3-phase-power-measurement) | Three-phase current is measured phase by phase, phase order matters, and phase loss can shift current into the remaining phases. A missing phase must not be reconstructed from a balance assumption. |

## Permitted local evidence

The v0.10 raw manifest reports five target meters for 2026-04-01 through 2026-06-30, with interval-end timestamps in `Asia/Seoul`. It reports a median 15-minute cadence, no duplicate timestamps, some 30-minute gaps, and `energy_reconstruction_allowed: false`. The current columns are explicitly `i1_ampere`, `i2_ampere`, and `i3_ampere`; the energy column is `receiving_active_kwh`.

The anonymized profiles identify the topology and meter-specific baselines:

| Meter | Topology | Current channels available in manifest | Current cadence | Energy cadence | Review implication |
| --- | --- | --- | --- | --- | --- |
| B-L-9 | 3P4W | i1, i2, i3 | 15 min | 15 min | All three measured phases are eligible when exact timestamp joins pass. |
| B-L-12 | 3P4W | i1, i2, i3, with 46 missing rows per phase in manifest | 15 min | 15 min | Do not fill. The manifest rate (0.5266%) and anonymized profile rate (0.497%) must be reconciled before automatic whole-window approval. |
| B-L-13 | 1P2W | i1 only; i2 and i3 structurally absent | 15 min | 60 min | i1 may be eligible for a single-phase target. i2/i3 and any inferred three-phase representation are ineligible. |
| B-L-14 | 3P4W | i1, i2, i3 | 15 min | 15 min | All three measured phases are eligible when exact timestamp joins pass. |
| B-L-35 | 1P2W | i1 only; i2 and i3 structurally absent; two i1 gaps | 15 min | 60 min | i1 may be eligible with the two gaps preserved as missing. i2/i3 and any inferred three-phase representation are ineligible. |

The profile baselines are evidence for meter-specific context, not a conversion formula. In particular, contract kW must not be converted to current by assuming voltage or power factor, and a generic manufacturer rating must not be assigned to a local meter.

## Physical constraints for current-only real-signal grafting

### Signal identity

1. The only writable signal is a measured current channel whose source semantic is ampere/RMS current or an explicitly documented current interval statistic. The graft must preserve the source semantic; it must not rename an instantaneous or interval current sample as energy or power.
2. Every written current value must be finite and non-negative. A blank, null, quality-invalid, or unavailable value is missing, never zero.
3. The engine must not calculate kW, kWh, Wh, power factor, or a missing phase from current. It must not use energy to back-calculate current.
4. An observed zero current is allowed only when the source row is present and valid. A missing row or missing channel remains missing.

### Phase-selective eligibility

1. Determine topology from the meter's approved metadata, not from a null pattern. For `3P4W`, `i1`, `i2`, and `i3` are distinct measured phase channels. For `1P2W`, only the observed single phase is eligible; structural nulls in the other two columns are not faults and must not be populated.
2. A phase can be grafted only if its source row has the same meter ID, exact interval-end timestamp, valid current value, and approved source provenance.
3. A three-phase physical interpretation, phase-loss claim, or all-phase detector input is blocked if any required phase is structurally absent, missing at the target timestamp, or has unresolved quality status.
4. If a source has one or more valid phases and another phase is missing, phase-specific copying may proceed only as an explicitly partial signal operation. It must not be described as a complete three-phase waveform.
5. The simultaneous i1/i2/i3 gaps reported for B-L-12 are measurement/data gaps, not evidence of a zero-current outage or a physical phase failure. The engine must preserve them and exclude those timestamps from any complete-phase claim.

### Scaling bounds

1. Production PASS requires identity scaling: `s = 1.0`. This is the only bound supported by the present evidence for a real-signal graft.
2. If a research-only transformed-current mode is separately registered, its hard envelope is `0.80 <= s <= 1.20`, with a per-meter and per-phase audit record. This envelope is a review bound, not a claim about meter accuracy or rated current.
3. Any `s != 1.0` is BLOCKED unless the exact local meter model/rated current, source quantiles, and meter-specific baseline envelope are present and the transformed value remains within the exact rated-current limit. The Itron examples are not acceptable substitutes for those local limits.
4. Scaling must not turn a missing value into a number, create a new phase, create an energy value, or be applied selectively to hide a phase imbalance. If a transformed current is used, its provenance must say `derived_current`, not `measured_current`.

### Energy-channel immutability

1. Before/after checks must show byte- or value-identical energy values, timestamps, units, multipliers, accumulation semantics, and missingness masks for every untouched energy field.
2. No energy interpolation, reconstruction, resampling, scaling, phase summation, or row insertion is allowed. `energy_reconstruction_allowed: false` is a hard gate.
3. If current-only grafting changes row ordering or timestamp keys, the engine must fail the energy identity check rather than silently realign energy.
4. Current-only physical plausibility does not imply energy conservation. The output must not be used to claim that the unchanged energy channel is physically implied by the grafted current.

### Cadence and timestamp alignment

1. Use the manifest's interval-end semantics, `Asia/Seoul` timezone, and normalized next-midnight representation for source `24:00`. Never shift an interval to its start or reinterpret local time as UTC.
2. Join on `(meter_id, timestamp, phase)` with one-to-one keys. No duplicate source timestamps, forward fill, interpolation, or 15-to-60/60-to-15 resampling is allowed.
3. The current source cadence is 15 minutes for this review. The 60-minute energy cadence reported for B-L-13 and B-L-35 is irrelevant to current grafting and must not be used to alter current timestamps.
4. A 30-minute gap is an explicit missing interval. The engine may leave the target unchanged at that timestamp, but it may not insert a synthetic row to make the grid look complete.

### Missing-phase handling

1. Preserve missingness as missing with a quality/provenance flag. Do not encode missing as `0 A`.
2. Do not use the balanced-system shortcut to calculate an unconnected phase. That is a meter configuration calculation, not a measured source row.
3. A phase-specific detector test must declare which phases are present. A complete three-phase test must require all three valid channels at every evaluated timestamp.
4. Any phase loss or outage interpretation requires independent voltage/status/event evidence. Current-channel absence alone is a data-quality condition.

### Provenance review

The engine must carry, at minimum, source manifest schema/version, source digest, source meter ID, source timestamp semantics/timezone, source column semantic, source topology, source cadence, source row/quality status, operation (`identity_current_copy` or `derived_current`), scale, and target timestamp. The manifest says the raw source remains untracked and that rows were not copied into the manifest; these facts must remain true. A provenance mismatch, source-denominator mismatch, or unapproved topology is BLOCK.

## Review conclusion

The physically defensible operation is a phase-selective, current-only, identity copy at exact source timestamps, with explicit missingness and an unchanged energy channel. Anything that fills structural phases, infers energy, changes cadence, or uses a generic meter rating is not a real-signal graft and must be blocked.

