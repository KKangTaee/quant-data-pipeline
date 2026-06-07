# Runtime Backtest Risk-On Momentum Split Status

Status: Completed
Date: 2026-06-07

## Current State

- `app/runtime/backtest_risk_on_momentum.py` now owns the Risk-On Momentum 5D runtime slice.
- `app/runtime/backtest.py` still re-exports the public runner for existing UI / service callers.
- `app/runtime/backtest.py` line count moved from 5719 to 5169.
- The new Risk-On Momentum runtime module is 571 lines.

## Verification

- RED contract tests failed before implementation with missing module / missing facade delegation.
- GREEN contract tests passed after implementation.
- Final verification passed: `py_compile`, full `tests.test_service_contracts` (`279` tests), UI / engine boundary checker, `git diff --check`, Streamlit health, and public import smoke.

## Remaining Follow-Up

- 8B: split real-money / guardrail / deployment readiness contract helpers from `app/runtime/backtest.py`.
- 8C: split strict quality/value family runtime helpers from `app/runtime/backtest.py`.
