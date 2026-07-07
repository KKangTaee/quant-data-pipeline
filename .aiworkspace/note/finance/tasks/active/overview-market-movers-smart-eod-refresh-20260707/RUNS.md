# Runs

## 2026-07-07

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_movers_eod_history_uses_delta_refresh_for_stale_symbols
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
