# LightGuard v0.12R Domain Evidence Review

## 1. Scope and freeze

This report is the LUNA Subagent B domain-literature deliverable. It preserves the v0.11 Route C boundary: available AMI data do not provide usable Gold or independent Silver operational labels. The report therefore evaluates whether four patterns are scientifically defensible anomaly signs and inspection candidates. It does not estimate fault probability or field accuracy.

The v0.12R literature search protocol was frozen before screening. Literature grade was assigned independently of H1, independent proxy scores, canonical-six membership, and blinded human ratings. No raw data, v0.11 artifact, registry, evidence matrix, test, or Git state was changed by this review.

## 2. Starting reference verification

The supplied Smart City Gnosis item is traceable to the IEEE record:

| Field | Verified value |
|---|---|
| Title | *IoT-based Efficient Streetlight Controlling, Monitoring and Real-time Error Detection System for Smart Cities in Bangladesh* |
| Authors | A.T.M. Mustafa Masud Chowdhury; Jeenat Sultana; Md Sakib Ullah Sourav |
| Conference | 2023 International Conference on Electrical, Computer and Communication Engineering, ECCE 2023, Chittagong, Bangladesh; 3rd conference edition in indexed records |
| DOI | [10.1109/ECCE57851.2023.10101600](https://doi.org/10.1109/ECCE57851.2023.10101600) |
| IEEE record | [IEEE Xplore document 10101600](https://ieeexplore.ieee.org/document/10101600) |
| Indexed cross-check | [Smart City Gnosis](https://smartcity.efri.uniri.hr/article.php?id=33966), [J-GLOBAL](https://jglobal.jst.go.jp/en/detail?JGLOBAL_ID=202302287091582525), [arXiv manuscript](https://arxiv.org/abs/2211.00074) |
| Source grade | Quality A, L3 direct streetlight/control relevance |

### What the paper calls an error

The original prototype combines an LDR, current sensing, traffic sensing, a microcontroller, and network reporting. The demonstrated error case is produced by covering the LDR for Street Light 3 in the laboratory. The controller then reports an inconsistent light/sensor state while the lamp is on. This is a state/sensor mismatch experiment.

It is not equivalent to:

- a confirmed lamp or controller failure in the field;
- a current-only cabinet fault label;
- a three-phase asymmetry diagnosis;
- a maintenance or repair outcome;
- a calibrated fault probability.

The paper also reports an approximately 60 percent energy-cost reduction estimate using city-corporation context. That result is an energy-management comparison, not an error-detection accuracy statistic. The distinction is essential for LightGuard.

## 3. Evidence by pattern

| Pattern | Direct support | Mechanism support | Method judgment | Final grade |
|---|---|---|---|---|
| Daytime full activation | IEEE ECCE LDR/state mismatch; DOE/PNNL current, power, and service-disruption monitoring; Lee and Huang repeated illumination maps | Expected ambient/schedule state can disagree with observed lighting/electrical behavior; causes remain non-unique | Strong as a multi-signal inspection candidate; require context and persistence | A / L3 direct |
| Persistent partial-load deviation | DOE/PNNL duration study; Villar-Rodriguez real utility load profiles; Capozzoli time-window anomaly detection; NIST CUSUM | Sustained departures from an in-control or meter-local expected process are more actionable than isolated spikes | Reasonable with frozen duration, causal baseline, transition exclusion, and missingness handling | A / L2 direct |
| Phase-selective activation | Micolta Mosquera FEM/lab sequence analysis; Bouzid controlled disturbance compensation; IEEE 1159 monitoring practice | Phase asymmetry and negative sequence can be diagnostic variables, but observed asymmetry is a mixture of causes | Reasonable only as phase-asymmetry observation unless phasor measurement and circuit mapping support sequence claims | A / L2 electrical |
| Meter-relative historical baseline | Villar-Rodriguez load-curve profiling; Capozzoli time-of-day windows; Zhang utility baseline comparison; NIST CUSUM | Expected behavior is meter/context dependent; residual persistence can be scored against historical normal | Strongly appropriate for triage if pre-event-only, meter-local, seasonal, and coverage-aware | A / L2 direct |

## 4. Source-by-source method and transfer audit

### 4.1 Streetlight and expected-state evidence

#### ECCE 2023

The paper's sensing architecture is a useful conceptual match for the LightGuard chain: external light context, electrical consumption, and controller status are different observations. Its strongest contribution is not the word “fault,” but the demonstration that disagreement between an expected ambient-light state and an observed lamp state can be surfaced automatically.

The method cannot establish whether an LDR is obstructed, miscalibrated, or failed; whether the controller schedule is wrong; or whether the lamp is physically defective. The artificial LDR-cover intervention has known cause, but LightGuard's AMI observations do not. It therefore supports `expected-state/current mismatch anomaly sign`, not `fault`.

#### DOE/PNNL

The DOE/PNNL study is the strongest direct electrical support in this review. Its test bed used 12 luminaires from 12 manufacturers and seven LED-driver manufacturers, with ten controlled undervoltage conditions from 120 VAC to 60 VAC. Long duration was greater than one minute. Human observation supplied the service-disruption reference, while circuit-level electrical measurements were evaluated for automated detection.

The result is a mechanism map, not a universal threshold table. All 12 units showed the high-current disruption at evaluated conditions, five showed low-light behavior, and six showed intermittent output. Voltage alone was insufficient to distinguish the disruption classes; current and power added diagnostic information. The authors explicitly note that additional data are needed to diagnose cause.

This directly supports a LightGuard rule that a daytime full-load event should be described as a persistent service-state mismatch and routed for inspection, especially when current, power, expected schedule, and ambient context agree. It does not prove a lamp fault because the feeder can be affected by voltage, wiring, controller, meter, or other load causes.

#### Lee and Huang

The Hitchhiker study demonstrates a separate but complementary route: repeated measured illumination along the same route, mapped in space and compared before and after a known government repair. The 10 Hz measurements and four-before/four-after map design show why repeated observations and operational follow-up matter.

The method measures optical outcome, not cabinet current. It supports the architecture of an inspection workflow and the need for external outcome confirmation. It cannot validate a current-only event or distinguish a lamp from an obstruction, weather, sensor, or route artifact.

### 4.2 Persistence and partial deviation

Villar-Rodriguez et al. use real Spanish utility smart-meter traces and emulate anomalous/non-technical-loss events. Their elastic time-series comparison is useful because timing shifts and profile shape matter in load data. The source carefully frames outliers as cases for utility action rather than as one physical cause.

Capozzoli et al. learn patterns at specific time windows using enhanced SAX and test two real building cases. Their post-mining diagnosis is explicitly preliminary and depends on additional HVAC data. This is directly relevant to LightGuard's need to keep daytime, night, transition, and weather-sensitive windows distinct.

NIST's CUSUM method explains why cumulative residual evidence can detect small mean shifts better than a single Shewhart observation. Its alpha, beta, shift-size, and control-limit framing is a methodological guardrail: persistence thresholds require a defined in-control reference and an explicit false-alarm tradeoff.

Together these sources make a persistent partial-load anomaly rule scientifically reasonable, but only as a meter-local deviation. The rule should not suppress data quality or schedule alternatives, and it should not call the residual a partial lamp failure without field outcome.

### 4.3 Phase-selective and negative-sequence evidence

The negative-sequence literature provides electrical mechanism support but also the most important transfer warning. Micolta Mosquera et al. derive sequence components from phase phasors and study inter-turn short circuits with FEM and laboratory experiments while varying voltage unbalance and load. Bouzid et al. experimentally compensate negative-sequence contributions from inherent asymmetry, sensor inaccuracy, and voltage unbalance before isolating a motor-fault component.

These studies show that phase asymmetry can carry diagnostic information, but they do not show that raw asymmetry has a unique cause. IEEE 1159-2019 provides the appropriate vocabulary for polyphase monitoring and source/load interaction, not an event-level fault label.

The present LightGuard pattern must therefore be named `phase-selective anomaly sign` or `phase-current asymmetry observation`. The term `negative sequence` is permitted only after synchronized phase voltage/current quantities, instrument provenance, phase ordering, and a validated Fortescue calculation are available. Even then, the output remains a diagnostic candidate until controller, feeder, and maintenance outcomes are checked.

### 4.4 Meter-relative historical baseline

Zhang et al. treat baseline as a counterfactual estimate of what load would have been under normal conditions, using correlated normal-day cohorts and actual utility data. This is not identical to LightGuard's meter-local baseline, but it validates the general principle that “normal” must be defined relative to comparable load behavior.

Capozzoli's unequal time windows support preserving the distinctive time structure of streetlight operations. Villar-Rodriguez supports shape-aware profile comparison. NIST supports cumulative persistence. The combined method is more defensible than a global current threshold, provided LightGuard maintains strict pre-evaluation history, warm-up abstention, seasonal strata, transition handling, and baseline coverage.

## 5. What the literature supports

- A daytime electrical reading inconsistent with a trusted expected lighting state is a plausible anomaly or inspection signal.
- Input voltage, current, power, ambient light, and expected state are complementary evidence, not interchangeable measurements.
- Sustained deviations and cumulative residuals can be more informative for triage than isolated spikes when the baseline and process assumptions are explicit.
- Meter-relative and time-of-day-aware baselines are scientifically preferable to one global threshold for heterogeneous loads.
- Phase asymmetry and negative-sequence quantities are recognized electrical diagnostic variables, but raw asymmetry is confounded and measurement-dependent.
- Repeated external observation and field repair/inspection outcomes are necessary to connect an anomaly sign to a physical event.
- Independent human or operational validation is a separate evidence layer; the literature cannot replace it.

## 6. What the literature does not support

- It does not establish that any of the six v0.11 AMI events is a real fault.
- It does not supply Suyeong cabinet-to-meter mapping, controller state, maintenance records, inspection labels, or repair outcomes.
- It does not justify `fault probability`, `fault rate`, `field accuracy`, `fault recall`, `FPR`, or `specificity` for LightGuard.
- It does not justify transferring a motor negative-sequence threshold to an aggregate streetlight feeder.
- It does not justify copying DOE/PNNL thresholds to a different luminaire, voltage system, aggregation point, or meter.
- It does not justify treating the ECCE laboratory LDR-cover test as field fault validation.
- It does not prove that persistence distinguishes physical failure from a legitimate schedule, controller override, feeder condition, meter drift, or data-pipeline problem.

## 7. Recommended LightGuard evidence wording

| Observed result | Allowed wording | Avoid |
|---|---|---|
| Daytime current near meter's night-on profile | `daytime full activation anomaly sign` | `all lamps failed on` |
| Repeated intermediate load departure | `persistent partial-load deviation` | `partial outage confirmed` |
| One phase active or phase pattern departs from history | `phase-selective anomaly sign` | `negative-sequence fault` unless phasor prerequisites are met |
| Historical residual above a frozen threshold | `meter-relative baseline anomaly` | `fault probability is X%` |
| Several signals agree | `multi-evidence inspection candidate` | `high-confidence actual fault` |

## 8. Required future validation

To move from anomaly sign to a Gold/Silver operational label, a prospective field design should capture:

- immutable cabinet-to-meter and phase mapping;
- rated fixture/lamp count and controller/photocell schedule;
- synchronized voltage, current, power, and phase measurement provenance;
- ambient-light or astronomical context and planned overrides;
- maintenance ticket, inspection observation, repair action, and adjudication time;
- data-quality and communication-chain status;
- a blinded review or independent field outcome that is collected without exposing H1/proxy scores.

The outcome should be time-bounded and cause-specific where possible. If the outcome only confirms a service disruption, retain that label as Silver Operational and do not silently upgrade it to Gold physical fault.

## 9. Review conclusion

The four LightGuard patterns have a defensible literature basis as anomaly signs, with strongest direct support for expected-state/current mismatch, persistence-aware streetlight electrical monitoring, and meter-relative historical comparison. Phase-selective behavior has plausible electrical diagnostic meaning but the current LightGuard data should not be described as negative-sequence current without phasor-capable measurement.

The methods are scientifically reasonable for inspection prioritization, not for fault confirmation. The v0.11 Gold/Silver gap remains open, and this literature review does not narrow that claim boundary.

## References

1. Chowdhury, A.T.M.M.M., Sultana, J., and Sourav, M.S.U. (2023). *IoT-based Efficient Streetlight Controlling, Monitoring and Real-time Error Detection System for Smart Cities in Bangladesh*. ECCE 2023. DOI: [10.1109/ECCE57851.2023.10101600](https://doi.org/10.1109/ECCE57851.2023.10101600).
2. Waghale, A. and Poplawski, M. (2023). *On the Way: Automated fault detection and diagnostics for LED street lighting systems*. U.S. DOE/PNNL, *LD+A*. [Official source](https://www.energy.gov/cmei/ssl/articles/way-automated-fault-detection-and-diagnostics-led-streetlighting-systems).
3. Lee, H.-C. and Huang, H.-B. (2015). *A Low-Cost and Noninvasive System for the Measurement and Detection of Faulty Streetlights*. IEEE TIM, 64(4), 1019-1031. DOI: [10.1109/TIM.2014.2361551](https://doi.org/10.1109/TIM.2014.2361551).
4. Villar-Rodriguez, E., Del Ser, J., Oregi, I., Bilbao, M.N., and Gil-Lopez, S. (2017). *Detection of non-technical losses in smart meter data based on load curve profiling and time series analysis*. *Energy*, 137, 118-128. DOI: [10.1016/j.energy.2017.07.008](https://doi.org/10.1016/j.energy.2017.07.008).
5. Capozzoli, A., Piscitelli, M.S., Brandi, S., Grassi, D., and Chicco, G. (2018). *Automated load pattern learning and anomaly detection for enhancing energy management in smart buildings*. *Energy*, 157, 336-352. DOI: [10.1016/j.energy.2018.05.127](https://doi.org/10.1016/j.energy.2018.05.127).
6. Bouzid, M.B.K., Champenois, G., and Tnani, S. (2018). *Reliable stator fault detection based on the induction motor negative sequence current compensation*. *IJEPES*, 95, 490-498. DOI: [10.1016/j.ijepes.2017.09.008](https://doi.org/10.1016/j.ijepes.2017.09.008).
7. Micolta Mosquera, J.E., Oslinger, J.L., and Franco, E. (2016). *Contributions to the online fault diagnosis of interturn short circuit in three-phase induction motor by means of negative sequence components*. *DYNA*, 83(198). DOI: [10.15446/dyna.v83n198.50378](https://doi.org/10.15446/dyna.v83n198.50378).
8. IEEE Power and Energy Society (2019). *IEEE Recommended Practice for Monitoring Electric Power Quality*, IEEE 1159-2019. [IEEE SA](https://standards.ieee.org/ieee/1159/6124/).
9. Zhang, Y., Chen, W., Xu, R., and Black, J. (2016). *A Cluster-Based Method for Calculating Baselines for Residential Loads*. IEEE TSG, 7(5), 2368-2377. DOI: [10.1109/TSG.2015.2463755](https://doi.org/10.1109/TSG.2015.2463755).
10. NIST (n.d.). *CUSUM Control Charts*. Engineering Statistics Handbook, section 6.3.2.3. [NIST](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm).
11. Dutta, P., Parvin, M., Saha, R., and Chakraborty, S. (2026). *Electrical Current Signature-Based Machine Learning Models for Streetlight Fault Prediction in Smart City Infrastructure*. *Informatica*, 50(2). DOI: [10.31449/inf.v50i2.8972](https://doi.org/10.31449/inf.v50i2.8972).
