# Runtime Package Boundary Risks

## Open Risks

- `app/services/backtest_practical_validation_diagnostics.py` and replay service still depend on Streamlit-free Practical Validation helpers under `app/web`; boundary lint reports these as advisory.
- Runtime module import loads non-UI dependencies from finance core; this is expected, but it must not load Streamlit.

## Closed In This Task

- `app.web.runtime` stale Python imports removed.
- `app/runtime` is included in boundary lint hard checks for Streamlit import / `st.*` usage.
