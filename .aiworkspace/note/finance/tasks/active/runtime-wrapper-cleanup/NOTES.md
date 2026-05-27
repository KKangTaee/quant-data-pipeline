# Runtime Wrapper Cleanup Notes

Status: Active
Created: 2026-05-27

## 2026-05-27 Findings

- `app/runtime/backtest.py` has no Streamlit import and currently passes boundary lint.
- The file mixes public runtime wrappers, result bundle construction, preflight helpers, strict strategy preflight, and Real-Money policy/hardening logic.
- Public callers import directly from `app.runtime.backtest`, so compatibility must be preserved even if helpers move.
- First low-risk split should avoid strategy result calculation and DB loader behavior.

## Decisions

- Keep public `run_*_backtest_from_db` wrappers in `app/runtime/backtest.py` for Task 8.
- Split helper files only when the public import path remains compatible.
- Prefer characterization tests for pure contracts over DB-backed smoke runs in this task.

## 8-02 Public Surface

Direct external callers use `app.runtime.backtest` for:

- `BacktestInputError`, `BacktestDataError`
- Real-Money and strict policy constants
- `build_backtest_result_bundle`
- `inspect_strict_annual_price_freshness`
- public `run_*_backtest_from_db` wrappers

Result bundle split must keep `app.runtime.backtest.build_backtest_result_bundle` and `app.runtime.build_backtest_result_bundle` available.

## 8-04 Result

Moved only the pure result bundle construction helper to `app/runtime/backtest_result_bundle.py`.
The public wrappers, constants, error classes, freshness helper, and DB-backed strategy execution paths remain in `app/runtime/backtest.py`.
