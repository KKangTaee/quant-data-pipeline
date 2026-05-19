# UI Engine Boundary Foundation Status

Status: Active
Created: 2026-05-19

## Current State

- Phase created after user approval.
- First task `ui-engine-boundary-audit` is complete.
- First implementation task `backtest-execution-service-boundary` is complete.
- `compare-service-boundary` implementation is complete.
- `practical-validation-service-boundary` first implementation slice is complete.
- Product code now has Single Strategy execution service, manual Compare execution service, Compare runner catalog service, result read model service, weighted portfolio builder service, saved replay data assembly service boundary, and Practical Validation source/result handoff service boundary.

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

Continue with `evidence-read-model-boundary` after Practical Validation service boundary verification.

Reason:

- Single Strategy and Compare service slices proved the `app/services` boundary.
- Practical Validation now has a first service contract without moving provider gap jobs or changing diagnostics.
- Final Review / Selected Dashboard evidence read models are the remaining boundary area in this phase.

## Next Action

Start `evidence-read-model-boundary`.
First inspect Final Review and Selected Dashboard helpers to identify shared read-only evidence construction that can move to `app/services` without changing selected dashboard write policy.
