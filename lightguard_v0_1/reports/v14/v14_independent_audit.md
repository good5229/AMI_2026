# LightGuard v0.14 Independent LUNA Audit

## Audit conclusion

**PASS**

The execution artefacts are internally reproducible, preserve the required claim boundary, report the observed independent-unit outcomes conservatively, and contain complete frozen HTTPS source provenance for every raw-manifest entry. No release-blocking finding or non-blocking warning remains.

## Independent checks

| Check | Result | Evidence |
|---|---|---|
| v0.13 MAD negative/non-evaluable freeze | PASS | Frozen target SHA-256 is `4194fcf900a5b1bd83e1b37076df4780c3d2c990d7227ec5a1570a2fa143726f`; status remains `FROZEN_NEGATIVE_NON_EVALUABLE`, primary gate `NOT_EVALUABLE_INCOMPLETE_COVERAGE`, MAD SC3 BA `0.52004485`, z-score BA `0.66598258`, grade `NO_EV_GRADE_NOT_EVALUABLE`. |
| London no-score block | PASS | One result row, status `PRIMARY_BLOCKED_PROVENANCE`; no performance release. |
| 3PhaseInsight reference-only | PASS | Registry and final summary retain report/specification-only status with no labelled raw benchmark claim. |
| CoDEx independent units | PASS | 40 unique result units; every unit is `measurement_run`. |
| CoDEx partial-prefix boundary | PASS | 40/40 raw entries are `partial_run=true`, each exactly 16,777,216 bytes, all local sizes and SHA-256 hashes match. No complete-run claim was found. |
| CoDEx outcome recount | PASS | 30 injection-positive partial prefixes, 0 escalated; 10 controls, 0 escalated. The defensible reporting state is `NOT_REPLICATED`. |
| SustData positive-control boundary | PASS | 18 unique `day_appliance_cluster` units; all are `TRANSITION_POSITIVE_CONTROL_ONLY` and explicitly not electrical faults. |
| SustData outcome recount | PASS | 2/18 positive-control clusters escalated. The defensible reporting state is `INCONCLUSIVE`. |
| Minimum two actual tracks | PASS | CoDEx-VFD and SustDataED2 were both actually evaluated. |
| No row-level pseudoreplication | PASS | Result units are runs or day/appliance clusters; configs prohibit row-level inference and naive row bootstrap. |
| No streetlight field-accuracy/fault-probability expansion | PASS | The explicit external-mechanism-only claim boundary is retained across results, manifests, matrix, and summary. |
| Raw data excluded from Git | PASS | `scripts/test_v14_artifacts.py` found no tracked path under `official_docs/external_benchmarks_v14`; independent index inspection also found none, and `.gitignore` contains `official_docs/`. |
| Raw manifest integrity | PASS | All 59 raw entries have non-empty valid HTTPS source URLs: CoDEx 40/40 and SustData 19/19. The strengthened test fails closed if the count differs from 59 or any source is absent/non-HTTPS. |
| Reproducibility manifest | PASS | All 11 listed aggregate artefact hashes match. |
| Artifact contract test | PASS | `python3 scripts/test_v14_artifacts.py` exits 0 and now prohibits `LIMITED_MECHANISM_SIGN`, enforces both PMC-3 statuses, validates all reproducibility hashes, and requires the final-summary `0/30` and `2/18` interpretations. |
| `PMC-3` unavailable | PASS | CoDEx-VFD is `NOT_AVAILABLE` and SustDataED2 is `N/A`; neither is reported as evaluated. |
| Outcome-calibrated mechanism conclusion | PASS | CoDEx PMC-1 is `SURROGATE_ONLY`; PMC-2/4/5 are `NOT_REPLICATED` from the frozen composite `0/30`. SustData PMC-1/2/4/5 are `INCONCLUSIVE` from `2/18`, without component-specific identification. |
| Final summary conservative state | PASS | Summary explicitly reports CoDEx `0 of 30` as not replicated, SustData `2 of 18` as inconclusive, no separate PMC-2/4/5 score, and PMC-3 unavailable. |

## Release-blocking findings

None.

## Non-blocking warnings

None.

## Required disposition

No QA release blocker or unresolved warning remains. Preserve the frozen raw-source URLs, partial-prefix boundary, independent-unit definitions, conservative outcome states, and external-only claim boundary in subsequent changes.

## Verification scope

- Independent rerun: `python3 scripts/test_v14_artifacts.py` -> PASS.
- Reproducibility manifest: 11/11 aggregate hashes matched.
- Raw source provenance: 59/59 valid HTTPS URLs, all unique; CoDEx 40/40 and SustData 19/19.
- Raw payloads and the frozen model, thresholds, and results remained unchanged. `v14_raw_external_manifest.json` changed intentionally to add source-URL provenance for all 59 entries, and the final reproducibility manifest binds that updated manifest hash.
- Flutter and Git were not executed, as required. The user-reported full-preflight PASS was not independently rerun in this audit.

## Scope boundary

These findings concern external physical-mechanism replication only. They do not estimate streetlight field accuracy, municipal performance, fault recall/FPR, asset condition, or actual fault probability.
