# Overview Data Health Ingestion Handoff V1 Runs

Status: Active
Created: 2026-06-08

## Runs

- `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_overview_data_health_handoff_ranks_problem_rows_and_points_to_collection_surfaces`
  - RED: failed with missing `build_overview_data_health_ingestion_handoff`.
  - GREEN: passed after service implementation.
- `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_data_health_tab_renders_ingestion_handoff_before_raw_status_table`
  - RED: failed with missing `render_data_health_ingestion_handoff` call.
  - GREEN: passed after UI wiring.
- `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests`
  - Passed: 61 tests.
- `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_dashboard_helpers.py app/web/overview_ui_components.py app/web/overview_dashboard.py`
  - Passed.
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
  - Passed: hard violations none, advisories none.
- `git diff --check`
  - Passed.
- Browser QA: `http://127.0.0.1:8503`
  - Confirmed `Data Health Handoff` renders before `Ops Status`.
  - Screenshot: `overview-data-health-ingestion-handoff-v1-qa.png` generated locally and left unstaged.
