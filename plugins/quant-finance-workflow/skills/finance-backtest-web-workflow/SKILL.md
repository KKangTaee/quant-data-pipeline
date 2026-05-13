---
name: finance-backtest-web-workflow
description: Build, debug, or refactor the quant-data-pipeline Streamlit Backtest web workflow. Use this when work touches app/web/backtest_*.py, app/web/pages/backtest.py, Backtest UI panels, Candidate Review, Portfolio Proposal, History, Candidate Library, saved portfolio replay, runtime registry helpers, JSONL UI persistence, or user-facing validation / readiness flows. Pair with finance-task-management for task setup/status and finance-doc-sync for closeout documentation.
---

# Finance Backtest Web Workflow

Use this skill for Backtest web app work in the active `quant-data-pipeline` repo/worktree.

This is a Backtest UI implementation skill. Use `finance-task-management` for active task setup and workflow ownership, then use `finance-doc-sync` near closeout when durable docs need alignment.

## Boundaries

Use this skill for:
- `app/web/pages/backtest.py`
- `app/web/backtest_*.py`
- `app/web/runtime/*.py` when used by the Backtest UI
- Candidate Review, Portfolio Proposal, History, Candidate Library, Final Review, Selected Portfolio Dashboard
- Streamlit state, forms, rerun feedback, saved replay, validation packs, route panels

Do not use this as the primary skill for DB ingestion, factor generation, core strategy implementation, or task-only planning.

## First Reads

Before editing Backtest UI code, read:
- `AGENTS.md`
- `.note/finance/docs/PROJECT_MAP.md`
- `.note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- `.note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- `.note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md` when stage ownership or user workflow changes

For current module ownership and registry safety rules, read `references/backtest-ui-boundaries.md`.

## Core Workflow

1. Identify the user-facing panel and owning module.
2. Confirm the data source: registries, run history, saved setup, or DB-backed provider data.
3. Preserve route boundaries; do not turn review screens into live approval or order behavior.
4. Implement in the owning module rather than expanding `app/web/pages/backtest.py`.
5. Keep Streamlit rerun feedback visible via session state when needed.
6. Keep forms and immediate controls intentionally separated.
7. Run focused Python compile/helper checks; use Browser/Playwright only when layout or interaction risk is meaningful.

## Closeout

Use `finance-doc-sync` when the change affects Backtest UI flow, script responsibility maps, README surface, roadmap/index, or durable logs.
