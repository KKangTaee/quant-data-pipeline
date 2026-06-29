# Operations Archive Tabs Removal Runs

## 2026-06-07

### RED

Command:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_overview_model_keeps_only_monitoring_and_health_lanes \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_console_model_exposes_v2_v5_audit_and_action_queue \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_console_model_uses_korean_user_facing_copy \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_navigation_hides_archive_pages_from_top_level_tabs
```

Result:

- Failed as expected before implementation.
- Failures showed archive lanes, archive decisions, and archive navigation entries were still present.

### GREEN

Command:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_overview_model_keeps_only_monitoring_and_health_lanes \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_console_model_exposes_v2_v5_audit_and_action_queue \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_console_model_uses_korean_user_facing_copy \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_navigation_hides_archive_pages_from_top_level_tabs
```

Result:

- Passed: 4 tests.
- Note: edgar dependency emitted deprecation warnings unrelated to this change.

### Pytest Availability

Command:

```bash
.venv/bin/python -m pytest tests/test_service_contracts.py -k "operations_overview_model or operations_console_model or operations_navigation" -q
```

Result:

- Failed before test execution because local venv has no `pytest` module.
- Used `unittest` instead.

### Final Focused Verification

Commands:

```bash
.venv/bin/python -m py_compile app/web/streamlit_app.py app/web/operations_overview.py tests/test_service_contracts.py
git diff --check
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py
```

Result:

- Passed.
- Stale archive navigation label search returned no matches in updated app/docs/test surfaces.

### Browser QA

Target:

```text
http://localhost:8517/operations
```

Result:

- Operations top navigation displayed only `Operations Overview`, `Portfolio Monitoring`, `System / Data Health`.
- DOM check confirmed no `Backtest Runs`, `Candidates`, or `Archive / Recovery` lane on the Operations screen.
- Screenshot: `operations-archive-tabs-removed-qa.png` generated as local QA artifact and not staged.
- Console note: Streamlit emitted `/operations/_stcore/*` 404 resource messages during direct route navigation; page rendered normally and DOM QA passed.
