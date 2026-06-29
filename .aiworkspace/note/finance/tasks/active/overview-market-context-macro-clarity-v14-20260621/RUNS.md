# Overview Market Context Macro Clarity V14 Runs

## 2026-06-21

### RED

```bash
uv run --with pytest python -m pytest \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_conditioned_pilot_as_separate_context \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_names_requested_effective_dates_and_macro_condition_roles \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_dimension_audit_inside_pilot \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_uses_median_strength_gradient_for_matrix \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_sector_pressure_map_renders_weighted_returns_with_two_decimals -q
```

Outcome: `5 failed` as expected. Failures showed the old `Macro 조건 비교`, old `사용 조건` chip group, old `Macro 조건 포함 핵심 자산` table title, no matrix strength variable, and 1-decimal sector pressure values.

### Focused GREEN

```bash
uv run --with pytest python -m pytest \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_conditioned_pilot_as_separate_context \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_names_requested_effective_dates_and_macro_condition_roles \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_dimension_audit_inside_pilot \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_uses_median_strength_gradient_for_matrix \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_sector_pressure_map_renders_weighted_returns_with_two_decimals -q
```

Outcome: `5 passed`.

### Focused Regression

```bash
uv run --with pytest python -m pytest \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_keeps_context_only_language \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_explains_similarity_before_statistics \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_prioritizes_matrix_and_collapses_stat_tables \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_turns_insufficient_data_into_actionable_gap_panel \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_conditioned_pilot_as_separate_context \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_names_requested_effective_dates_and_macro_condition_roles \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_dimension_audit_inside_pilot \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_uses_median_strength_gradient_for_matrix \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_sector_pressure_map_renders_weighted_returns_with_two_decimals -q
```

Outcome: `9 passed`.

### Static And Full Contract

```bash
git diff --check
uv run python -m py_compile app/web/overview_ui_components.py app/services/overview_market_context_analog.py app/services/overview_market_intelligence.py app/web/overview_dashboard_helpers.py
uv run --with pytest python -m pytest tests/test_service_contracts.py -q
```

Outcome: `git diff --check` and py_compile passed with no output. Full contract result: `382 passed, 3 warnings`.

### Browser QA

```bash
uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true
```

Playwright QA on `http://localhost:8525` confirmed:

- Sector pressure map still renders 11 tiles and now displays returns with 2 decimals such as `+1.80%`.
- Historical analog matrix renders median-strength style variables and shows the legend `색상은 중간값 방향과 크기 기준`.
- Macro conditioned comparison now shows `Macro 조건 후 결과 변화`, `기본 유사 맥락 기준`, `Macro 추가 조건`, broad vs conditioned deltas, and `현재 Macro 배경`.
- The old `Macro 조건 포함 핵심 자산` default title is no longer visible.
- QA screenshot: `overview-market-context-macro-clarity-v14-qa.png` (generated artifact, not staged).
