---
name: finance-backtest-web-workflow
description: Build, debug, or refactor the quant-data-pipeline Streamlit Backtest web workflow. Use this when work touches app/web/backtest_*, app/services/backtest_*, app/runtime/backtest/, Backtest UI panels, Candidate Review, Portfolio Proposal, History, Candidate Library, saved portfolio replay, runtime registry helpers, JSONL UI persistence, Practical Validation, Final Review, or Selected Portfolio Dashboard. Pair with finance-task-intake before broad work and finance-doc-sync for closeout documentation.
---

# Finance Backtest Web Workflow

Use this skill for Backtest web app work in the active `quant-data-pipeline` repo/worktree.

This is a Backtest UI implementation skill. Use `finance-task-intake` before broad work, then use `finance-doc-sync` near closeout when durable docs need alignment.

## Boundaries

Use this skill for:
- `app/web/backtest_page.py`, `app/web/backtest_workflow_shell.py`, and `app/web/backtest_*`
- `app/services/backtest_*` for Streamlit-free workflow/read-model services
- `app/runtime/backtest/` for runners, read models, and JSONL stores
- Candidate Review, Portfolio Proposal, History, Candidate Library, Final Review, Selected Portfolio Dashboard
- Streamlit state, forms, rerun feedback, saved replay, validation packs, route panels

Do not use this as the primary skill for DB ingestion, factor generation, core strategy implementation, or task-only planning.

## First Reads

Before editing Backtest UI code, read:
- `AGENTS.md`
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md` when stage ownership or user workflow changes

For current module ownership and registry safety rules, read `references/backtest-ui-boundaries.md`.

## Core Workflow

1. Identify the user-facing panel and owning module.
2. Confirm the data source: registries, run history, saved setup, or DB-backed provider data.
3. Preserve route boundaries; do not turn review screens into live approval or order behavior.
4. Implement in the owning module rather than expanding `app/web/backtest_page.py` or the workflow shell.
5. Keep Streamlit rerun feedback visible via session state when needed.
6. Keep forms and immediate controls intentionally separated.
7. Run focused Python compile/helper checks; use Browser/Playwright only when layout or interaction risk is meaningful.

## Closeout

Use `finance-doc-sync` when the change makes an owning flow, responsibility map, product direction, Roadmap state,
or document discovery fact stale. Ordinary closeout may update task docs only; do not update Roadmap, Index,
or root logs unless their documented role actually changed.
