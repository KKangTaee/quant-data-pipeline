# Runs

| Time | Command | Result |
|---|---|---|
| 2026-06-21 | `git status --short` | Existing local generated/untracked artifacts only before V11 edits. |
| 2026-06-21 | `git log --oneline --decorate -12` | Latest commit before V11: `184d364c Overview Market Context analog 기준일 보정`. |
| 2026-06-21 | `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_explains_similarity_before_statistics tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_conditioned_pilot_as_separate_context tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_names_requested_effective_dates_and_macro_condition_roles tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_dimension_audit_inside_pilot -q` | RED: 4 failed before implementation; GREEN: 4 passed after implementation. |
| 2026-06-21 | `git diff --check` | Passed. |
| 2026-06-21 | `uv run python -m py_compile app/web/overview_ui_components.py app/web/overview_dashboard.py` | Passed. |
| 2026-06-21 | `uv run --with pytest python -m pytest tests/test_service_contracts.py -q` | Passed: 377 passed, 3 warnings. |
| 2026-06-21 | `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true` | Browser QA server started on `http://localhost:8525`. |
| 2026-06-21 | Browser QA | Confirmed Market Context renders closed-session brief, historical analog basis controls, selected-as-of warning, 20D / monthly pattern changes, and separated Macro comparison section. Screenshots: `overview-market-context-analog-macro-ux-v11-qa.png`, `overview-market-context-analog-macro-ux-v11-macro-qa.png` (generated, not staged). |
