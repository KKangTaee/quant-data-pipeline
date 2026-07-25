---
name: finance-doc-sync
description: Synchronize durable finance documentation after an implementation, workflow, runbook, roadmap, QA, report, registry, or user-analysis change. Use this only for documentation alignment in the new .aiworkspace/note/finance docs structure; pair it with finance-task-intake and the relevant domain, integration, or runbook skill for the actual work.
---

# Finance Doc Sync

Use this skill when completed work changes how durable finance docs should read.

This is a closeout documentation skill. It does not classify work, implement code, resolve integration, or write detailed runbooks.

## Primary Skill First

| Work type | Primary skill |
|---|---|
| Backtest Streamlit UI / runtime JSONL helpers | `finance-backtest-web-workflow` |
| Request classification / active task intake | `finance-task-intake` |
| Merge, worktree, conflict, or integrated diff review | `finance-integration-review` |
| Repeated command / operating procedure docs | `finance-runbook-maintainer` |
| DB ingestion, schema, UPSERT, collectors, loaders | `finance-db-pipeline` |
| Factor generation, PIT assumptions, accounting fallback | `finance-factor-pipeline` |
| Core strategy, engine, transform, performance | `finance-strategy-implementation` |

For the detailed update matrix, read `references/doc-sync-matrix.md`.

## Canonical Docs

- Product/project maps: `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md`, `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Architecture and flow docs: `.aiworkspace/note/finance/docs/architecture/`, `.aiworkspace/note/finance/docs/flows/`
- Data / DB docs: `.aiworkspace/note/finance/docs/data/`
- Runbooks and agent notes: `.aiworkspace/note/finance/docs/runbooks/`, `.aiworkspace/note/finance/agent/`
- Active work: `.aiworkspace/note/finance/tasks/active/`, `.aiworkspace/note/finance/phases/active/`
- Root handoff logs: `.aiworkspace/note/finance/WORK_PROGRESS.md`, `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Roadmap/index/glossary: `.aiworkspace/note/finance/docs/ROADMAP.md`, `.aiworkspace/note/finance/docs/INDEX.md`, `.aiworkspace/note/finance/docs/GLOSSARY.md`
- Backtest reports: `.aiworkspace/note/finance/reports/backtests/`

## Core Workflow

1. Identify the completed change and classify it by document role.
2. Update only the owning durable docs whose facts actually changed.
3. Keep implemented behavior separate from future plans.
4. Treat “no canonical doc change” as a normal closeout result and record it in the task when useful.
5. Record a root handoff entry only when the next worker needs a high-signal decision or milestone.
6. Update Roadmap only when baseline, workflow state, approved scope, or priority changed.
7. Update Index only when document discovery, canonical path, or read order changed.
8. If a runbook procedure changed, route the procedure detail to `finance-runbook-maintainer`.
9. If integration or conflict risk remains, route the review to `finance-integration-review`.

## Boundary

Do not force code inspection for document-only work. Do inspect code when implementation behavior, table meaning, runtime flow, or strategy assumptions changed. Do not use this skill as a catch-all for task intake or implementation.
