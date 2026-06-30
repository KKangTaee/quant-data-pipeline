# Backtest Boundary Refactor V1 Status

Status: Active

## Current

- 2026-07-01: User approved staged `1차 -> QA -> commit -> ... -> 7차` refactor flow.

## Stage Log

- 1차: Completed. Added `app/web/backtest_state.py` and `app/web/backtest_formatters.py`; `backtest_page.py` now uses the state boundary instead of importing workflow state helpers directly from `backtest_common.py`.
- 2차: Completed. Added `app/services/backtest_single_payload.py`; Single Strategy runner now normalizes execution payload through the service boundary before display/execution.
- 3차: Completed. Added `app/services/backtest_portfolio_mix_readiness.py`; Portfolio Mix role flag detection now lives in the service layer with a web compatibility wrapper.
- 4차: Completed. Added `app/services/backtest_validation_status_policy.py`; Practical Validation module planner now imports shared status normalization/ranking policy.
- 5차: Pending
- 6차: Pending
- 7차: Pending
