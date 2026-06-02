# Design

## UX Direction

- Keep the dashboard as an operational work surface, not a marketing page.
- Use a horizontal shelf for portfolios, but enforce stable card dimensions and line clamping.
- Treat deletion as portfolio management, not a primary shelf action.
- Turn strategy setup from a dataframe/form stack into a compact board: selected row summary first, editable slot fields second.
- Make `모니터 시나리오` explicitly portfolio-level. Strategy tabs remain detail drill-down.

## Implementation Notes

- Prefer HTML/CSS helpers inside `app/web/final_selected_portfolio_dashboard.py` for visual shell only.
- Preserve existing Streamlit forms and runtime functions for persistence.
- Hide raw ids from the default visual flow; keep raw details in expanders only.
- Do not alter `SELECTED_DASHBOARD_PORTFOLIOS.jsonl` directly.
