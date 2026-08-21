# Agent Learning Note

## Role

LightGuard v0.8 goal orchestration, frozen-artifact protection, experiment
separation, integration, validation, and final completion audit.

## Model actually used

`gpt-5.6-sol` orchestration policy. Wave workers are explicitly restricted to
`gpt-5.6-terra` and `gpt-5.6-luna` as specified by the goal.

## Sources

- URL: https://openai.com/index/harness-engineering/
  - Institution/author: OpenAI
  - Checked: 2026-08-20
  - Key point: repository-visible plans, tests, and feedback loops should make
    long-running agent work legible and verifiable.
  - LightGuard use: checkpoint artifacts and executable preflights are treated
    as evidence, not progress prose.
- URL: https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/multi_agents_spec.rs
  - Institution/author: OpenAI Codex
  - Checked: 2026-08-20
  - Key point: agent spawning, waiting, messaging, and closing have explicit
    lifecycle contracts and bounded concurrency.
  - LightGuard use: Wave 1 is split into three narrow, non-overlapping outputs.
- URL: https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/multi_agents.rs
  - Institution/author: OpenAI Codex
  - Checked: 2026-08-20
  - Key point: child results require explicit collection and lifecycle cleanup.
  - LightGuard use: results are reviewed and completed workers are closed before
    implementation begins.
- URL: https://learn.chatgpt.com/docs/agent-configuration/agents-md
  - Institution/author: OpenAI
  - Checked: 2026-08-20
  - Key point: repository guidance is discovered hierarchically and closer
    instructions override broader ones.
  - LightGuard use: `harness_docs` and repository `AGENTS.md` remain mandatory.

## Risks

- Parallel edits to shared experiment files can contaminate frozen boundaries.
- A green calibration result can be mistaken for independent evidence.
- Generated regional scenarios can be overstated as field generalization.
- Holdout review can cause accidental post-hoc tuning.

## Adopted rules

- Keep Wave 1 write scopes disjoint.
- Treat v0.7 SHA `383c91e2c22d9364232c80683b6f8e4b6dc09d35`
  as regression-only and prohibit its 96 cases from tuning.
- Freeze design, calibration, candidate parameters, and confirmatory holdout in
  that order with SHA-256 evidence.
- Do not modify Flutter until confirmatory metrics are final.
- Keep actual external regional AMI status `unavailable` unless official evidence
  proves otherwise.
