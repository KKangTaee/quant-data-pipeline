# Overview Market Context Macro Intersection V18 Runs

## Commands

- `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_adds_stored_futures_rate_pressure_condition_without_future_rows tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_conditioned_pilot_as_separate_context -q`
  - RED: 2 failed before implementation because `macro_condition_counts` was absent and the UI still used sequential GLD-then-futures copy.
  - GREEN: 2 passed after implementation.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests -q`
  - Result: 23 passed.
- `uv run python -m py_compile app/services/overview_market_context_analog.py app/web/overview_ui_components.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`
  - Result: 382 passed, 3 existing edgar deprecation warnings.
- `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true`
  - Browser QA: Market Context Macro section rendered `기본 유사 맥락 기준 / GLD 같은 상태 / 금리선물 같은 상태 / 두 조건 모두`.
  - Actual QA DOM showed counts `81 / 37 / 13 / 6` and no `GLD 조건 통과` sequential copy.
  - Screenshot: `overview-market-context-macro-intersection-v18-qa.png` generated artifact, not staged.
