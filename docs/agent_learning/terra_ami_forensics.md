# TERRA Actual AMI Replay Forensics, v0.5

## Scope and provenance

This note investigates only the six anonymized competition B-line AMI replay
events. It does not join those records to Busan weather/solar context or to
Suyeong assets, and it does not change a parser, detector, canonical event, or
frozen validation artifact.

The task assignment identified this worker as `gpt-5.6-terra`. The execution
environment exposed no independently verifiable runtime model identifier, so
that assignment label is recorded as task provenance rather than an independent
model-identity attestation.

The source-of-truth chain was:

1. Ignored workbook: `official_docs/AMI Data Sample/2-2_MDMS..._B...xlsx`,
   sheet `B선로 AMI DATA`.
2. Canonical event table: `lightguard_app/assets/data/ami_events.csv`.
3. Replay manifest and six replay CSVs under
   `lightguard_app/assets/data/ami_event_windows/`.
4. Extraction: `scripts/extract_ami_event_windows.py`.
5. Legacy comparison: `scripts/run_v04_validation.py`, `replay_regression()`.
6. Detector definition: `lightguard_v0_1/src/build_lightguard_v01.py`, where
   `total_current` is the sum of non-null `i1`, `i2`, and `i3` values for one
   record.

The six committed replay files cover 110 source rows. The workbook source-row
numbers in the manifest were checked directly: all 110 were present and the
exported `active_energy_kwh`, `i1`, `i2`, and `i3` values match the workbook.

## External technical evidence

All URLs below were accessed on 2026-08-20. They establish general AMI/MDMS
handling principles; they do not override the supplied workbook's own schema.

| Source | Exact URL | Relevant point |
|---|---|---|
| Oracle Utilities, Interval Data File Specifications | https://docs.oracle.com/en/industries/utilities/opower-platform/data-transfer/interval-data-file-specifications.html | Interval usage has a unit and fixed interval length; this format labels usage timestamps as interval ends and illustrates 15-minute records. |
| Oracle Utilities, Configurable Consumption Extracts | https://docs.oracle.com/en/industries/energy-water/meter-solution-cloud-service/2510/mscs-user-guides/Topics/D1_AG_Data_Extracts_ConfigurableConsumptionExtracts.html | Interval duration is explicit; the first interval's measurement time is start plus interval size. This demonstrates why timestamp convention must be known before shifting values. |
| Korea Energy Agency, public-institution electricity monitoring notice | https://min24.energy.or.kr/gb/public/dashboard/dashboard.do | AMI communication errors can be corrected later; AMI failure can leave uncorrectable missing periods. Missingness must therefore be represented, not silently converted to zero. |
| Itron IEE, Interval validation rules | https://docs.itrontotal.com/IEEMDM/Content/Topics/252711.htm | MDMS validation explicitly checks gaps, overlapping intervals, reference-channel alignment, and meter-clock alignment. |
| KEPCO, AMI usage case | https://home.kepco.co.kr/kepco/front/html/WZ/2024_01/light.html | KEPCO describes remote AMI readings at 15- to 60-minute cadence for operational confirmation. |

## What the workbook can and cannot establish

The B-line workbook has a `시간` column, received active energy
`유효전력량(kWh)`, and phase-current columns `Ia`, `Ib`, and `Ic`. Its rows form
15-minute labels in every replay window. The canonical event table explicitly
calls the energy attribution method `interval-end overlap + median by
time-of-day`.

The workbook itself does not document whether its `시간` label is an
interval-start or interval-end convention, nor whether each current is an
instantaneous sample or an interval statistic. Therefore this investigation
does not shift current timestamps and never converts kWh to amperes. The
interval-end wording remains evidence for the energy-attribution method only.

## Six-event findings

Every event has complete expected 15-minute labels inside its replay window and
zero duplicate timestamps. `B-L-35` and `B-L-13` have no `i2`/`i3` values in
their windows, but each row has an `i1` value; these are phase-field omissions,
not wholly missing current rows.

For all six events, the canonical value equals the maximum, within the canonical
event labels, of `sum(non-null i1, i2, i3)`. The maximum remains the same when
using the full replay window or one 15-minute label either side of the event.
There is no parser, extraction, timestamp-alignment, whole-row-gap, or duplicate
timestamp evidence for any of the six cases.

The v0.4 comparison instead calculated the maximum *individual phase* observed
anywhere in the replay window and compared it to the canonical *per-record sum
of available phases*. That comparison is equal only for the two I1-only events:

| Event | Canonical sum peak (A) | v0.4 individual-phase peak (A) | Result |
|---|---:|---:|---|
| AMI-EVT-237615b73a | 16.550 | 16.550 | legacy pass |
| AMI-EVT-d406cc5296 | 7.080 | 2.940 | legacy mismatch |
| AMI-EVT-fda2dd8737 | 43.158 | 16.429 | legacy mismatch |
| AMI-EVT-f394b2a542 | 48.736 | 18.594 | legacy mismatch |
| AMI-EVT-4ada00d8f3 | 6.490 | 3.990 | legacy mismatch |
| AMI-EVT-d706634ed1 | 5.900 | 5.900 | legacy pass |

Thus `peak consistency = 2/6` is preserved as the historical result of the
legacy, non-comparable metric. It is not evidence of a detector failure.

## Recommended adjudicated metric

Use a separate replay-integrity metric, never a replacement for the v0.4 field:

```text
canonical_aggregate_peak_A =
  max over event record timestamps [sum of non-null Ia, Ib, Ic for that record]

adjudicated_consistent =
  abs(replay_event_aggregate_peak_A - canonical_peak_current_a)
  <= max(0.05 A, 0.02 * canonical_peak_current_a)
```

This is a like-for-like comparison with the detector's existing `total_current`
definition. It produces `6/6` source/replay consistency on these six records,
but it is not a field-accuracy metric, a fault-confirmation metric, or a reason
to modify the historical `2/6` value. Current aggregation must continue to
retain per-phase availability: summing only observed phases is appropriate for
reproducing the canonical detector, while a production electrical-load estimate
should separately flag absent phases rather than treating them as zero.

The per-event evidence and adjudication are in
`lightguard_v0_1/reports/v05/peak_consistency_forensics.csv` and
`lightguard_v0_1/reports/v05/peak_consistency_adjudication.md`.
