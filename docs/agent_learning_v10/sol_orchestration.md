# Agent Learning Note

## Role

LightGuard v0.10 goal orchestrator and implementation owner. The role protects
the frozen v0.9 evidence, the ignored source AMI, the pre-outcome transport
protocol, causal replay, claim boundaries, verification, and release workflow.

## Actual Model

`gpt-5.6-sol`

## Sources Reviewed

- https://openai.com/index/harness-engineering/
  - Institution / Authors: OpenAI, Ryan Lopopolo
  - Why relevant: repository knowledge, executable feedback loops, and agent-legible invariants for long-running implementation.
- https://openai.com/index/introducing-the-codex-app/
  - Institution / Authors: OpenAI
  - Why relevant: coordinated long-running agents, isolated responsibilities, and explicit supervision.
- https://openai.com/codex/
  - Institution / Authors: OpenAI
  - Why relevant: current Codex product and software-engineering workflow boundary.
- https://github.com/openai/codex/blob/main/docs/agents_md.md
  - Institution / Authors: OpenAI Codex
  - Why relevant: repository-local instruction discovery and precedence.
- https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/multi_agents_spec.rs
  - Institution / Authors: OpenAI Codex
  - Why relevant: narrow delegation, completion handling, and agent lifecycle semantics.
- https://airc.nist.gov/airmf-resources/airmf/
  - Institution / Authors: NIST
  - Why relevant: measured evidence, limitations, governance, and risk communication.
- https://www.nist.gov/publications/nistsematech-engineering-statistics-handbook-chapter-2-measurement-process
  - Institution / Authors: NIST/SEMATECH
  - Why relevant: measurement-process characterization and time-dependent variability.

## Rules adopted

- Apply `harness_docs` before project changes and keep a backlog record.
- Freeze v0.9 H1 before any actual-background outcome is inspected.
- Treat ignored raw AMI as immutable private input; commit fingerprints only.
- Select backgrounds with source coverage and quality rules, never H1 outcome.
- Never call unmodified anonymized AMI normal truth or attach municipal, KMA,
  KASI, or rated-load facts to it.
- Delegate only bounded methodology and review outputs; close completed agents.
- Require deterministic scripts, manifests, tests, and independent QA rather
  than accepting agent self-report.

## Risks

- Full-period data may exist but contain meter-specific gaps or sparse phases.
- Current-only grafts can become physically misleading if energy is rewritten.
- Paired recovery can be confounded when the original pair is already inspect.
- Future leakage can enter through full-period baselines or transition estimates.
- Repeated windows can create pseudoreplication and overstate uncertainty.
- A transport PASS still does not establish field fault accuracy.

## Execution Contract

1. Pass the full April-June B-feeder raw-AMI gate or stop with
   `BLOCKED_NO_FULL_AMI`.
2. Freeze source, v0.9, background eligibility, injection assignment, H1, and
   transport gates before scoring.
3. Use one primary injected variant per meter-day and meter-day clustered
   uncertainty.
4. Replay chronologically with `history.timestamp < decision_time`; insufficient
   history is `not_evaluable_warmup`.
5. Develop R1 only after a frozen H1 transport-gate failure.
6. Allow completion only after independent QA and the full v0.10 preflight.

