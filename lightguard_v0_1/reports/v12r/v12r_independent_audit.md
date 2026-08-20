# LightGuard v0.12R Independent Blind Review and Methodology QA

## Role

Subagent D, LUNA: independent audit of literature learning, the frozen v0.11
boundary, v12R joins, the blinded human-review packet, Flutter wording, and the
current artifact contract. This audit did not generate human labels, run
Flutter, run the v12R preflight, run Git, or change v0.11/H1/Proxy/raw files.

## Actual Model

LUNA role executed by the GPT-5 Codex runtime. No distinct LUNA model identifier
was exposed by the session.

## Scope and evidence inspected

- All four existing `docs/agent_learning_v12r/` notes, including the TERRA methodology and circularity notes and the LUNA domain note.
- Frozen protocol, 21-source registry, 21-row literature matrix, 765-row case join, v0.11 freeze manifest, review manifest, review protocol, blindness audit, HTML packet, CSV template, empty human-result files, reproducibility manifest, and final summary.
- v12R build/import/analyze/preflight scripts by static inspection.
- Flutter literature card and v12R grounding, validation, and Gold/Silver acquisition documents.
- The only executed repository command: `python3 scripts/test_v12r_artifacts.py`.

## Starting-reference and literature-method audit

The supplied starting reference is traceable to the IEEE record for *IoT-based
Efficient Streetlight Controlling, Monitoring and Real-time Error Detection
System for Smart Cities in Bangladesh*, by A.T.M. Mustafa Masud Chowdhury,
Jeenat Sultana, and Md Sakib Ullah Sourav, ECCE 2023, DOI
[10.1109/ECCE57851.2023.10101600](https://doi.org/10.1109/ECCE57851.2023.10101600).
The current domain review correctly records IEEE document 10101600 and limits
the demonstrated LDR-cover intervention to a laboratory state/sensor mismatch.
It does not promote the result to field failure, AMI-only validation, or a fault
probability.

The local registry contains 21 unique sources: 19 quality A and 2 quality B.
The matrix contains one row per source and records support grade, data type,
field-label availability, transfer limits, allowed claims, and prohibited
claims. The matrix retains an L0 limitation record rather than hiding a source
that cannot transfer positive field evidence.

The external methodology sources independently support the review controls:

| Source | Method finding | LightGuard applicability |
|---|---|---|
| Mamede et al., BMJ Quality & Safety 2024, [DOI](https://doi.org/10.1136/bmjqs-2023-016621) | Randomized diagnostic experiment shows salient early information can anchor later judgment. | Hide H1, Proxy, Literature, rank, and canonical metadata before rating. |
| Cohen, Psychological Bulletin 1968, [DOI](https://doi.org/10.1037/h0026256) | Weighted kappa accounts for scaled disagreement on an ordinal scale. | Use only after two or more real reviewers rate common cases. |
| STARD 2015, BMJ 351:h5527, [DOI](https://doi.org/10.1136/bmj.h5527) | Diagnostic reporting should state reference standard, reader masking, timing, missingness, and uncertainty. | Keep Gold/Silver absence, packet status, indeterminate handling, and claim limits explicit. |
| FDA reader-study guidance, [PDF](https://www.fda.gov/media/71237/download) | Readers should not know truth standard, diagnosis, outcome, or treatment identity where feasible; supplied information should be standardized prospectively. | The packet presents anonymized traces, a uniform window, missingness, and past-only local baseline. |
| NIST measurement-process characterization, [chapter](https://www.itl.nist.gov/div898/handbook/mpc/mpc.htm) | Repeatability, reproducibility, calibration, stability, and uncertainty are distinct from interpretation. | Missing phase channels and measurement provenance are not converted into asset faults. |
| FDA reader studies, [method page](https://www.fda.gov/science-research/fda-stem-outreach-education-and-engagement/evaluating-medical-devices-using-reader-studies) | Reader studies evaluate controlled interpretive decisions, not a replacement for a physical truth standard. | Human anomaly-sign review cannot upgrade a case to confirmed fault. |

These sources make the review protocol methodologically reasonable as a bias
controlled, ordinal anomaly-sign assessment. They do not make the AMI sample a
diagnostic-accuracy cohort.

## Gate table

| Gate | Evidence inspected | Result |
|---|---|---|
| v0.11 freeze | `v11_freeze_manifest.json`, release SHA, frozen file hashes | PASS |
| Search protocol frozen before screening | Freeze manifest path, SHA, and `frozen_before_screening: true` | PASS |
| Starting reference metadata and DOI | IEEE record/DOI cross-check in domain review and registry | PASS |
| Source quality | 21 unique registry entries, 19 A, 2 B, HTTPS URLs | PASS |
| Pattern directness and transfer limits | P1-P4 matrix with L0-L3, allowed/prohibited claims | PASS |
| Anomaly versus fault language | Reports and Flutter docs use anomaly sign, inspection candidate, and field confirmation unavailable | PASS |
| Probability boundary | No fault probability, field accuracy, recall, FPR, or specificity claim | PASS |
| Literature/H1/Proxy independence | Pattern literature grade does not use detector outputs; shared AMI origin remains disclosed | PASS with WARN |
| Case join integrity | 765 proxy-high rows; literature grade is pattern-based; field confirmation unavailable | PASS |
| RMS-only phase terminology | P3 is phase-current asymmetry observation; negative-sequence claims prohibited | PASS |
| Review protocol | Pre-registered strata, shortfall rule, labels, confidence, reasons, agreement plan | PASS |
| Packet pre-freeze and blindness | 62 unique cases, fixed namespaces, packet SHA, hidden fields absent from HTML | PASS |
| Human labels | Results and consensus files contain headers only; status is `HUMAN_REVIEW_PENDING` | PASS, pending by design |
| AI substitution prevention | Import path accepts real reviewer CSVs; no agent-generated labels | PASS |
| Gold/Silver absence | Freeze, final report, app docs, and acquisition plan all retain Gold 0/Silver 0 | PASS |
| Flutter wording/docs | Card shows Level 3 and Pending; docs state evidence grade is not fault probability | PASS |
| Protected files | Artifact test confirms `.env`, `official_docs/`, and `harness_docs/` are not tracked | PASS |
| Current artifact contract | `python3 scripts/test_v12r_artifacts.py` output: `status: PASS`, sources 21, matrix rows 21, proxy high 765, review cases 62, human labels 0 | PASS |
| Human agreement, enrichment, T3, Level 4 | No real labels; kappa and human enrichment correctly not calculated | WARN, unavailable |
| Flutter analyze/test/web/Android and full preflight | Not run under this Subagent D instruction; no success claim made | WARN, not executed |

## Independence and transfer findings

Literature evidence is independent of H1 and Proxy scores at the grade-making
stage: the matrix assigns grade by pattern and source support, and the artifact
test checks that a pattern has one literature grade. The resulting `final_evidence_grade`
is intentionally a convergence label that also considers H1/proxy agreement; it
must not be called an independent literature grade. H1 and Proxy still share the
same AMI origin, so their concordance is algorithmic convergence, not independent
field corroboration.

The four pattern interpretations are reasonable only as anomaly signs:

- Expected-state/current mismatch is a context-plus-electrical inspection signal, not a lamp or controller fault.
- Persistent meter-relative departure is a screening signal only with a past-only, meter-local, coverage-aware reference.
- Phase-selective behavior is an asymmetry observation. RMS-only inputs do not support negative-sequence terminology.
- Historical baseline residuals are counterfactual references, never Gold/Silver labels.

The packet is deliberately enriched and therefore cannot estimate population
prevalence. A later reviewer may rate `STRONG_ANOMALY_SIGN`,
`POSSIBLE_ANOMALY_SIGN`, `LOW_CONCERN`, or `INSUFFICIENT_DATA`; those labels will
describe human anomaly-sign perception only. At least two real reviewers are
required before weighted Cohen kappa, enrichment, permutation/bootstrap results,
consensus, T3, or Level 4 are emitted.

## Final judgement

**PASS for independent methodology and artifact QA, with WARN status for two
explicitly unresolved gates.**

The unresolved items are not defects in the no-reviewer state:

1. Real human labels have not been collected, so human concordance, kappa, and
   Level 4 are unavailable by protocol.
2. Flutter and the complete v12R preflight were not executed by this role, so
   this audit does not assert those build gates.

No evidence was found that the current artifacts fabricate human labels, expose
literature/detector metadata in the blind packet, convert RMS-only phase data to
negative sequence, or replace Gold/Silver with external literature.

The maximum defensible current claim remains Level 3: literature-supported,
algorithm-convergent anomaly-sign evidence with field confirmation unavailable.
