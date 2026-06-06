# Design

## Current Structure

`render_final_selected_portfolio_dashboard_page()` loads dashboard rows and saved monitoring portfolios, then delegates to `_render_dashboard_portfolio_workspace()`.

Current workspace order:

1. summary badge strip
2. `_render_my_portfolio_manager()`
3. `_render_strategy_selection_manager()`
4. `_render_portfolio_monitoring_overview()`
5. `_render_selected_strategy_detail()`
6. `_render_portfolio_strategy_comparison()`

The portfolio-wide monitoring scenario already exists in `_render_portfolio_monitoring_overview()`, but it is section 3 after the setup UI.

## Implementation Direction

- Keep persistence and runtime helpers unchanged.
- Split the scenario update button out of `_render_portfolio_monitoring_overview()` so the top hero can be read-only.
- Add an active monitoring hero wrapper that handles no portfolio, no strategy, not run, and run states.
- Render the hero immediately after the workspace badge strip.
- Render portfolio shelf next, then strategy configuration with the update button below it.
- Rename lower strategy detail as detailed check so readiness/provider/open issue evidence remains below setup.

## Contract Check

Scenario results are kept in Streamlit session state by portfolio / slot / selected decision / input signature.
Saved portfolio setup remains `.aiworkspace/note/finance/saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl`.
Moving render order does not change Final Review decision rows, saved setup schema, or runtime replay inputs.
