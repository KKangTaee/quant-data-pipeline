# Backtest Execution Service Boundary Notes

Status: Complete
Created: 2026-05-19

## Implementation Notes

- The service imports runtime functions directly from `app.web.runtime.backtest` and default constants from `finance.sample` / runtime constants.
- The service does not import `app.web.backtest_common` because that module imports Streamlit and owns a large UI/session-state helper surface.
- `strategy_name` remains part of the service call signature so future contract objects can keep user-facing strategy context, but the service does not add a new bundle meta field for it.
- `app/web/backtest_single_runner.py` remains the place where run history is appended, preserving the first-slice rule that persistence side effects stay in the UI layer.

## Files Changed

| File | Change |
| --- | --- |
| `app/services/__init__.py` | service package source boundary |
| `app/services/backtest_execution.py` | new Streamlit-free Single Strategy execution service |
| `app/web/backtest_single_runner.py` | reduced to UI state/history wrapper around the service |
