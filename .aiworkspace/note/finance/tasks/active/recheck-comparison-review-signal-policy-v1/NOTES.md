# Recheck Comparison Review Signal Policy V1 Notes

Status: Active
Created: 2026-05-29

## Notes

- Existing web `_build_review_trigger_board()` duplicates CAGR / MDD / benchmark spread thresholds that already exist in `build_selected_portfolio_recheck_comparison()`.
- 12-4 should move the Review Signals board to a runtime read model so contract tests can cover policy mapping without Streamlit.
