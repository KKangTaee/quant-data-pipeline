# Operations Overview QA Runbook

Status: Active
Last Verified: 2026-06-08

## Purpose

Use this runbook when verifying `Operations > Operations Overview` after UI, routing, or documentation changes.

## Start The Local App

Use a free port. The examples below use `8508` because `8507` is often reused by prior QA sessions.

```bash
.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8508 --server.headless true --server.runOnSave false --server.fileWatcherType none
```

Expected result:

- Streamlit reports `Local URL: http://localhost:8508`.
- `curl -I --max-time 5 http://localhost:8508/` returns `200 OK`.

## Canonical Browser QA Path

1. Open `http://localhost:8508/`.
2. Use the top navigation menu.
3. Select `Operations > Operations Overview`.
4. Confirm the URL becomes `/operations`.
5. Confirm no `Page not found` dialog is visible.

Expected visible sections:

- `Operations Console`
- `Portfolio Monitoring Status`
- `Evidence Health`
- `Today's Operations Queue`
- `Primary Operations`
- Disabled `Live Approval`, `Order`, and `Auto Rebalance` badges

Expected queue fields:

- `Priority`
- `Evidence`
- `Metric`
- `주문 / 자동 리밸런싱 비활성`

## Direct Route Diagnostic

Direct first-load navigation to `http://localhost:8508/operations` can show Streamlit's `Page not found` dialog even while the Operations content renders.

Treat this as local direct-route QA noise when all of the following are true:

- Top-navigation entry from `/` to `Operations Overview` does not show the dialog.
- The page body renders `Operations Console`.
- The queue renders `Priority`, `Evidence`, and `Metric`.
- No archive / development-history copy is visible in the operator path.

If the dialog appears after normal top-navigation entry, treat it as a routing regression and investigate `app/web/streamlit_app.py`.

## Focused Verification Commands

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_overview_model_keeps_only_monitoring_and_health_lanes \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_overview_model_keeps_execution_boundary_disabled \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_console_model_hides_cleanup_artifacts_and_keeps_action_queue \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_console_model_uses_korean_operator_facing_copy \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_review_queue_prioritizes_blockers_scenarios_reviews_and_system_health \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_review_queue_source_renders_priority_and_evidence \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_overview_model_adds_portfolio_first_summary \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_overview_model_adds_evidence_health_strip \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_overview_source_renders_evidence_health_before_queue \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_overview_source_renders_portfolio_summary_before_queue \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_overview_source_hides_development_history_titles \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_navigation_hides_archive_pages_from_top_level_tabs
```

Expected result:

- `Ran 12 tests`
- `OK`

Also run:

```bash
.venv/bin/python -m py_compile app/web/operations_overview.py tests/test_service_contracts.py
git diff --check
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py
```

Expected result:

- py_compile exits 0.
- `git diff --check` prints no whitespace errors.
- UI / Engine Boundary Check prints `Result: PASS`.
- Finance Refinement Hygiene Check reports no missing checklist items.
