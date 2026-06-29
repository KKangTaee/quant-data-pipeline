# Runs

## 2026-06-22

- RED:
  - `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewAutomationContractTests::test_overview_source_confidence_renders_status_board_not_diagnostic_table tests/test_service_contracts.py::OverviewAutomationContractTests::test_overview_market_context_refresh_bar_has_compact_no_action_state -q`
  - Result: failed as expected. Missing `ov-source-status-board` and `_render_overview_market_context_refresh_status_panel`.
- Focused GREEN:
  - `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewAutomationContractTests::test_overview_source_confidence_summary_exposes_scan_metrics_before_opening tests/test_service_contracts.py::OverviewAutomationContractTests::test_overview_source_confidence_groups_reference_and_meta_without_unresolved_copy tests/test_service_contracts.py::OverviewAutomationContractTests::test_overview_source_confidence_uses_ledger_language_without_review_gate_copy tests/test_service_contracts.py::OverviewAutomationContractTests::test_overview_source_confidence_renders_status_board_not_diagnostic_table tests/test_service_contracts.py::OverviewAutomationContractTests::test_overview_market_context_refresh_bar_has_compact_no_action_state -q`
  - Result: `5 passed`.
- Syntax / whitespace:
  - `uv run python -m py_compile app/web/overview_ui_components.py app/web/overview_dashboard.py`
  - Result: passed.
  - `git diff --check`
  - Result: passed.
- Full contract:
  - `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`
  - Result: `386 passed, 3 warnings`.
- Browser QA:
  - `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true`
  - Opened `http://localhost:8525`, `Workspace > Overview > Market Context`.
  - Confirmed source confidence renders `자료 상태 요약`, `시장 브리프 직접 자료`, `참고 / 관리 자료`, and refresh panel renders current no-action state.
  - Screenshot: `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev/overview-market-context-source-refresh-ux-v21-qa.png`.
