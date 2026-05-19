# Backtest Execution Service Boundary Design

Status: Complete
Created: 2026-05-19

## Boundary

```text
app/web/backtest_single_runner.py
  -> app/services/backtest_execution.py
  -> app/web/runtime/backtest.py
  -> finance/loaders/* / finance/sample.py / finance engine
```

## Responsibility Split

| Layer | Responsibility |
| --- | --- |
| `app/web/backtest_single_runner.py` | payload display, Streamlit spinner, session state write, run history append, success message |
| `app/services/backtest_execution.py` | strategy dispatch, elapsed timing, error normalization, result bundle metadata update |
| `app/web/runtime/backtest.py` | DB-backed runtime wrappers and data/runtime errors |
| `finance/*` | strategy, engine, transform, performance behavior |

## Contract

`execute_single_backtest(payload, strategy_name=...)` returns `BacktestExecutionResult`.

Fields:

- `ok`
- `bundle`
- `error_kind`
- `error_message`
- `elapsed_seconds`

Error kinds remain:

- `input`
- `data`
- `system`

The UI-facing error text remains compatible with the previous runner:

- `Backtest input issue: ...`
- `Backtest data issue: ...`
- `Backtest execution failed: ...`

## Preservation Rules

- Keep `st.session_state.backtest_last_bundle`.
- Keep `st.session_state.backtest_last_error`.
- Keep `st.session_state.backtest_last_error_kind`.
- Keep `append_backtest_run_history(..., run_kind="single_strategy")` in the UI layer for this slice.
- Keep `meta["ui_elapsed_seconds"]` behavior.
