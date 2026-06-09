# Runs

## 2026-06-10

- `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_market_context_refresh_result_model_separates_issue_rows tests.test_service_contracts.OverviewAutomationContractTests.test_market_context_refresh_result_renderer_surfaces_issue_expander` -> RED, then GREEN.
- `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests` -> PASS, 38 tests.
- `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests` -> PASS, 77 tests.
- `uv run python -m py_compile app/web/overview_dashboard.py app/jobs/overview_actions.py tests/test_service_contracts.py` -> PASS.
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` -> PASS.
- `git diff --check` -> PASS.
- Browser QA at `http://localhost:8505/` -> PASS; refresh result UI displayed issue expander and full result expander. Screenshot: `overview-refresh-result-ux-v3-qa.png`.
