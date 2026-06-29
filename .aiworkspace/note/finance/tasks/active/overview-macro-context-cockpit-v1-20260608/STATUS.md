# Overview Macro Context Cockpit V1 Status

Status: Completed
Created: 2026-06-08

## Current Status

- 2026-06-08: Started 1차 implementation task in `codex/sub-dev`.
- 2026-06-08: Classified as focused multi-step implementation task, not new phase work.
- 2026-06-08: Read required docs and research bundle; confirmed Cockpit V1 is the approved first build candidate.
- 2026-06-08: Implemented Overview Macro Context Cockpit V1 above the existing Overview tabs.
- 2026-06-08: Browser QA confirmed cockpit renders before deep tabs with source / freshness / stale / data review states visible.

## Scope State

- Completed in scope: Overview summary-first cockpit using existing DB-backed read models.
- Stayed out of scope: provider/schema/storage changes, Candidate Ops IA changes, Data Health action queue, full heatmap / macro week view.

## Result

- Added `build_overview_macro_context_cockpit()` in `app/services/overview_market_intelligence.py`.
- Added cached `load_overview_macro_context_cockpit()` in `app/web/overview_dashboard_helpers.py`.
- Added compact cockpit rendering in `app/web/overview_ui_components.py`.
- Rendered the cockpit at the top of `app/web/overview_dashboard.py` before existing deep tabs.
- Added service/UI contract tests for cockpit summary, tab ordering, refresh-state normalization, and dark-theme text readability.

## Next

- 2차 candidate: Data Health -> Ingestion Handoff / Action Queue.
- 3차 candidate: breadth / heatmap and macro week view.

## 2026-06-09 Follow-Up: Futures Monitor Chart Scope

- User reported that `Workspace > Overview > Futures Monitor` still showed only 6 charts when Watch Group / Symbols were effectively set to all.
- Confirmed root cause: `_futures_chart_symbols()` capped chart render symbols at 6 without a visible scope control.
- Added a `Charts` control with `Compact 6` default and `All with data` option, plus explicit "showing N of M" / "data-backed charts" copy.
- Scope stayed UI-only: no provider, DB schema, registry, saved JSONL, validation gate, monitoring signal, or trading action changes.
