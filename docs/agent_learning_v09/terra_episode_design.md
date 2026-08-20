# TERRA v0.9 episode-separated experimental design learning note

Access date: 2026-08-20 (KST)

## Applied decisions

- A date, KMA ASOS station observation group, and KASI solar response are an indivisible validation unit. Splitting hourly observations across calibration and confirmation would leak the weather episode.
- The `20260901` split is frozen before v0.9 outcome inspection. The original v0.7 anchor is retained, and other dates are selected by SHA-256 order for runtime-independent reproduction.
- Every station-date has exactly 24 official KMA hours and no station-date is reused. Missing KASI context is blocked, never filled with an internal solar formula.
- v0.8 remains frozen regression and failure-analysis evidence. This subtask does not load v0.8 results, detector settings, candidate settings, or labels.

## Sources consulted

- OpenAI, [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/). Accessed 2026-08-20. Applied repository system-of-record and mechanically checked invariants.
- OpenAI, [Introducing the Codex app](https://openai.com/index/introducing-the-codex-app/). Accessed 2026-08-20. Applied narrow delegated scope and explicit coordination boundaries.
- OpenAI, [Codex](https://openai.com/codex/). Accessed 2026-08-20. Applied human-specified task boundaries and auditable artifacts.
- GitHub Docs, [Customize GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot). Accessed 2026-08-20. Applied project-specific instructions and task-scoped tooling.
- GitHub Docs, [Custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration). Accessed 2026-08-20. Applied role-specific, least-privilege tool and secret boundaries.
- Korea Meteorological Administration, [Meteorological observation data quality and statistics management guidance](https://data.kma.go.kr/resources/images/publication/%EA%B8%B0%EC%83%81%EA%B4%80%EC%B8%A1%EB%8D%B0%EC%9D%B4%ED%84%B0%20%ED%92%88%EC%A7%88%20%ED%86%B5%EA%B3%84%20%EA%B4%80%EB%A6%AC%20%EC%A7%80%EC%B9%A8%282025.9%29.pdf). Accessed 2026-08-20. Used ASOS station provenance and hourly completeness expectations.
- Korea Astronomy and Space Science Institute, [Area sunrise/sunset information API](https://www.data.go.kr/data/15012688/openapi.do). Accessed 2026-08-20. Used official date-and-area sunrise, sunset, and civil-twilight fields.
- scikit-learn, [Cross-validation: evaluating estimator performance](https://scikit-learn.org/stable/modules/cross_validation.html). Accessed 2026-08-20. Used held-out separation as the evaluation principle.
- NIST/SEMATECH, [Response surface designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri336.htm). Accessed 2026-08-20. Used pre-specified factor coverage rather than outcome-driven date selection.

## Residual risk and handoff

Only 12 anchor-date KASI values are currently present in frozen v0.7. The remaining 36 dates are intentionally blocked. A later owner must run the documented official KASI acquisition with a process-environment key, review serialized failures, rebuild the manifest, and proceed only when the gate is open with 48 ready episodes.
