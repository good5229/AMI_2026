# SOL v0.14 Orchestration Learning Record

Date: 2026-08-21

## Role

SOL coordinates the pre-outcome suitability gate, disjoint TERRA/LUNA reviews, bounded external-data execution, independent QA, and commit-only-after-preflight policy.

## Actual Model

GPT-5 Codex runtime acting as SOL orchestrator.

## Sources Reviewed

- OpenAI, Harness engineering: repository-local instructions and deterministic checks should make the desired path easy and unsafe paths fail closed.
- OpenAI Codex documentation: `AGENTS.md` supplies repository-scoped operating guidance.
- OpenAI multi-agent documentation: delegated work is split into narrow, disjoint scopes and integrated by the parent.
- Original London Met, KU Leuven RDR, Scientific Data/OSF/IEEE PES, and Zenodo records enumerated in the v0.14 suitability and provenance reports.

## Dataset Type

Mixed external electrical evidence: proprietary-derived distribution voltage data, controlled laboratory current disturbance runs, real residential transition data, and a three-phase data-specification report.

## License

License is an activation gate, not an administrative note. London remains blocked because its record does not state a reusable dataset license. CoDEx is CC BY 4.0. SustDataED2 is accepted only for its narrow transition-positive-control role after the IEEE PES registry's CC BY 4.0 record was checked. The 3PhaseInsight report does not license or expose the underlying customer data.

## Label Provenance

Controlled injection state, human-corrected appliance transition, undocumented disturbance class, and absent labels are kept as four distinct evidence types. None is renamed as a Suyeong streetlight fault label.

## Physical Provenance

Rows are never independent evidence units. CoDEx uses run/episode units and bounded prefixes; SustDataED2 uses transition clusters grouped by day and appliance. No missing phase, unit, timestamp, or measurement semantics are imputed.

## Risks

- A favorable external score could be overclaimed as municipal field accuracy.
- Partial CoDEx prefixes could be mislabeled as full runs.
- Appliance transitions could be mislabeled as faults.
- Two measured current channels could be mislabeled as complete three-phase asymmetry.
- Outcome-aware dataset or threshold selection could invalidate the experiment.

## Adopted Rules

1. Freeze v0.13 negative/non-evaluable evidence and all v0.14 suitability/config artifacts before performance access.
2. Run only provenance-eligible tracks; blocked and reference-only tracks receive explicit non-performance records.
3. Record every raw source URL, byte scope, hash, and partial/full status outside Git while tracking only aggregate manifests.
4. Treat controlled disturbance replication and transition positive control as mechanism evidence only.
5. Require independent LUNA QA and the complete Flutter preflight before commit or push.

