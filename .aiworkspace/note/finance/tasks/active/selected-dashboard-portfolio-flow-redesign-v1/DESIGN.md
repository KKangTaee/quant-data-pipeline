# Design

## Current Structure

- `render_final_selected_portfolio_dashboard_page()` currently renders status cards and `Final Review Handoff` before user portfolios.
- `_render_my_portfolio_manager()` uses a form and selectbox, not a horizontal card shelf.
- Portfolio saved state stores only `selected_decision_ids`, so strategy start / end / balance / memo is session-only in the scenario area.
- `_render_performance_recheck()` renders recheck preflight, readiness, symbol freshness, and provider evidence before scenario inputs.
- Monitoring result is strategy-local; portfolio-level total invested / current value / P&L / CAGR / MDD summary is not the first visible result.

## Target Direction

- Keep the same source-of-truth boundary:
  - Final Review selected rows are read-only.
  - Dashboard portfolios are saved setup only.
  - Scenario results stay in session state.
- Add backward-compatible `strategy_slots` beside `selected_decision_ids`.
- Enrich selected strategy rows with slot config for rendering.
- Move evidence blocks behind lower detail expanders after the scenario result.
- Derive rebalance info from selected component `selection_history` and replay settings where available.

## Files

- `app/runtime/final_selected_portfolios.py`: saved-state normalization, slot CRUD, strategy-state join.
- `app/web/final_selected_portfolio_dashboard_helpers.py`: portfolio/strategy tables and monitoring summary display helpers.
- `app/web/final_selected_portfolio_dashboard.py`: render order, portfolio shelf, strategy builder, scenario-first view.
- `tests/test_service_contracts.py`: saved-state and slot-state contract coverage.
- docs flow files and root handoff logs after implementation.
