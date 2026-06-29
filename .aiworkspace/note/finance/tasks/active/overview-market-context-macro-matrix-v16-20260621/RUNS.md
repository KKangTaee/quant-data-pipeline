# Overview Market Context Macro Matrix V16 Runs

## Runs

- RED:
  - `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_conditioned_pilot_as_separate_context -q`
  - Result: failed as expected because `ov-macro-basis-bar` / `ov-macro-delta-matrix` did not exist yet.
- Focused GREEN:
  - Same command.
  - Result: 1 passed.
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
  - Confirmed `ov-macro-basis-bar` and `ov-macro-delta-matrix` render, old sample flow / delta table classes are gone, and current Macro backdrop labels are Korean-first.
  - Screenshot: `overview-market-context-macro-matrix-v16-qa.png`.
