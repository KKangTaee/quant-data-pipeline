# Overview Market Context Analog Usability V12 Runs

## 2026-06-21

- `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests -q`
  - RED: 3 expected failures before implementation.
  - GREEN: 21 passed after service/UI changes.
- `git diff --check`
  - Passed.
- `uv run python -m py_compile app/services/overview_market_context_analog.py app/web/overview_ui_components.py app/web/overview_dashboard.py`
  - Passed.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`
  - Passed: 378 passed, 3 warnings from `edgar` deprecations.
- `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true`
  - Browser QA passed for Market Context latest/default, selected as-of, 20D pattern, stale basis repair action, matrix render, support summary, and collapsed detail tables.
  - Screenshot artifacts created and intentionally not staged:
    - `overview-market-context-analog-usability-v12-qa.png`
    - `overview-market-context-analog-usability-v12-matrix-qa.png`
