# UI Engine Boundary Foundation Status

Status: Active
Created: 2026-05-19

## Current State

- Phase created after user approval.
- First task `ui-engine-boundary-audit` is complete.
- First implementation task `backtest-execution-service-boundary` is complete.
- `compare-service-boundary` implementation is complete.
- Product code now has Single Strategy execution service, manual Compare execution service, Compare runner catalog service, result read model service, weighted portfolio builder service, and saved replay data assembly service boundaries.

## Latest Findings

- `app/web` has 45 Python files.
- 18 `app/web` files import Streamlit.
- 19 `app/web` files use `st.session_state`.
- Heaviest session-state concentration:
  - `app/web/backtest_common.py`: 345 hits
  - `app/web/backtest_single_forms.py`: 337 hits
  - `app/web/backtest_compare.py`: 269 hits
  - `app/web/streamlit_app.py`: 78 hits
- `app/services` and `app/api` have no source `.py` files in the current worktree, only `__pycache__` traces.
- `app/web/runtime/backtest.py` is Streamlit-free and is a good transition dependency for services.

## Current Decision

Start with Single Strategy execution service extraction, not Compare or Practical Validation.

Reason:

- It is smaller than Compare.
- It directly addresses UI-engine execution coupling.
- It lets the phase establish a repeatable extraction pattern before touching larger workflows.

## Next Action

Start `practical-validation-service-boundary`.
First inspect `app/web/backtest_practical_validation.py` and helpers to separate pure diagnostic computation from Streamlit save / handoff behavior while preserving `NOT_RUN` semantics.
