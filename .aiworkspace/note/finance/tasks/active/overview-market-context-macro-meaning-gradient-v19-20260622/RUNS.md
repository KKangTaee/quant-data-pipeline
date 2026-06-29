# Runs

## 2026-06-22

- `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_dimension_audit_inside_pilot tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_uses_median_strength_gradient_for_matrix -q`
  - RED: failed before implementation because state-meaning copy and gradient class were absent.
- Same command after implementation
  - GREEN: `2 passed`.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_conditioned_pilot_as_separate_context tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_dimension_audit_inside_pilot tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_uses_median_strength_gradient_for_matrix -q`
  - `3 passed`.
- `uv run python -m py_compile app/web/overview_ui_components.py`
  - Passed.
- `git diff --check`
  - Passed.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests -q`
  - `23 passed`.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`
  - `382 passed, 3 existing edgar deprecation warnings`.
- `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true`
  - Browser QA passed. Verified `Macro 조건 결과 비교`, 30 gradient cells, and T10Y3M / VIXCLS / BAA10Y meaning copy in DOM.
  - Screenshot: `overview-market-context-macro-meaning-gradient-v19-qa.png`.
