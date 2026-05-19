# Compare Service Boundary Design

Status: In progress
Created: 2026-05-19

## Current Boundary After Slice 1

```text
app/web/backtest_compare.py
  -> app/services/backtest_compare_execution.py
  -> app/web/backtest_compare.py::_run_compare_strategy
  -> app/web/runtime/backtest.py
  -> finance/*
```

This is an intermediate boundary.
The service owns the manual compare execution loop and error normalization, while the strategy runner catalog still lives in `app/web/backtest_compare.py`.

## Responsibility Split

| Layer | Responsibility |
| --- | --- |
| `app/web/backtest_compare.py` | form render, validation before submit, spinner, session state, history append, result render, weighted UI |
| `app/services/backtest_compare_execution.py` | manual multi-strategy execution loop, elapsed timing, error normalization |
| `app/web/backtest_compare.py::_run_compare_strategy` | temporary strategy runner catalog and per-strategy runtime dispatch |
| `app/web/runtime/backtest.py` | DB-backed runtime wrappers |

## Why Not Move Everything Now?

`backtest_compare.py` has several distinct responsibilities mixed together.
Moving the full runner catalog and weighted builder in one patch would also require moving strict universe presets and data-only result helpers that currently live in Streamlit-adjacent modules.

The safer migration is:

1. Move multi-strategy execution loop and error normalization.
2. Move strategy runner catalog and compare defaults.
3. Move weighted portfolio builder after data-only helper dependencies are separated.
4. Move saved portfolio replay execution.

## Contract

`execute_strategy_compare(...)` returns `StrategyCompareExecutionResult`.

Fields:

- `ok`
- `bundles`
- `error_kind`
- `error_message`
- `elapsed_seconds`

Error text remains compatible with the previous UI:

- `Comparison input issue: ...`
- `Comparison data issue: ...`
- `Comparison execution failed: ...`
