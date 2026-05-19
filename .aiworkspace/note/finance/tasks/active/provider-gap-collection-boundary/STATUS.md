# Provider Gap Collection Boundary Status

Status: Complete
Created: 2026-05-20

## Progress

- Task opened as the next UI-engine boundary follow-up.
- Current provider gap coupling identified in `app/web/backtest_practical_validation.py`.
- Moved provider gap row / collection plan / job orchestration into `app/services/backtest_practical_validation.py`.
- Updated `app/web/backtest_practical_validation.py` to render service rows / plans and call service collection on button click.
- Added service contract tests for provider gap planning and mocked job orchestration.
- Updated durable docs for service/UI responsibility.

## Result

- UI still owns Streamlit display and `st.session_state`.
- Service now owns source map lookup, collectable gap classification, collector order, and run history metadata.
- Focused tests and compile checks pass.
