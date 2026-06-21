# Overview Market Context Macro Polish V17 Runs

## Commands

- `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_conditioned_pilot_as_separate_context tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_names_requested_effective_dates_and_macro_condition_roles tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_dimension_audit_inside_pilot -q`
  - RED: 3 failed before implementation because the condition meaning text and new Macro backdrop title/classes were absent.
  - GREEN: 3 passed after implementation.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests -q`
  - Result: 23 passed.
- `uv run python -m py_compile app/web/overview_ui_components.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`
  - Result: 382 passed, 3 existing edgar deprecation warnings.
- `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true`
  - Browser QA: Market Context Macro section rendered condition meaning text and reference Macro backdrop state / ratio cards.
  - Screenshot: `overview-market-context-macro-polish-v17-qa.png` generated artifact, not staged.
