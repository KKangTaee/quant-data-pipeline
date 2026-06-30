# Backtest Boundary Refactor V1 Notes

- `app/web/backtest_common.py` is the highest-risk shared boundary because it imports Streamlit, runtime wrappers, finance loaders, and UI helpers together.
- `app/services/backtest_practical_validation_modules.py` already owns much of the Practical Validation module gate semantics.
- `app/services/backtest_selected_route_preflight.py` is the current selected-route preflight entrypoint for Final Review handoff.
