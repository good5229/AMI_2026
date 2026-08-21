# Agent Learning Note

## Role

LightGuard v0.5 long-running goal coordinator: protect frozen evidence, keep phases moving toward executable artifacts, delegate narrow non-overlapping research, integrate results, and require independent QA before completion.

## Model actually used

Requested coordinator model: `gpt-5.6-sol`. The host exposes this exact model and the required `gpt-5.6-terra` and `gpt-5.6-luna` overrides. The current-thread metadata APIs do not return the root thread's effective model identifier, so this limitation remains explicitly recorded in the progress watchdog.

## Sources reviewed

- URL: https://openai.com/index/introducing-the-codex-app/
  Institution: OpenAI
  Checked: 2026-08-20
  Key point: long-running work can be split across parallel agents and isolated worktrees, with changes reviewed per thread.
  Application: use only narrow Wave 1 scopes and keep each agent on disjoint output paths.
- URL: https://openai.com/index/harness-engineering/
  Institution: OpenAI
  Checked: 2026-08-20
  Key point: `AGENTS.md` should be a repository map while structured docs remain the system of record; feedback loops and mechanical checks matter more than a monolithic instruction file.
  Application: keep `harness_docs` authoritative and use `docs/goal_progress_v05.md` plus reproducible manifests as durable evidence.
- URL: https://openai.com/index/unrolling-the-codex-agent-loop/
  Institution: OpenAI
  Checked: 2026-08-20
  Key point: agent work is an iterative context/tool loop whose quality depends on explicit environment evidence and bounded tool use.
  Application: each phase must end in code, data, tests, a report, or a reproducibility log.
- URL: https://openai.com/index/introducing-codex/
  Institution: OpenAI
  Checked: 2026-08-20
  Key point: Codex tasks operate in isolated repository environments and should iteratively test their work.
  Application: preserve reviewable phase commits and do not accept unverified analysis as completion evidence.
- URL: https://github.com/openai/codex/blob/main/docs/agents_md.md
  Institution: OpenAI Codex repository
  Checked: 2026-08-20
  Key point: scoped instruction discovery controls which repository rules apply.
  Application: apply root AGENTS and `harness_docs` before v0.5 changes.
- URL: https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/multi_agents_spec.rs
  Institution: OpenAI Codex repository
  Checked: 2026-08-20
  Key point: model overrides must be explicit when a child must not inherit the parent model; completed agents continue consuming slots until closed.
  Application: explicitly select Terra/Luna and close every completed Wave 1 agent.
- URL: https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/multi_agents.rs
  Institution: OpenAI Codex repository
  Checked: 2026-08-20
  Key point: collaboration handlers carry agent state and runtime context across spawn, wait, send, and close operations.
  Application: wait sparingly and continue local critical-path work while agents run.
- URL: https://github.com/openai/codex/blob/main/codex-rs/core/templates/collab/experimental_prompt.md
  Institution: OpenAI Codex repository
  Checked: 2026-08-20
  Key point: agents should be used for well-defined parallel work, told that other agents exist, prohibited from recursive delegation when appropriate, and closed after completion.
  Application: Wave 1 prompts prohibit nested delegation and assign non-overlapping files.
- URL: https://github.com/openai/codex/blob/main/codex-rs/config/src/config_toml.rs
  Institution: OpenAI Codex repository
  Checked: 2026-08-20
  Key point: concurrent-thread, nesting, default model, and reasoning settings are explicit runtime concerns.
  Application: keep concurrency to three Wave 1 agents and verify requested model metadata in their notes.

## Risks / Anti-patterns

- Repeating plans without a concrete artifact.
- Letting child agents edit overlapping files or spawn descendants.
- Treating generated summaries or green tests as proof without checking their coverage.
- Mutating v0.3/v0.4 frozen sets during v0.5 sensitivity work.
- Calling known detector candidates truth labels or field accuracy.
- Converting public contract totals into per-dispatch cost without a matching denominator.

## Concrete execution rules adopted

- Keep the main critical path local and delegate only independent sidecars.
- Update the watchdog at every checkpoint with commands and artifact evidence.
- Preserve old peak consistency and document any metric adjudication as an explicit versioned change.
- Require timestamp `< t` for every causal baseline observation.
- Keep public/API research separate from deterministic local all-run scripts.
- Close completed agents immediately after collecting their outputs.
- Stop and request the exact public-data URL from the user if an essential source cannot be obtained from the supplied URLs or existing official sources.
