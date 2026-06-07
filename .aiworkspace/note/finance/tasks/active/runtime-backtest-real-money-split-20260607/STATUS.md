# Runtime Backtest Real-Money Split Status

Status: Completed
Date: 2026-06-07

## Current State

- `app/runtime/backtest_real_money.py` now owns the real-money / readiness helper family.
- `app/runtime/backtest.py` still re-exports constants and helpers for existing caller compatibility.
- `app/runtime/backtest.py` line count moved from 5169 after 8A to 3294.
- The new real-money runtime module is 1939 lines.

## Verification

- RED contract tests failed before implementation with missing module / missing facade delegation.
- GREEN contract tests passed after implementation.
- Focused `BacktestRuntimeContractTests` and `BoundaryContractHardeningTests` passed.
- Final verification passed: `py_compile`, full `tests.test_service_contracts` (`281` tests), UI / engine boundary checker, `git diff --check`, Streamlit health, task count check, and public import smoke.

## Remaining Follow-Up

- 8C: split strict quality / value family runtime wrappers from `app/runtime/backtest.py`.
- Later: consider whether final selected portfolio runtime should receive a similar helper extraction pass.
