# Overview Market Context Tab V1 Runs

## Commands

- RED: `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_renders_market_context_as_first_deep_tab tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_renders_macro_context_cockpit_inside_market_context_tab tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_renders_ia_closeout_guide_inside_market_context_tab_after_cockpit` -> failed because the first `Market Context` tab/helper did not exist.
- GREEN focused: same command -> `Ran 3 tests ... OK`.
- Regression: `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests` -> `Ran 34 tests ... OK`.
- Regression: `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests` -> `Ran 73 tests ... OK`.
- Compile: `uv run python -m py_compile app/web/overview_dashboard.py tests/test_service_contracts.py` -> OK.
- Boundary: `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` -> PASS.
- Whitespace: `git diff --check` -> OK.
- Browser QA: `http://localhost:8505/` shows `Market Context` as selected first tab with refresh button, cockpit, Deep Tab guide, and Source Confidence in the same tab.
