# Futures Monitor Dedup UX V1 Runs

| Time | Command | Result |
|---|---|---|
| 2026-06-23 09:00 KST | `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_futures_monitor_command_summary_owns_page_state_without_provider_rows tests.test_service_contracts.OverviewAutomationContractTests.test_futures_monitor_live_summary_line_avoids_repeating_top_move_or_run tests.test_service_contracts.OverviewAutomationContractTests.test_futures_monitor_macro_support_items_do_not_repeat_scenario` | RED confirmed. All 3 tests error because `_futures_command_summary_items`, `_futures_live_summary_line`, and `_macro_support_items` do not exist yet. |
| 2026-06-23 09:02 KST | Same 3-test command | GREEN after adding summary helper contracts and initial UI ownership split. |
| 2026-06-23 09:05 KST | `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.FuturesMacroThermometerContractTests tests.test_service_contracts.FuturesMarketMonitoringContractTests` | PASS. 91 tests passed. Existing edgar deprecation / Streamlit cache warnings only. |
| 2026-06-23 09:06 KST | `uv run python -m py_compile app/web/overview_dashboard.py tests/test_service_contracts.py` | PASS. |
| 2026-06-23 09:06 KST | `git diff --check` | PASS. |
| 2026-06-23 09:09 KST | 3-test command after shortening Macro confidence value | First attempt failed because the test concatenated label and value into a false positive; adjusted the assertion to check the value field directly, then PASS. |
| 2026-06-23 09:09 KST | `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.FuturesMacroThermometerContractTests tests.test_service_contracts.FuturesMarketMonitoringContractTests` | PASS. 91 tests passed. Existing edgar deprecation / Streamlit cache warnings only. |
| 2026-06-23 09:10 KST | Browser QA on `http://localhost:8503` | PASS. Confirmed command center owns page-level state, Macro support strip no longer repeats scenario, confidence value is shortened, Live Chart header no longer repeats top move / provider run rows. Saved `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev/futures-monitor-dedup-ux-v1-qa.png`. |
| 2026-06-23 09:16 KST | Focused 3-test command, py_compile + `git diff --check`, then 91-test command after restoring non-duplicate status pill tone | PASS. Browser screenshot was refreshed at `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev/futures-monitor-dedup-ux-v1-qa.png`. |
