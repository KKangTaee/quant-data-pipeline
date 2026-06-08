# Runs

| Time | Command | Result |
|---|---|---|
| 2026-06-07 | `git status --short` | Dirty tree confirmed; unrelated local/user artifacts present. |
| 2026-06-07 | `rg -n "Futures|futures|OHLCV|Refresh Futures" ...` | Futures Monitor path located in Overview web, service, jobs, data collector, and contract tests. |
| 2026-06-07 | `.venv/bin/python -m unittest tests.test_service_contracts.FuturesMarketMonitoringContractTests.test_futures_monitor_anchors_chart_window_to_latest_stored_candle` | RED: old `UTC_TIMESTAMP()`-anchored query returned `MISSING` instead of `REVIEW`. |
| 2026-06-07 | `.venv/bin/python -m unittest tests.test_service_contracts.FuturesMarketMonitoringContractTests.test_futures_monitor_anchors_chart_window_to_latest_stored_candle` | GREEN after service query fix. |
| 2026-06-07 | `.venv/bin/python -m unittest tests.test_service_contracts.FuturesMarketMonitoringContractTests tests.test_service_contracts.FuturesMacroThermometerContractTests` | 15 tests passed. |
| 2026-06-07 | `.venv/bin/python -m py_compile app/services/futures_market_monitoring.py finance/data/futures_market.py app/jobs/overview_actions.py app/web/overview_dashboard.py` | Passed. |
| 2026-06-07 | `.venv/bin/python -m unittest tests.test_service_contracts` | 288 tests passed. |
| 2026-06-07 | `git diff --check` | Passed. |
| 2026-06-07 | `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` | PASS, no violations/advisories. |
| 2026-06-07 | Browser QA at `http://localhost:8502` | Futures Monitor rendered `Pre-open Core` symbols as `Stale` with latest stored data visible; screenshot saved as generated artifact `futures-monitor-stale-refresh-qa-20260607.png`. |
