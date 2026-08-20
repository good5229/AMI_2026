# v0.12R Evidence Synthesis and Circularity Audit

**Role:** Subagent C, TERRA, Evidence Synthesis and Circularity Auditor  
**Date:** 2026-08-21  
**Inputs:** frozen [search protocol](../../lightguard_v0_1/reports/v12r/v12r_literature_search_protocol.md), [TERRA methodology](terra_literature_methodology.md), [LUNA domain review](luna_domain_literature.md), and [domain evidence review](../../lightguard_v0_1/reports/v12r/v12r_domain_evidence_review.md).  
**Output matrix:** [v12r_literature_evidence_matrix.csv](../../lightguard_v0_1/data/validation/v12r/v12r_literature_evidence_matrix.csv)

## Independent decision

The research logic is scientifically reasonable for identifying **proxy anomaly signs** and forming **inspection candidates**. It is not scientifically reasonable to claim a LightGuard event is a physical fault, calculate a fault probability, or report field precision, recall, false-positive rate, or specificity. No reviewed study supplies the missing Suyeong-gu join among an AMI meter, cabinet/asset/phase topology, controller or photocell state, and a time-bounded field outcome.

This synthesis did not inspect or use H1, proxy scores, canonical-six membership, scenario outcomes, or human-review ratings. Literature support is not an input to a detector score and detector results are not an input to this matrix.

## Method

I reconciled the A/B records into 21 unique sources. The Lee and Huang paper appears in both prior reviews but is counted once. Each source was audited for bibliographic identity, target domain, measurement, anomaly definition, label origin, field versus laboratory validation, transfer assumptions, confounding, and evaluation leakage.

`L3` means direct streetlighting/current/expected-state relevance, `L2` an analogous AMI or electrical mechanism, `L1` an evaluation or measurement-process guardrail, and `L0` no transferable positive support. These are relevance grades, never probabilities or validation metrics. The current-signature simulation remains as an `L0` limitation record so synthetic evidence cannot be counted as field evidence.

## Metadata and study-design reconciliation

The core titles, years, and DOIs in A/B are consistent. The ECCE reference resolves to IEEE document `10101600`, DOI `10.1109/ECCE57851.2023.10101600`; its demonstrated error is a laboratory LDR-cover intervention, not an AMI-only field-maintenance fault. The 2025 Scientific Reports paper, DOI `10.1038/s41598-025-19414-8`, uses a real road-lighting platform but labels anomalous observation periods without a recoverable root-cause or repair-outcome protocol. Its F1 and selected thresholds are therefore non-transferable.

DOE/PNNL is a controlled undervoltage experiment, not a field cohort. It establishes that a common electrical disturbance can yield different service disruptions and that voltage alone does not diagnose cause. Its device-specific current, power, voltage, and duration thresholds must not be copied to Suyeong cabinet AMI. Ayaz et al. supports only a topology-dependent group-localization assumption; its assertion of high certainty is not independent field validation.

The fraud/non-technical-loss studies are useful comparators, including some externally inspected outcomes, but their intervention process and class definitions are not streetlight faults. Benchmark papers are leakage guardrails, not LightGuard validation. Measurement and CUSUM references justify a defined in-control reference and uncertainty boundary, not an asset-fault label.

## Pattern verdicts

### P1: Expected-state/current mismatch

This is reasonable only when expected state is independently evidenced by a controller log, verified photocell/ambient-light measurement, or authoritative operational context. The literature supports a multi-signal inspection workflow, not astronomical-time-only inference or root-cause diagnosis. Approved override, dimming, controller/sensor error, feeder conditions, meter error, communication delay, and unrelated load remain alternatives.

### P2: Persistent meter-relative load departure

Meter-local, time-aware residuals and sustained departures are valid screening ideas only with a causal pre-event baseline, adequate history and coverage, seasonal/schedule strata, transition exclusion, and a frozen threshold. A CUSUM-style rule additionally needs its in-control mean, variability, design shift, and false-alarm tradeoff. Persistence is not specific to lamp failure.

### P3: Phase-current asymmetry observation

Negative-sequence studies require synchronized phase phasors, phase order, voltage/current provenance, and a validated Fortescue calculation. RMS magnitudes per phase do not provide these inputs. The current pattern must therefore be `phase-current asymmetry observation` or `phase-selective anomaly sign`, never `negative-sequence current`, `negative-sequence fault`, or a failed-lamp diagnosis. Supply unbalance, load mix, topology, CT error, inherent asymmetry, and mapping error are unresolved confounders.

### P4: Meter-relative historical baseline

Baseline construction is counterfactual estimation, not a label. It supports a frozen past-only meter-relative reference, not validation by detector-derived normality, inclusion of the scored period, or pooling unrelated meters until local variation is erased.

## Circularity and claim gates

- Laboratory injection cannot validate real Suyeong AMI faults or calibrate fault probability.
- A detector output, injection label, canonical membership, or unblinded review cannot be ground truth for the same pattern.
- Repeated references to a broad abnormal-load concept are not independent confirmation of one fault mechanism.
- Theft inspection labels do not transfer to road-lighting fault labels.
- Benchmark F1, study-selected thresholds, and device-specific thresholds are not portable.

LightGuard may present a time- and meter-bounded observed departure as an `anomaly sign` and route it as an `inspection candidate`, while retaining measurement, baseline, expected-state, missingness, and alternative-explanation evidence. Gold or Silver requires authoritative topology/context and an independent time-aligned operational outcome.

## Final assessment

The A/B conclusion is upheld with two conservative clarifications: the 2025 road-lighting study has direct domain relevance but no recoverable field root-cause validation, and RMS-only phase current is not a negative-sequence measurement. The v0.12R evidence layer is defensible only if the matrix's allowed/prohibited claims are enforced. It does not close the Gold/Silver gap or validate any H1/proxy result.
