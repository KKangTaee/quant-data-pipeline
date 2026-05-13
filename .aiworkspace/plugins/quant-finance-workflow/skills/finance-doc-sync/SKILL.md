---
name: finance-doc-sync
description: Final-sync finance project documentation after implementation, task workflow, roadmap, QA, backtest report, registry, or user analysis changes in quant-data-pipeline. Use this as a documentation alignment and closeout skill, not as the primary implementation or task-management skill; pair it with finance-task-management plus the relevant domain skill when those domains are being changed.
---

# Finance Doc Sync

Use this skill when work in the active `quant-data-pipeline` repo/worktree changes or clarifies the finance project and durable docs should stay aligned.

This is a closeout documentation skill. It is not the primary implementation skill for Backtest UI, task lifecycle, phase lifecycle, DB ingestion, factor, or core strategy work.

## Primary Skill First

| Work type | Primary skill |
|---|---|
| Backtest Streamlit UI / runtime JSONL helpers | `finance-backtest-web-workflow` |
| Task / phase workflow, checklist, roadmap status | `finance-task-management` |
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

1. Identify the change type and the owning primary skill.
2. Read only the relevant docs and code paths.
3. Update the smallest durable doc set needed to avoid stale guidance.
4. Keep current behavior separate from future plans.
5. Record durable decisions in `QUESTION_AND_ANALYSIS_LOG.md`.
6. Record non-trivial milestones in `WORK_PROGRESS.md`.
7. If task or phase status changed, sync the relevant active task / phase docs and roadmap.
8. If a backtest result became durable, sync the report index and strategy log/hub when applicable.
9. Run repo-local hygiene helpers when relevant.
10. Commit a coherent completed unit unless the user asked not to.

## Boundary

Do not force code inspection for document-only work. Do inspect code when implementation behavior, table meaning, runtime flow, or strategy assumptions changed.
