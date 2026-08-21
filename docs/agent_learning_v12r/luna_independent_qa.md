# Agent Learning Note

## Role

Subagent D, LUNA: blind-review integrity and independent methodology QA for
LightGuard v0.12R. The task was to audit the evidence layers and the review
packet, not to generate labels, retune a detector, or make a field-fault claim.

## Actual Model

LUNA role executed by the GPT-5 Codex runtime. The session did not expose a
separate model identifier for a distinct LUNA model.

## Search Queries

The web-learning pass was completed before the repository audit. Queries used:

- `blinded assessment reviewer masking diagnostic accuracy randomized study anchoring bias`
- `anchoring bias diagnostic reasoning experimental study`
- `Cohen 1968 weighted kappa original paper ordinal interrater agreement DOI`
- `NIST interrater agreement kappa weighted Cohen diagnostic review`
- `STARD 2015 blinding reference standard diagnostic accuracy`
- `FDA reader study blinded independent review diagnostic imaging guidance`
- `independent blinded review diagnostic accuracy interobserver agreement ordinal ratings`
- `NIST Cohen kappa inter-rater agreement ordinal weighted`

## Sources Reviewed

The following additional primary, government, or standards sources were used to
learn the review methodology. They are methodological guardrails, not evidence
that a LightGuard event is a fault.

1. **Mamede, S., Zandbergen, A., Carvalho-Filho, M.A., et al. (2024).**
   *Role of knowledge and reasoning processes as predictors of anchoring bias
   in diagnostic reasoning: a randomised controlled experiment.* BMJ Quality
   & Safety, 33(9), 563-572. DOI: [10.1136/bmjqs-2023-016621](https://doi.org/10.1136/bmjqs-2023-016621).
   Peer-reviewed randomized experiment. Salient early information changed
   diagnostic reasoning, and knowledge of discriminating features affected
   susceptibility. Applicability: keep stratum, detector, and literature
   labels out of the reviewer view; a blind trace is a bias-control device, not
   a truth label.

2. **Sanchez Ordonez, M., Rubio Moraga, A., and Bermejo Velasco, P. (2025).**
   *Impact of anchoring bias in medical diagnostic decision-making: an
   experimental study.* Revista Espanola de Salud Publica, PMID 41200955,
   [PubMed record](https://pubmed.ncbi.nlm.nih.gov/41200955/).
   Peer-reviewed experimental vignette study. Initial salient information was
   associated with later diagnostic choices. Applicability: do not expose
   Literature A/B, H1, Proxy, rank, or canonical membership before a human
   anomaly-sign rating.

3. **Cohen, J. (1968).** *Weighted kappa: Nominal scale agreement provision
   for scaled disagreement or partial credit.* Psychological Bulletin, 70(4),
   213-220. DOI: [10.1037/h0026256](https://doi.org/10.1037/h0026256).
   Peer-reviewed foundational method. Weighted kappa preserves the fact that
   adjacent ordinal disagreements are less severe than distant disagreements.
   Applicability: use quadratic-weighted Cohen kappa only after at least two
   real reviewers provide the same cases and ordinal labels.

4. **Bossuyt, P.M., Reitsma, J.B., Bruns, D.E., et al. (2015).** *STARD 2015:
   An updated list of essential items for reporting diagnostic accuracy
   studies.* BMJ, 351:h5527. DOI: [10.1136/bmj.h5527](https://doi.org/10.1136/bmj.h5527);
   checklist: [STARD](https://stard-statement.org/checklist_maintext.htm).
   Peer-reviewed reporting standard. It requires explicit reference standards,
   timing, reader expertise, masking, missing/indeterminate handling, and
   uncertainty reporting. Applicability: v0.12R must report the missing field
   reference standard, the review status, packet composition, and the fact that
   prevalence and fault accuracy are not estimable.

5. **U.S. Food and Drug Administration.** *Guidance for Industry: Developing
   Medical Imaging Drug and Biological Products, Part 3: Clinical Trial Design,
   2004, blinded image evaluation sections.* Government guidance,
   [PDF](https://www.fda.gov/media/71237/download).
   The guidance requires reader blinding to truth-standard, diagnosis, outcome,
   and treatment information where feasible, with prospectively standardized
   information. Applicability: the HTML packet may show only anonymized traces,
   a uniform window, missingness, and past-only baseline context.

6. **U.S. Food and Drug Administration.** *Evaluating Medical Devices Using
   Reader Studies.* Government methodology page,
   [FDA](https://www.fda.gov/science-research/fda-stem-outreach-education-and-engagement/evaluating-medical-devices-using-reader-studies).
   Reader studies evaluate interpretive decisions under controlled presentation;
   they do not turn reader agreement into a physical truth standard. Applicability:
   a pending packet is review-ready, while any later human label remains an
   anomaly-sign judgment rather than a confirmed fault.

7. **NIST/SEMATECH.** *Engineering Statistics Handbook, Measurement Process
   Characterization*, C.M. Croarkin, NIST, 2003, updated 2017,
   [NIST chapter](https://www.itl.nist.gov/div898/handbook/mpc/mpc.htm).
   Government measurement-science guidance. Repeatability, reproducibility,
   stability, calibration, bias, and uncertainty must be separated from the
   interpretation of a measured departure. Applicability: missing channels,
   phase availability, clock alignment, meter identity, and baseline coverage
   remain explicit evidence fields.

8. **NIST.** *Forensic facial examiners vs. super-recognizers: Evaluating
   identity judgment agreement and accuracy*, NIST publication record,
   [NIST PDF](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=932786).
   Government applied-methods study using independent examiners and weighted
   ordinal kappa. Applicability: agreement statistics require independently
   rendered judgments on common cases; they cannot be calculated from an empty
   human-results file or from agent-generated labels.

## Risks

- Blinding reduces anchoring and confirmation risk but cannot create a field reference standard.
- The packet is an enriched review sample, not a prevalence sample; review-positive rates must not be generalized to all AMI origins.
- H1 and Proxy are not literature-independent data sources because they share the same AMI origin. The literature grade is independent of their scores, but multi-layer convergence is not independent evidence in the causal sense.
- The v12R final evidence grade intentionally combines literature grade with H1/proxy concordance. It must not be confused with the pattern-level literature grade.
- RMS phase magnitudes do not provide synchronized phasors or Fortescue components. The correct term is `phase-current asymmetry observation` or `phase-selective anomaly sign`, not `negative-sequence fault`.
- Human labels are absent. No kappa, human enrichment, T3 class, or Level-4 claim is available.
- A passing artifact contract does not substitute for the unrun Flutter and full v12R preflight gates.

## Adopted Rules

- Freeze v0.11 and the literature search protocol before using screened results.
- Verify the starting ECCE metadata and DOI against the IEEE record; treat its LDR-cover experiment as a laboratory state/sensor mismatch, not field fault validation.
- Keep Literature, H1, Proxy, and Human Review as named evidence layers.
- Assign literature grades from pattern/source support only; never derive them from H1, Proxy, canonical membership, or reviewer outcomes.
- Hide stratum, Literature, H1, Proxy, rank, and canonical metadata from reviewers.
- Treat `HUMAN_REVIEW_PENDING` and `PHASE_B_REVIEW_READY` as valid states when no real reviewer file exists.
- Require at least two real reviewers before weighted Cohen kappa, enrichment, permutation, bootstrap, consensus, T3, or Level 4.
- Use Evidence Grade as explanatory support strength, never as fault probability.
- Preserve Gold usable = 0 and Silver Operational usable = 0.
- Keep RMS-only phase language conservative and retain field confirmation as unavailable.
- Use generated manifests, hashes, and the artifact test as stronger evidence than agent self-report.

## Learning-to-audit conclusion

The methodology is reasonable for a blinded anomaly-sign review of a fixed,
enriched packet. It is not reasonable to interpret the packet as a diagnostic
accuracy study or to treat reviewer agreement as a fault label. This distinction
drives the PASS/WARN split in the independent audit.
