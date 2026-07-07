# Runs

## 2026-07-07

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_movers_eod_history_uses_delta_refresh_for_stale_symbols
```

Result: passed.

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_market_movers_eod_refresh_result_caption_explains_smart_scope
```

Result: passed.

```bash
.venv/bin/python -m py_compile app/web/overview/market_movers_helpers.py app/jobs/overview_actions.py
git diff --check -- app/web/overview/market_movers_helpers.py tests/test_service_contracts.py .aiworkspace/note/finance/tasks/active/overview-market-movers-smart-eod-refresh-20260707
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_market_movers_eod_refresh_result_caption_explains_smart_scope tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_movers_refresh_bar_exposes_eod_action_for_non_daily_basic_ui
```

Result: passed.

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_movers_refresh_action_collects_eod_history_through_ohlcv_job \
  tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_movers_refresh_action_uses_large_universe_loader_for_top1000 \
  tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_movers_refresh_action_uses_nasdaq_directory_loader \
  tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_movers_eod_history_uses_delta_refresh_for_stale_symbols
```

Result: passed.
