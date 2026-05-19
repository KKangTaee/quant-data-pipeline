# UI Engine Boundary Audit Notes

Status: Active
Created: 2026-05-19

## Summary

The current code already separates core engine code under `finance/*`, but the Streamlit-facing `app/web` layer still mixes UI state, runtime dispatch, registry persistence, and read-model construction.

The service boundary should be introduced between `app/web` and existing runtime/engine code, not as a replacement for the engine.

## Current Flow

```text
app/web/streamlit_app.py
  -> app/web/pages/backtest.py
  -> app/web/backtest_analysis.py
  -> app/web/backtest_single_*.py or app/web/backtest_compare.py
  -> app/web/runtime/backtest.py
  -> finance/loaders/*
  -> finance/sample.py
  -> finance/engine.py / finance/strategy.py / finance/transform.py
  -> finance/performance.py
  -> result bundle
  -> st.session_state / run_history / registries
```

## Evidence

| Finding | Evidence |
| --- | --- |
| `app/web` is large enough to treat as a UI product layer | 45 Python files |
| Streamlit dependency is broad | 18 `app/web` files import Streamlit |
| UI session state is widespread | 19 `app/web` files use `st.session_state` |
| Heaviest state files | `backtest_common.py` 345, `backtest_single_forms.py` 337, `backtest_compare.py` 269, `streamlit_app.py` 78 |
| Existing runtime adapter is useful | `app/web/runtime/backtest.py` has no Streamlit dependency |
| Current service/API source boundary is empty | `app/services` and `app/api` have no source `.py` files in this worktree |

## First Extraction Candidate

`app/web/backtest_single_runner.py`

Current mixed responsibilities:

- renders runtime payload
- opens Streamlit spinner
- dispatches strategy runtime based on payload strategy key
- catches input/data/system exceptions
- writes `st.session_state.backtest_last_*`
- appends run history
- renders success message

Recommended first extraction:

- move runtime dispatch, elapsed timing, and error normalization to `app/services/backtest_execution.py`
- leave payload render, spinner, session state writes, history append, success message in `app/web/backtest_single_runner.py` for the first slice

## Later Extraction Candidates

| Candidate | Why later |
| --- | --- |
| `app/web/backtest_compare.py` | Very large; contains strategy runner catalog, compare execution, weighted portfolio, saved replay, chart render, and session state |
| `app/web/backtest_practical_validation_helpers.py` | Important but overlaps active Practical Validation V2 and mixes diagnostics, persistence, and UI handoff |
| `app/web/runtime/final_selected_portfolios.py` | Mostly service-like already, but imports `app.web.backtest_candidate_library_helpers` for replay; handle after execution boundary pattern is stable |

## No-Go For First Implementation

- Do not modify `finance/strategy.py`.
- Do not modify `finance/engine.py`.
- Do not modify `finance/transform.py`.
- Do not modify `finance/performance.py`.
- Do not change DB schema or loaders.
- Do not change registry JSONL files.
- Do not change Streamlit session state key names.
- Do not introduce FastAPI, React, Next.js, or another UI framework.
