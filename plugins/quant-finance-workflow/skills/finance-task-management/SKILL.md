---
name: finance-task-management
description: Classify and manage quant-data-pipeline finance work as an active task or optional phase. Use this when the user asks to plan, start, continue, checkpoint, close, or reorganize finance work; when task docs under .note/finance/tasks/active need PLAN/DESIGN/STATUS/NOTES/RUNS/RISKS updates; when root handoff logs need concise milestone updates; or when deciding which finance implementation skill should own the code work.
---

# Finance Task Management

Use this skill for finance workflow control in the active `quant-data-pipeline` repo/worktree.

This is a task-orchestration skill, not a domain implementation skill. Pair it with a narrower implementation skill when code changes are needed, then use `finance-doc-sync` near closeout when durable docs must be aligned.

## First Reads

Read only what is needed:
- `AGENTS.md`
- `.note/finance/docs/INDEX.md`
- `.note/finance/docs/ROADMAP.md`
- `.note/finance/docs/PROJECT_MAP.md`
- the active task under `.note/finance/tasks/active/` when continuing existing work
- `.note/finance/docs/runbooks/README.md` when operating procedure is unclear

For detailed task document rules, read `references/task-document-contract.md`.

## Classify The Request

| Request shape | Default handling |
|---|---|
| Tiny one-off answer or command | answer directly; no task docs unless durable state changes |
| Focused multi-step task | use or create `.note/finance/tasks/active/<task-id>/` |
| Major roadmap/product work | use an active task first; open a phase only when the user explicitly wants phase management |
| Code implementation | pair with the matching domain implementation skill |
| Documentation alignment after implementation | pair with `finance-doc-sync` |
| Backtest report migration or durable result note | keep under `.note/finance/reports/backtests/` and update its index |

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
4. Update task status as work moves from planned to in progress to completed.
5. For code work, switch to the appropriate domain skill and follow its verification rules.
6. Record important command outcomes in `RUNS.md`.
7. Keep `.note/finance/WORK_PROGRESS.md` and `.note/finance/QUESTION_AND_ANALYSIS_LOG.md` concise.
8. Before closeout, use `finance-doc-sync` when overview, roadmap, README, data architecture, flow docs, or indexes changed.
9. Commit a coherent unit unless the user explicitly asks not to.

## Safety

- Do not stage or commit local run history, generated artifacts, temp CSVs, or registry JSONL unless the user explicitly asks.
- Do not use this skill as a reason to edit domain code without the matching implementation skill.
- Do not expand a task into adjacent UX, data, or strategy redesign unless the user confirmed that scope.
- Preserve user work in a dirty tree; do not revert files you did not change.
