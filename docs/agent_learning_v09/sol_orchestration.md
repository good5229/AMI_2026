# SOL Orchestration Learning for LightGuard v0.9

Access date: 2026-08-20

## Sources reviewed

- [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/): repository-local context, explicit invariants, executable feedback loops, and continuously enforced boundaries make long-running agent work legible and reproducible.
- [OpenAI Codex for engineering teams](https://openai.com/business/solutions/engineering/): agents can move from issue to tested change while humans retain control over what ships.
- [OpenAI Codex orchestration: Symphony](https://openai.com/index/open-source-codex-orchestration-symphony/): orchestration works best when work items, acceptance criteria, and validation state are explicit rather than held in conversation only.
- [OpenAI Agents SDK agent patterns](https://github.com/openai/openai-agents-python/blob/main/examples/agent_patterns/README.md): deterministic staged flows and bounded specialist agents are preferable when outputs feed a fixed downstream sequence.
- [NIST randomized block designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm): block controlled nuisance factors and randomize remaining variation. Region and season are therefore explicit blocks, while dates are assigned before outcomes are inspected.
- [NIST choosing an experimental design](https://www.itl.nist.gov/div898/handbook/pri/section3/pri3.htm): objectives, factors, levels, and design must be fixed before analysis. v0.9 freezes its episode split and promotion gates before confirmatory scoring.

## Applied orchestration policy

- SOL owns integration, freeze integrity, candidate implementation, confirmatory boundary enforcement, Flutter integration, and final Git operations.
- TERRA owns bounded hard-negative forensics and episode-separated design. LUNA owns explainable gate research and final independent QA.
- v0.8 calibration and confirmatory results are regression and failure-analysis evidence only. They cannot select v0.9 parameters.
- The 48 official episodes are split before candidate outcomes exist. Calibration and confirmatory dates, episode IDs, and KMA observation identities must have empty intersections.
- Candidate search is bounded to H1, H2, and H3. Weather weight remains `0`; weather is context and an analysis stratum, not a score modifier.
- Calibration prioritizes normal and hard-negative FPR gates before recall. Confirmatory data permits no retuning and can legitimately yield `selected_candidate: null`.
- Artifact contracts, deterministic regeneration, independent QA, Flutter analyze/test/build, secret exclusion, and immutable hashes form the release feedback loop.

## Claim discipline

Controlled scenario metrics describe generated validation cases only. The six anonymized competition AMI windows have no field-fault truth labels and are used only to compare replay decisions and evidence paths. No result establishes municipal field accuracy, actual fault recall, or production readiness.
