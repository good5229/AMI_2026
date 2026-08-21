# TERRA v0.9 Hard-Negative Forensics Learning Note

Access date: 2026-08-20 (KST).

## Working rules applied

1. Treat the repository harness and narrow task contract as executable
   constraints: preserve the frozen v0.8 boundary, record the work before
   editing, and make source integrity visible in the audit itself.
2. Keep a row-level identifier trail. Aggregate FPR alone cannot reveal whether
   solar, weather, missing-feature, or persistence mechanisms overlap.
3. Separate evidence gathering from candidate design. This audit classifies
   frozen false positives but performs no threshold or parameter search.
4. Preserve unavailable load and phase values as missing values. Do not replace
   them with zeros or regional averages.

## Sources consulted

- [OpenAI, Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/): repository-local guidance, mechanical invariants, and feedback loops make agent work reviewable and repeatable.
- [OpenAI, Introducing the Codex app](https://openai.com/index/introducing-the-codex-app/): scoped parallel work needs isolated responsibilities and visible review boundaries.
- [OpenAI, Codex CLI - Getting Started](https://help.openai.com/en/articles/11096431): local agent execution has approval boundaries; task scope should not imply access to unrelated runtime configuration.
- [GitHub Docs, Support for different types of custom instructions](https://docs.github.com/en/copilot/reference/custom-instructions-support): `AGENTS.md` is a supported mechanism for shared agent instructions.
- [GitHub Docs, About custom agents](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-custom-agents): focused specialist roles and tool scopes reduce unintended cross-task changes.
- [Korea Meteorological Administration, ASOS hourly-data Open API](https://data.kma.go.kr/api/selectApiDetail.do?openApiNo=241&pgmNo=42): ASOS observations are official experiment context; their availability must be represented instead of fabricated.
- [scikit-learn, Classification metrics](https://scikit-learn.org/stable/modules/model_evaluation.html): false positives are normal observations predicted positive, and FPR must be interpreted with the negative-class denominator.

## Method consequences for v0.9

The output inventory is deterministic from the frozen v0.8 calibration and
confirmatory JSON plus candidate-freeze JSON. Each row keeps original labels and
case identifiers, a frozen decision score, and both one additive primary family
and overlapping evidence flags. This supports later episode-separated design
without leaking confirmatory rows into tuning.

## Claim boundary

The audit reports controlled scenario behavior only. It does not establish
Suyeong, Gangneung, Chungju, or other municipal field-AMI false-positive rates;
it also does not change the status of v0.8 weather context as non-promoted.
