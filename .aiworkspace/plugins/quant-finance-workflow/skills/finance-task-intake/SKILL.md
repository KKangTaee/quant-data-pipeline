---
name: finance-task-intake
description: Classify incoming quant-data-pipeline finance requests before work starts. Use this when deciding whether a request is phase work, active task work, code implementation, documentation-only work, integration review, runbook maintenance, or simple Q&A; when choosing which docs to read first; when choosing the active task location; or when routing to the right finance domain skill.
---

# Finance Task Intake

Use this skill at the start of non-trivial finance work in the active `quant-data-pipeline` repo/worktree.

This is an intake and routing skill. It does not own implementation, merge review, runbook writing, or final documentation sync.

## First Reads

Read only what is needed:
- `AGENTS.md`
- `.aiworkspace/note/finance/docs/INDEX.md`
- `.aiworkspace/note/finance/docs/ROADMAP.md`
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- the active task under `.aiworkspace/note/finance/tasks/active/` when continuing existing work
- `.aiworkspace/note/finance/docs/runbooks/README.md` when operating procedure is unclear

For detailed task document rules, read `references/task-document-contract.md`.

## Classify The Request

| Request shape | Default handling |
|---|---|
| Tiny one-off answer or command | answer directly; no task docs unless durable state changes |
| Focused multi-step task | use or create `.aiworkspace/note/finance/tasks/active/<task-id>/` |
| Major roadmap/product work | use an active task first; open a phase only when the user explicitly wants phase management |
| Code implementation | pair with the matching domain implementation skill |
| Documentation alignment after implementation | route to `finance-doc-sync` |
| Merge conflict, worktree integration, sub-result integration, final verification planning | route to `finance-integration-review` |
| Repeated command or operating procedure needs durable instructions | route to `finance-runbook-maintainer` |
| Backtest report migration or durable result note | keep under `.aiworkspace/note/finance/reports/backtests/` and update its index |

## Domain Skill Routing

- Backtest UI, Streamlit panels, Candidate Review, Final Review, runtime JSONL helpers: `finance-backtest-web-workflow`
- Ingestion, collectors, DB schema, UPSERT, loaders: `finance-db-pipeline`
- Factor generation, accounting-to-factor logic, PIT factor assumptions: `finance-factor-pipeline`
- Strategy, transform, engine, performance, samples: `finance-strategy-implementation`
- Documentation final sync and cross-document alignment: `finance-doc-sync`

If more than one domain is involved, state the boundary first and keep edits scoped to owning files.

## Workflow

1. Identify whether this is a new task, continued task, phase work, or simple answer.
2. Read the minimum current-state docs and relevant active task docs.
3. State the working scope in plain language before broad changes.
4. Decide the owning skill or combination of skills.
5. If task docs are needed, create or update only the active task shell and initial status.
6. Hand off implementation to the domain skill, merge/integration to `finance-integration-review`, runbook changes to `finance-runbook-maintainer`, or final docs to `finance-doc-sync`.

## Safety

- Do not stage or commit local run history, generated artifacts, temp CSVs, or registry JSONL unless the user explicitly asks.
- Do not use this skill as a reason to edit domain code without the matching implementation skill.
- Do not expand a task into adjacent UX, data, or strategy redesign unless the user confirmed that scope.
- Preserve user work in a dirty tree; do not revert files you did not change.
