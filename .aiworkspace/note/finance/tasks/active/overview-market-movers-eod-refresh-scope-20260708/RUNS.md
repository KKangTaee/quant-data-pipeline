# Runs

- 2026-07-08: RED targeted unittest failed as expected because `run_overview_market_movers_eod_history` did not accept `as_of_date`, preflight builder was missing, Top universe loader was still market-cap based, and React payload did not expose preflight.
- 2026-07-08: GREEN targeted unittest:
  - `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_movers_eod_history_accepts_effective_as_of_date_to_skip_current_symbols tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_movers_eod_history_batches_delta_by_start_date tests.test_service_contracts.OverviewAutomationContractTests.test_market_movers_eod_refresh_preflight_explains_collection_scope tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_movers_refresh_action_uses_liquidity_universe_loader_for_top1000 tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_react_actions_include_price_history_refresh_for_non_daily tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_react_event_bridge_dispatches_eod_history_refresh_once`
  - Result: OK, 6 tests.
- 2026-07-08: Broader regression unittest:
  - `.venv/bin/python -m unittest` with 13 focused Market Movers action / React dispatch tests.
  - Result: OK, 13 tests.
- 2026-07-08: `.venv/bin/python -m py_compile app/jobs/overview_actions.py app/web/overview/market_movers_helpers.py`
  - Result: OK.
- 2026-07-08: `git diff --check -- app/jobs/overview_actions.py app/web/overview/market_movers_helpers.py app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx app/web/streamlit_components/market_movers_workbench/src/style.css tests/test_service_contracts.py`
  - Result: OK.
- 2026-07-08: `npm run build` in `app/web/streamlit_components/market_movers_workbench`
  - Result: OK.
- 2026-07-08: Browser QA on local Streamlit `http://localhost:8502/?overview_tab=market-movers`.
  - DOM confirmed Top1000 Weekly state and action text `가격 이력 갱신 최신 1,000개 스킵 가능`.
  - Screenshot saved as `browser-qa-market-movers-top1000-weekly.png`; screenshot is generated QA artifact and should not be committed unless explicitly requested.
