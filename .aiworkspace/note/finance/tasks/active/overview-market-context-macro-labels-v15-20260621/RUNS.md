# Overview Market Context Macro Labels V15 Runs

## Runs

- RED:
  - `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_conditioned_pilot_as_separate_context tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_names_requested_effective_dates_and_macro_condition_roles tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_dimension_audit_inside_pilot -q`
  - Result: 3 failed as expected for missing GLD / Rate Pressure labels, summary sentence, and Korean Macro backdrop explanations.
- GREEN focused:
  - Same command.
  - Result: 3 passed.
- Focused regression:
  - `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_keeps_context_only_language tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_explains_similarity_before_statistics tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_prioritizes_matrix_and_collapses_stat_tables tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_turns_insufficient_data_into_actionable_gap_panel tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_conditioned_pilot_as_separate_context tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_names_requested_effective_dates_and_macro_condition_roles tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_dimension_audit_inside_pilot tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_uses_median_strength_gradient_for_matrix tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_sector_pressure_map_renders_weighted_returns_with_two_decimals -q`
  - Result: 9 passed.
- Static:
  - `git diff --check`
  - `uv run python -m py_compile app/web/overview_ui_components.py app/services/overview_market_context_analog.py app/services/overview_market_intelligence.py app/web/overview_dashboard_helpers.py`
  - Result: passed.
- Full service contracts:
  - `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`
  - Result: 382 passed, 3 warnings.
- Browser QA:
  - `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true`
  - Confirmed Market Context shows `81회 -> 37회 -> 6회`, GLD / Rate Pressure stage labels, T10Y3M / VIXCLS / BAA10Y Korean descriptions, and broad-anchor same-state count wording.
  - Screenshot: `overview-market-context-macro-labels-v15-qa.png`.
