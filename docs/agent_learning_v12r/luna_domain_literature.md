# Agent Learning Note

## Role

v0.12R Subagent B, LUNA, Streetlight and Electrical Mechanism Literature Reviewer.

The task was to learn and critically validate research methods for four LightGuard patterns:

1. Daytime full activation or expected-state/current mismatch.
2. Persistent partial-load deviation rather than a one-sample spike.
3. Phase-selective activation and three-phase asymmetry, including the limits of negative-sequence interpretation.
4. Meter-relative historical, time-of-day baseline deviation.

The review was conducted after the v0.12R search protocol was frozen and without using H1, proxy scores, canonical membership, or human-review outcomes to select or grade sources.

## Actual Model

GPT-5, operating in the assigned LUNA Subagent B role.

## Search Queries

The frozen query families were used without result-dependent reformulation:

- `street-light daytime operation`
- `streetlight fault detection current sensor`
- `streetlight ambient light + current monitoring`
- `schedule mismatch`
- `lighting energy waste abnormal operation`
- `smart meter persistent load deviation anomaly`
- `partial load anomaly detection`
- `sustained current deviation fault monitoring`
- `three phase current imbalance fault diagnosis`
- `negative sequence current fault detection`
- `phase current asymmetry anomaly`
- `power quality phase imbalance diagnostics`
- `smart meter time-of-day baseline anomaly`
- `load profile deviation detection`
- `robust residential/commercial load anomaly`

Metadata was checked against the original publisher, IEEE, DOI, official government, or institutional full-text record where available. Search snippets and secondary summaries were not used as the sole support for a core claim.

## Sources Reviewed

### S1. Starting item: IEEE ECCE 2023 streetlight paper

- Title in IEEE metadata: *IoT-based Efficient Streetlight Controlling, Monitoring and Real-time Error Detection System for Smart Cities in Bangladesh*.
- Authors in IEEE and indexed metadata: A.T.M. Mustafa Masud Chowdhury, Jeenat Sultana, and Md Sakib Ullah Sourav. Some mirrors display a shortened or alternate first-name form; the IEEE record is the authoritative citation.
- Conference: 2023 International Conference on Electrical, Computer and Communication Engineering, ECCE 2023, Chittagong, Bangladesh. It is the 3rd ECCE according to the indexed conference record.
- DOI: [10.1109/ECCE57851.2023.10101600](https://doi.org/10.1109/ECCE57851.2023.10101600).
- Original publisher record: [IEEE Xplore document 10101600](https://ieeexplore.ieee.org/document/10101600).
- Independent metadata cross-check: [Smart City Gnosis record 33966](https://smartcity.efri.uniri.hr/article.php?id=33966), [J-GLOBAL record](https://jglobal.jst.go.jp/en/detail?JGLOBAL_ID=202302287091582525), and the authors' [arXiv manuscript](https://arxiv.org/abs/2211.00074).
- Source type and grade: peer-reviewed IEEE conference paper, Quality A, direct streetlight relevance L3.
- Research logic: combine a light-dependent resistor for external-light/sunlight state, current sensing for electrical consumption, ultrasonic sensing for traffic, a microcontroller, and network reporting/control. The system adjusts brightness and reports a local state inconsistency.
- Error definition actually demonstrated: in the laboratory prototype, the LDR for Street Light 3 was artificially covered. The system then treated the sensor/light state as an error while the lamp was still on. This is a sensor-state or expected-state mismatch demonstration, not a field-maintenance label and not a measured three-phase fault.
- Sensing logic: the LDR supplies the ambient-light input; current sensors provide real-time consumption information; the ultrasonic sensor changes brightness based on traffic. The paper does not establish that a cabinet-level current deviation alone uniquely identifies a lamp failure.
- Data and validation: the paper discusses city-corporation data for an energy-cost comparison and reports an estimated energy-cost reduction of approximately 60 percent. The error test is a lab intervention with an artificially covered LDR. There is no independently adjudicated field fault/repair dataset, no maintenance-outcome confusion matrix, and no fault-recall calibration.
- Scientific judgment: reasonable direct support for the proposition that expected ambient-light state and observed lamp/electrical state can form an inspection signal. It does not justify treating a LightGuard daytime cabinet-current event as a confirmed fault. The paper's title-level “error detection” is broader than the demonstrated ground truth.

### S2. DOE/PNNL connected LED streetlight fault-diagnostics study

- Authors: Anay Waghale and Michael Poplawski.
- Title: *On the Way: Automated fault detection and diagnostics for LED street lighting systems*.
- Source: U.S. Department of Energy, Solid-State Lighting / PNNL, published in *LD+A*, June 2023. [Official PDF page](https://www.energy.gov/cmei/ssl/articles/way-automated-fault-detection-and-diagnostics-led-streetlighting-systems).
- Supporting official context: [Connected Streetlighting Systems](https://www.energy.gov/cmei/ssl/connected-streetlighting-systems).
- Source type and grade: government laboratory technical publication, Quality A, direct streetlight/electrical relevance L3.
- Research logic: expose luminaires to controlled, long-duration undervoltage in a connected-lighting test bed, observe service disruptions, define distinct disruption modes, then ask which input voltage, current, and power measurements could detect them.
- Sample/domain: 12 LED streetlights from 12 luminaire manufacturers containing drivers from seven driver manufacturers; ten programmed undervoltage conditions from nominal 120 VAC down to 60 VAC; long-duration condition defined as more than one minute.
- Ground-truth mechanism: the induced electrical condition is controlled undervoltage. Human observation identifies service disruptions. The paper distinguishes “Luminaire: High Current,” “Luminaire: Low Light,” and “Luminaire: Intermittent Output.”
- Field validation and statistics: this is laboratory/bench validation, not a municipal field cohort. Results reported include all 12 units showing high current, 5 of 12 low-light, and 6 of 12 intermittent-output behavior at evaluated conditions. No population fault rate is supplied.
- Key diagnostic lesson: input voltage alone is mainly useful for indicating whether a disruption may have occurred. Distinguishing causes requires additional input current and/or power observations. Example thresholds are engineering recommendations from the test, including 120 percent of rated current for prolonged high-current risk and 95 percent of rated input power for low-light risk.
- Limitations: the study did not identify or reproduce all possible causes of undervoltage; unit behavior varied and some behavior may be intentional by design. Thresholds are not universal for every luminaire or cabinet.
- Scientific judgment: strong direct support for multi-signal expected-state/current mismatch and for persistence. It also directly supports keeping “possible service disruption” separate from confirmed cause. Transfer to LightGuard is at the level of a screening rule, not a fault classifier.

### S3. Lee and Huang, IEEE streetlight illumination mapping

- Authors: Huang-Chen Lee and Huang-Bin Huang.
- Title: *A Low-Cost and Noninvasive System for the Measurement and Detection of Faulty Streetlights*.
- Publication: *IEEE Transactions on Instrumentation and Measurement*, 64(4), 1019-1031, 2015.
- DOI: [10.1109/TIM.2014.2361551](https://doi.org/10.1109/TIM.2014.2361551). [Bibliographic record](https://dblp.org/rec/journals/tim/LeeH15). The accessible author manuscript is linked from [ResearchGate](https://www.researchgate.net/publication/273296013_A_Low-Cost_and_Noninvasive_System_for_the_Measurement_and_Detection_of_Faulty_Streetlights).
- Source type and grade: peer-reviewed IEEE journal paper, Quality A, direct streetlight relevance L3.
- Research logic: mount light meters and GPS on a vehicle (“Hitchhiker”), collect illumination intensity at 10 Hz, create spatial illumination maps, and compare repeated maps before and after a government repair.
- Sample/domain: proof-of-concept route in a 600 m by 400 m area in Chiayi County, Taiwan; four maps before repair and four after repair, with the repair completed by the local government on 7 August 2013.
- Ground-truth mechanism: reduced road illumination and change in a known repaired streetlight, not cabinet current. The study uses repeated spatial observation and repair timing as operational reference.
- Field validation and statistics: real-route measurements and before/after maps are used. The paper is a proof of concept and complementary to electrical inspectors; it does not claim a universal fault rate or provide a general streetlight-population sensitivity estimate.
- Limitations: optical output is not the same as electrical current; weather, vehicle path, obstruction, sensor placement, and map matching can alter readings. It does not establish a current threshold or a three-phase rule.
- Scientific judgment: supports the principle that repeated expected-versus-observed state mismatch is actionable for inspection. It cannot validate a cabinet AMI current event by itself.

### S4. Villar-Rodriguez et al., smart-meter load-curve anomaly detection

- Authors: Esther Villar-Rodriguez, Javier Del Ser, Izaskun Oregi, Miren Nekane Bilbao, and Sergio Gil-Lopez.
- Title: *Detection of non-technical losses in smart meter data based on load curve profiling and time series analysis*.
- Publication: *Energy*, 137, 118-128, 2017.
- DOI: [10.1016/j.energy.2017.07.008](https://doi.org/10.1016/j.energy.2017.07.008). [Institutional record and accepted manuscript](https://scienceportal.tecnalia.com/en/publications/detection-of-non-technical-losses-in-smart-meter-data-based-on-lo/).
- Source type and grade: peer-reviewed journal paper, Quality A, direct AMI/load-profile relevance L2.
- Research logic: represent load traces using statistical descriptors and time-series shape comparison, using elastic distances that tolerate timing shifts and warping. The detector identifies outlying consumption traces rather than assigning a single physical cause.
- Sample/domain: real smart-meter traces from a Spanish utility, with non-technical-loss events emulated on those traces.
- Ground-truth mechanism: the anomalous cases are emulated loss/fraud patterns and may also resemble meter malfunction; they are not a streetlight repair label.
- Field validation and statistics: real utility data are used, but the abnormal cases are emulated. The paper reports comparative detection performance in its experimental setup, not a field-maintenance accuracy for physical assets.
- Limitations: residential/utility consumer load shape is not the same as a municipal streetlight feeder; shape similarity can discard absolute timing that matters for sunrise and control schedules; emulation does not prove a physical fault mechanism.
- Scientific judgment: strong support for meter-relative load-shape anomaly detection and for not equating outlier status with fault. Transfer is reasonable for a meter-local anomaly sign if schedule and asset context remain explicit.

### S5. Capozzoli et al., time-windowed expected-versus-observed building load

- Authors: Alfonso Capozzoli, Marco Savino Piscitelli, Silvio Brandi, Daniele Grassi, and Gianfranco Chicco.
- Title: *Automated load pattern learning and anomaly detection for enhancing energy management in smart buildings*.
- Publication: *Energy*, 157, 336-352, 2018.
- DOI: [10.1016/j.energy.2018.05.127](https://doi.org/10.1016/j.energy.2018.05.127).
- Source type and grade: peer-reviewed journal paper, Quality A, direct operational-load relevance L2.
- Research logic: apply an enhanced Symbolic Aggregate approXimation transformation, optimize unequal time-window widths and symbol intervals for the building's behavior, and detect infrequent or unexpected patterns at specific times of day. A post-mining step uses additional heating/cooling data for preliminary diagnosis.
- Sample/domain: whole-building electrical load from two case studies with different size, end use, sampling frequency, explanatory variables, and heating/cooling configurations.
- Ground-truth mechanism: unexpected operational energy patterns; the added HVAC datasets are explanatory context, not independent repair labels.
- Field validation and statistics: the method is tested on two real case studies and described as flexible/robust within them. The paper does not supply a streetlight fault-outcome validation.
- Limitations: building diversity affects generalization; the post-mining diagnosis is explicitly preliminary; operational anomalies may be caused by occupants, controls, equipment, or measurement issues.
- Scientific judgment: supports using time-of-day and meter-specific historical structure instead of a global threshold. It supports an anomaly/inspection candidate, not a cause label.

### S6. Bouzid, Champenois, and Tnani, negative-sequence compensation

- Authors: M. Ben Khader Bouzid, G. Champenois, and S. Tnani.
- Title: *Reliable stator fault detection based on the induction motor negative sequence current compensation*.
- Publication: *International Journal of Electrical Power & Energy Systems*, 95, 490-498, 2018.
- DOI: [10.1016/j.ijepes.2017.09.008](https://doi.org/10.1016/j.ijepes.2017.09.008).
- Source type and grade: peer-reviewed electrical-engineering journal paper, Quality A, direct electrical mechanism relevance L2.
- Research logic: measure total negative-sequence current, separately characterize inherent machine asymmetry, sensor inaccuracy, and voltage-unbalance contributions, and subtract those disturbances so the residual is more specific to the tested stator fault.
- Sample/domain: experimental 1.1 kW induction motor; healthy and faulty tests; inter-turn short-circuit and phase-to-phase faults under unbalanced supply.
- Ground-truth mechanism: deliberately introduced motor faults with laboratory control of voltage-unbalance conditions.
- Field validation and statistics: laboratory experimental validation across multiple fault and disturbance conditions; no municipal feeder or streetlight population validation.
- Limitations: negative-sequence current is a superposition of fault, supply unbalance, inherent asymmetry, and sensor error. A raw phase imbalance cannot be interpreted as one cause. A streetlight cabinet aggregate may not expose the phasor information required by the method.
- Scientific judgment: strong cautionary support for treating phase-selective behavior as an anomaly sign and for requiring disturbance controls. It does not support calling a LightGuard phase-selective event a negative-sequence fault unless synchronized phase quantities and an appropriate circuit model are available.

### S7. Micolta Mosquera, Oslinger, and Franco, negative-sequence electrical indicators

- Authors: Javier Ernesto Micolta Mosquera, José Luis Oslinger, and Edinson Franco.
- Title: *Contributions to the online fault diagnosis of interturn short circuit in three-phase induction motor by means of negative sequence components*.
- Publication: *DYNA*, 83(198), 2016.
- DOI: [10.15446/dyna.v83n198.50378](https://doi.org/10.15446/dyna.v83n198.50378).
- Source type and grade: peer-reviewed journal paper with open full text, Quality A, direct electrical mechanism relevance L2.
- Research logic: compute symmetrical components using the Fortescue transform from phase voltage/current phasors; use negative-sequence current and impedance as indicators; examine voltage-unbalance and load-level effects with finite-element simulations and laboratory experiments.
- Sample/domain: squirrel-cage induction motor, FEM simulation plus laboratory tests. The abstract does not justify a LightGuard-scale field sample claim.
- Ground-truth mechanism: inter-turn short circuit in a controlled motor study, with voltage unbalance and load as confounders.
- Field validation and statistics: simulation and lab validation, no streetlight feeder or maintenance-outcome data.
- Limitations: motor physics and phasor access differ from a cabinet-level AMI meter. A current magnitude per phase without phase angle, time synchronization, and voltage is not equivalent to a negative-sequence diagnostic.
- Scientific judgment: supports the electrical plausibility of phase asymmetry as a diagnostic feature, while reinforcing a strict non-equivalence between “phase-selective load pattern” and “negative-sequence fault.”

### S8. IEEE 1159-2019 power-quality monitoring practice

- Title: *IEEE Recommended Practice for Monitoring Electric Power Quality*.
- Publisher and year: IEEE Power and Energy Society, active standard, 2019.
- Source: [IEEE Standards Association record](https://standards.ieee.org/ieee/1159/6124/).
- Source type and grade: standard/recommended practice, Quality A, electrical measurement relevance L2.
- Research logic: define nominal conditions and deviations in single-phase and polyphase AC systems, describe monitoring devices and application techniques, and require interpretation in relation to source, load, and their interaction.
- Ground-truth mechanism: the standard is not a fault experiment; it provides measurement and interpretation vocabulary for power-quality deviations.
- Field validation and statistics: no experiment or accuracy statistic is claimed by the standards page. Its value is measurement-process consistency, not event-level truth.
- Limitations: it does not label a municipal streetlight anomaly, select a LightGuard threshold, or prove maintenance cause.
- Scientific judgment: appropriate authority for reporting a phase deviation as a measured electrical-quality observation, not as a fault diagnosis. It reinforces the need to retain measurement location, instrument capability, and interpretation context.

### S9. Zhang et al., historical load baseline construction

- Authors: Yi Zhang, Weiwei Chen, Rui Xu, and Jason Black.
- Title: *A Cluster-Based Method for Calculating Baselines for Residential Loads*.
- Publication: *IEEE Transactions on Smart Grid*, 7(5), 2368-2377, 2016.
- DOI: [10.1109/TSG.2015.2463755](https://doi.org/10.1109/TSG.2015.2463755). [Institutional record](https://scholarship.libraries.rutgers.edu/esploro/outputs/journalArticle/A-Cluster-Based-Method-for-Calculating-Baselines/991031758135804646).
- Source type and grade: peer-reviewed IEEE journal paper, Quality A, direct meter-baseline relevance L2.
- Research logic: construct normal nonevent-day cohorts from load-profile correlations, estimate a counterfactual baseline from similar nonparticipating members, and compare actual event-day metered load with that baseline.
- Sample/domain: actual utility meter data in a residential demand-response setting; the abstract reports comparison with traditional baseline methods.
- Ground-truth mechanism: demand-response event/non-event status, not a physical fault. The normal baseline is a statistical comparator.
- Field validation and statistics: actual utility data and comparison to traditional methods; the abstract reports significantly more accurate baselines but does not transfer its metric to LightGuard.
- Limitations: cohort-based baselines are not automatically meter-specific; demand-response conditions differ from streetlight schedules; weather and event selection can alter the comparator.
- Scientific judgment: supports the principle that expected load must be built from historical or comparable normal behavior and that a baseline is a counterfactual estimate, not a label.

### S10. NIST Engineering Statistics Handbook, CUSUM

- Title: *CUSUM Control Charts*.
- Publisher: National Institute of Standards and Technology, Engineering Statistics Handbook.
- Source: [NIST section 6.3.2.3](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm).
- Source type and grade: government statistical methodology, Quality A, general time-series/measurement relevance L1.
- Research logic: accumulate standardized deviations from an in-control mean; choose design parameters for a shift size and false-alarm/miss tradeoff. NIST notes improved sensitivity over Shewhart charts for small mean shifts, especially shifts of about two standard deviations or less.
- Ground-truth mechanism: a statistical process mean shift, not a streetlight failure.
- Field validation and statistics: the method is presented through control-chart theory and design equations for alpha, beta, and shift size; no LightGuard field statistic is implied.
- Limitations: the in-control mean and variance must be credible; serial dependence, schedule transitions, missingness, drift, and multiple testing alter operating characteristics.
- Scientific judgment: supports persistence-aware accumulation as a method family. LightGuard should report a meter-relative cumulative deviation or persistence evidence, with thresholds frozen before outcome review, rather than claim a CUSUM alarm is a fault.

### S11. Dutta et al., current-signature streetlight ML study, retained as a limitation source

- Authors: Pallav Dutta, Masuma Parvin, Rumpa Saha, and Suddhasatwa Chakraborty.
- Title: *Electrical Current Signature-Based Machine Learning Models for Streetlight Fault Prediction in Smart City Infrastructure*.
- Publication: *Informatica*, 50(2), 2026.
- DOI: [10.31449/inf.v50i2.8972](https://doi.org/10.31449/inf.v50i2.8972).
- Source type and grade: peer-reviewed journal article, Quality A, direct streetlight/current relevance L3 but limited transfer strength.
- Method: eight supervised classifiers on a public Kaggle dataset, augmented with simulated current-signature features; SMOTE was applied to the training set and 5-fold cross-validation was used.
- Limitation that matters here: the authors explicitly state that field-collected, non-simulated sensor validation remains future work. It is therefore not used as a core basis for a LightGuard fault claim. It is useful evidence that model performance can be optimistic when current signatures are simulated and labels are not operational outcomes.

## Methodological Validation

### Daytime full activation or expected-state/current mismatch

The method is scientifically reasonable as a screening construct when three things are explicit:

1. Expected state is defined from a trusted schedule or measured ambient-light context.
2. Electrical observation is measured at a known point and compared with an appropriate rated or historical reference.
3. Persistence and possible causes are retained rather than collapsed into a binary fault label.

The ECCE paper directly demonstrates a light-sensor state mismatch, while the DOE/PNNL work demonstrates why input current and power add information beyond voltage or state alone. For LightGuard, the strongest defensible output is `daytime full activation anomaly sign` or `inspection candidate`.

It cannot prove that all lamps on the cabinet are illuminated, that the photocell/astronomical controller failed, that an unobserved load is absent, or that a repair is required. Weather, scheduled override, construction lighting, meter placement, aggregation, and sensor error remain alternatives.

### Persistent partial-load deviation

The method is reasonable because a repeated departure from a meter's own expected profile is more informative for triage than an isolated spike, and NIST's CUSUM framework formalizes sensitivity to small sustained mean shifts. DOE/PNNL's duration-based testing also shows why duration is part of the mechanism, not merely a UI decoration.

The scientifically safe implementation is a predeclared meter-relative deviation plus a minimum persistence rule, with transition periods and missing data handled explicitly. A single sample should be labeled transient or unavailable unless other evidence supports escalation.

It cannot prove a partial lamp outage, a stable controller failure, or a physical degradation. A sustained change may reflect a legitimate schedule, load composition change, voltage condition, meter drift, communication duplication, or a change in the asset population.

### Phase-selective activation and negative sequence

The method is scientifically reasonable only at the level of a phase-asymmetry observation. The electrical literature supports negative-sequence components as useful diagnostic variables in controlled polyphase-machine studies, but also shows that unbalance is a superposition of supply, inherent equipment, sensor, and fault effects. IEEE 1159 supports standardized monitoring and interpretation of polyphase deviations.

LightGuard must not call its present phase-selective cabinet pattern “negative-sequence current” unless it has synchronized phase phasors or an equivalent validated calculation. If only per-phase RMS current is available, the allowed term is `phase-selective anomaly sign` or `phase-current asymmetry observation`.

It cannot prove a short circuit, insulation failure, open conductor, phase wiring error, or individual lamp fault. Voltage measurements, phase sequence, CT accuracy, aggregation topology, and asset-phase mapping are required before a causal electrical diagnosis.

### Meter-relative historical baseline

The method is scientifically reasonable and better aligned with the LightGuard problem than a single global current threshold. Villar-Rodriguez et al. support load-shape outlier detection on real utility data; Capozzoli et al. support time-window-specific expected behavior; Zhang et al. show that baseline construction is a counterfactual estimation problem rather than a label. NIST supplies the persistence/statistical-process complement.

The baseline must be meter-local by default, use only observations available before the evaluation period, preserve seasonal and schedule strata, expose warm-up/unavailable states, and retain coverage and uncertainty. A pooled regional baseline may be a comparator, never a substitute for meter history without a documented reason.

It cannot prove a fault because an anomalous residual can be caused by a legitimate operational change or measurement process failure. Baseline quality is a prerequisite for an anomaly sign, not a guarantee of physical causation.

## Source Quality and Transfer Grades

| Source | Quality | Directness | Method verdict | LightGuard use |
|---|---|---:|---|---|
| IEEE ECCE 2023 | A | L3 | Reasonable state-mismatch prototype; lab-injected error | Supports anomaly wording only |
| DOE/PNNL connected streetlighting | A | L3 | Strong controlled electrical/service-disruption study | Supports multi-signal and persistence gates |
| Lee and Huang 2015 | A | L3 | Real-route before/after illumination mapping | Supports repeated expected/observed inspection signal |
| Villar-Rodriguez et al. 2017 | A | L2 | Real utility traces plus emulated anomalies | Supports shape/profile anomaly, not fault |
| Capozzoli et al. 2018 | A | L2 | Two real building cases, time-window pattern detection | Supports time-of-day baselines and cautious diagnosis |
| Bouzid et al. 2018 | A | L2 | Controlled motor experiments with disturbance compensation | Supports confounding warning for phase asymmetry |
| Micolta Mosquera et al. 2016 | A | L2 | FEM plus lab negative-sequence analysis | Supports electrical plausibility, not cabinet transfer |
| IEEE 1159-2019 | A | L2 | Measurement/interpretation standard | Supports terminology and measurement provenance |
| Zhang et al. 2016 | A | L2 | Actual utility baseline comparison | Supports counterfactual baseline framing |
| NIST CUSUM | A | L1 | Statistical persistence method | Supports sustained-deviation logic |
| Dutta et al. 2026 | A | L3 | Simulated current features, no field sensor validation | Limitation/control source, not a core claim anchor |

## Risks

- The most direct streetlight source has a laboratory sensor intervention, not independent field maintenance labels.
- DOE/PNNL controlled thresholds are device- and test-condition-specific; copying them into Suyeong would be unjustified.
- AMI load-profile studies often use emulated non-technical losses or operational anomalies, not physical lighting repairs.
- Negative-sequence papers concern motors with phasor-capable measurements. Per-phase cabinet RMS values are not automatically negative-sequence components.
- Meter-relative baselines can leak future information, absorb the anomaly into the normal profile, or mistake a legitimate schedule change for an anomaly if history eligibility is not frozen.
- A measured anomaly can originate in the asset, controller, feeder, meter, communication chain, or data transformation.
- “Fault,” “error,” “anomaly,” and “service disruption” are not interchangeable labels across the reviewed studies.
- Literature quality and directness are evidence grades, not probabilities and not validation metrics for H1 or the v0.11 proxy.

## Adopted Rules

1. Preserve `anomaly sign`, `inspection candidate`, and `service-disruption signal` as the default LightGuard vocabulary.
2. Do not convert a literature anomaly indicator into Gold, Silver, fault probability, fault rate, field accuracy, recall, FPR, or specificity.
3. Treat daytime activation as a mismatch between expected state/context and measured electrical behavior, not as a confirmed controller or lamp fault.
4. Require persistence and transition handling for partial-load deviation; isolate one-sample spikes as transient or unavailable evidence.
5. Call the present phase pattern `phase-selective anomaly sign` unless synchronized phase quantities and a validated sequence calculation exist.
6. Keep voltage, current, power, ambient light, schedule, phase mapping, meter placement, and data quality as separate evidence fields.
7. Build historical baselines meter-locally and causally from pre-evaluation observations; never silently impute missing history.
8. Treat human inspection, maintenance records, controller logs, and field measurements as the route to Gold/Silver labels. The literature cannot supply those labels.
9. Report the alternative explanations that remain after each detector fires.
10. Keep literature grade independent from H1, proxy, canonical-six, and blinded-review results.
11. Use the literature to justify triage and measurement design, not to select thresholds after seeing LightGuard outcomes.
12. For any future causal claim, require a prospective field protocol with asset-meter mapping, expected-state/controller logs, voltage/current/power measurement provenance, maintenance outcome, and time-bounded adjudication.

## Bottom Line

The methods are scientifically reasonable for LightGuard only as layered anomaly-sign and inspection-prioritization evidence. The strongest direct support is for expected-state plus electrical mismatch, persistence-aware current/power monitoring, and meter-relative historical comparison. Phase-selective behavior is a plausible electrical anomaly sign but needs substantially richer measurement before negative-sequence or fault language is permitted. None of the reviewed methods removes the v0.11 Gold/Silver gap.
