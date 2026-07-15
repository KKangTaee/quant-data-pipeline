# Institutional Portfolios Selection Loading V1 Notes

## Diagnosis

- Manager click should update the selected stored portfolio, not run SEC collection.
- Manual SEC collection remains the secondary refresh action.
- Watchlist cards are always rendered by `build_institutional_manager_rail`, but `_selected_manager` only searches the DB manager result list.
- When a clicked watchlist CIK is not in the current manager result list, `_selected_manager` resets `institutional_portfolios_selected_cik` to the first DB row.
- Because the rendered component key can remain the first DB row key, the previous custom component event can be returned again and handled again, producing a rerun loop.
- Reverse lookup is a separate bottleneck. Portfolio model queries for watchlist managers measured around 0.01s; `load_institutional_interest_model("AAPL")` measured around 10.1s because the SQL recomputes filing totals from all holdings.
