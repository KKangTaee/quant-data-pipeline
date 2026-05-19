# Compare Service Boundary Design

Status: Implementation complete
Created: 2026-05-19

## Current Boundary After Slice 4

```text
app/web/backtest_compare.py
  -> app/services/backtest_compare_execution.py
  -> app/services/backtest_compare_catalog.py
  -> app/web/runtime/backtest.py
  -> finance/*

app/web/backtest_compare.py
  -> app/services/backtest_weighted_portfolio.py
  -> app/services/backtest_result_read_model.py
  -> app/web/runtime/backtest.py
  -> finance/performance.py

app/web/backtest_compare.py
  -> app/services/backtest_saved_portfolio_replay.py
  -> app/services/backtest_compare_catalog.py
  -> app/services/backtest_weighted_portfolio.py
  -> app/services/backtest_result_read_model.py
```

The services own the manual compare execution loop, error normalization, strategy runner catalog, compare defaults, universe resolution, and runtime dispatch.
Weighted portfolio bundle construction and component contribution read models are also Streamlit-free services.
Saved portfolio replay execution and history context assembly are now Streamlit-free service work.
The UI still owns preset source dictionaries because `app/web/backtest_common.py` is Streamlit-adjacent, so it passes them to the service as a `ComparePresetCatalog`.

## Responsibility Split

| Layer | Responsibility |
| --- | --- |
| `app/web/backtest_compare.py` | form render, validation before submit, spinner, session state, history append, result render, weighted UI, `ComparePresetCatalog` assembly, saved replay UI side effects |
| `app/services/backtest_compare_execution.py` | manual multi-strategy execution loop, elapsed timing, error normalization |
| `app/services/backtest_compare_catalog.py` | strategy runner catalog, compare defaults, preset/manual universe resolution, runtime dispatch |
| `app/services/backtest_weighted_portfolio.py` | weighted portfolio result bundle construction, component metadata assembly |
| `app/services/backtest_result_read_model.py` | data trust rows, monthly component contribution amount/share views |
| `app/services/backtest_saved_portfolio_replay.py` | saved portfolio replay strategy rerun, weighted bundle creation, replay source context, history context assembly |
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

`build_weighted_portfolio_bundle(...)` receives already-built strategy result bundles and returns the same UI-facing weighted bundle shape as before.
It does not write history, mutate `st.session_state`, or render the result.

`replay_saved_portfolio_record(...)` receives a saved portfolio record, a strategy runner callback, and an optional dynamic input resolver callback.
It returns `SavedPortfolioReplayResult` with:

- component strategy bundles
- weighted portfolio bundle
- replay source context for session state
- compare history bundle/context
- weighted portfolio history context

It does not write history, mutate `st.session_state`, or render the result.
