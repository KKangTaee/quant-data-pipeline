# Runs

## 2026-06-07

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_overview_model_keeps_only_monitoring_and_health_lanes tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_console_model_hides_cleanup_artifacts_and_keeps_action_queue tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_console_model_uses_korean_operator_facing_copy tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_overview_source_hides_development_history_titles`
  - Result: FAIL as expected. Existing model still reported `operations_overview_v1`, `operations_console_v2_v5`, and source still contained development-history / archive decision titles.
- GREEN: same focused unittest command.
  - Result: PASS, 4 tests.
- Focused operations regression: `.venv/bin/python -m unittest tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_overview_model_keeps_only_monitoring_and_health_lanes tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_overview_model_keeps_execution_boundary_disabled tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_console_model_hides_cleanup_artifacts_and_keeps_action_queue tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_console_model_uses_korean_operator_facing_copy tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_overview_source_hides_development_history_titles tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_navigation_hides_archive_pages_from_top_level_tabs`
  - Result: PASS, 6 tests.
- Compile: `.venv/bin/python -m py_compile app/web/operations_overview.py tests/test_service_contracts.py`
  - Result: PASS.
- Browser QA: opened `http://localhost:8517/operations`.
  - Result: `Operations Console`, `Today's Operations Queue`, `Primary Operations`, `Portfolio Monitoring`, and `System / Data Health` visible.
  - Result: `Operations surface decisions`, `Operations restructuring roadmap`, `Hidden archive`, `Archive 도구`, and `과거 archive` count 0.
  - Screenshot: `operations-cockpit-cleanup-qa.png`.
- Diff / boundary checks:
  - `git diff --check`: PASS.
  - `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`: PASS.
  - `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`: PASS after root concise logs were updated.
