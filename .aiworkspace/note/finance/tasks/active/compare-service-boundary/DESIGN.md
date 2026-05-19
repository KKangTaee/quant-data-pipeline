# Compare Service Boundary Design

Status: In progress
Created: 2026-05-19

## Current Boundary After Slice 2

```text
app/web/backtest_compare.py
  -> app/services/backtest_compare_execution.py
  -> app/services/backtest_compare_catalog.py
  -> app/web/runtime/backtest.py
  -> finance/*
```

This is an intermediate boundary.
The services own the manual compare execution loop, error normalization, strategy runner catalog, compare defaults, universe resolution, and runtime dispatch.
The UI still owns preset source dictionaries because `app/web/backtest_common.py` is Streamlit-adjacent, so it passes them to the service as a `ComparePresetCatalog`.

## Responsibility Split

| Layer | Responsibility |
| --- | --- |
| `app/web/backtest_compare.py` | form render, validation before submit, spinner, session state, history append, result render, weighted UI, `ComparePresetCatalog` assembly |
| `app/services/backtest_compare_execution.py` | manual multi-strategy execution loop, elapsed timing, error normalization |
| `app/services/backtest_compare_catalog.py` | strategy runner catalog, compare defaults, preset/manual universe resolution, runtime dispatch |
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

`run_compare_strategy(...)` receives `ComparePresetCatalog` instead of importing `app/web/backtest_common.py`.
That keeps the service Streamlit-free while preserving the existing preset dictionaries until a later preset module split.
