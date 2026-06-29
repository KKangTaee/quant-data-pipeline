# Runs

## 2026-06-22

- `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewAutomationContractTests::test_overview_dashboard_uses_lazy_selected_deep_tab_rendering tests/test_service_contracts.py::OverviewAutomationContractTests::test_overview_dashboard_dispatches_only_selected_deep_tab tests/test_service_contracts.py::OverviewAutomationContractTests::test_overview_dashboard_defaults_unknown_deep_tab_to_market_context -q`
  - RED first: expected failures before helper implementation.
  - GREEN after implementation: 3 passed.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewAutomationContractTests -q`
  - 68 passed.
- `uv run python -m py_compile app/web/overview_dashboard.py`
  - Passed.
- `git diff --check`
  - Passed.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`
  - 384 passed, 3 dependency deprecation warnings from `edgar`.
- `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true`
  - Browser QA completed at `http://localhost:8525`.
  - Confirmed default Overview renders `Market Context` content without `Market Movers` scan content.
  - Confirmed selecting `Market Movers` renders `Market Movers` on demand.
  - Screenshot: `overview-lazy-tab-render-v20-qa.png` (generated artifact, not staged).
