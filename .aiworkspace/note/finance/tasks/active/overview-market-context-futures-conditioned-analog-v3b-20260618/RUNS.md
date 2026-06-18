# Runs

Status: Active
Last Updated: 2026-06-18

| Command | Result | Notes |
|---|---|---|
| `git status --short` | Done | Pre-work dirty tree contained only existing forbidden/generated items: `finance/.DS_Store`, `.superpowers/`, and prior QA screenshots. |
| `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "...historical_analog..."` | Expected fail | Red state: `build_historical_analog_snapshot()` did not yet accept `futures_history`. |
| `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "...historical_analog..."` | Pass | Focused 4-test TDD slice passed after implementation. |
| `git diff --check` | Pass | No whitespace errors. |
| `uv run python -m py_compile app/services/overview_market_context_analog.py app/services/futures_macro_thermometer.py app/web/overview_ui_components.py app/web/overview_dashboard_helpers.py finance/loaders/futures.py` | Pass | Requested compile command exited 0. |
| `uv run --with pytest python -m pytest tests/test_service_contracts.py -q` | Pass | 361 passed, 3 third-party `edgar` deprecation warnings. |
| `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true` | Pass | Local Streamlit server started on `http://localhost:8525`. |
| Browser QA | Pass | `Workspace > Overview > Market Context`, pattern `20D`: broad sample 69, Macro sample 1, GLD condition row, Rate Pressure futures proxy row, no forbidden Korean copy. Screenshot: `overview-market-context-futures-conditioned-analog-v3b-qa.png`. |
