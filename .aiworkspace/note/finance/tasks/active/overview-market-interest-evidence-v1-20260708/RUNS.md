# Overview Market Interest Evidence V1 Runs

## Commands

- `2026-07-08` RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_interest_read_model_classifies_public_sources_without_recommendation tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_interest_summary_uses_conservative_statuses_from_existing_metadata`
  - Result: failed as expected because `app.services.overview.market_interest` did not exist yet.
- `2026-07-08` GREEN: same two market-interest service tests.
  - Result: passed.
- `2026-07-08` RED/GREEN UI: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_market_movers_redesign_v2_phase5_uses_investigation_pane tests.test_service_contracts.OverviewAutomationContractTests.test_market_mover_investigation_react_payload_hides_statement_action_when_current tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_interest_read_model_classifies_public_sources_without_recommendation tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_interest_summary_uses_conservative_statuses_from_existing_metadata tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_selected_investigation_adds_market_interest_action_and_tab tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_mover_market_interest_react_event_sets_session_state_without_provider_fetch`
  - Result: passed after updating the selected-symbol action, tab, session state, and conservative copy contract.
- `2026-07-08` focused closeout: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests tests.test_service_contracts.OverviewAutomationContractTests.test_market_movers_redesign_v2_phase5_uses_investigation_pane tests.test_service_contracts.OverviewAutomationContractTests.test_market_mover_investigation_react_payload_hides_statement_action_when_current`
  - Result: passed, 135 tests.
- `2026-07-08` compile: `.venv/bin/python -m py_compile app/services/overview/market_interest.py app/web/overview/market_movers_helpers.py`
  - Result: passed.
- `2026-07-08` diff hygiene: `git diff --check`
  - Result: passed.
- `2026-07-08` Browser QA: `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8517 --server.headless true --server.runOnSave false --server.fileWatcherType none`
  - Result: passed. In-app browser opened `http://localhost:8517/?overview_tab=market-movers`, selected a Market Movers ticker, triggered `시장 관심 근거 확인` from the React investigation pane, opened the `시장 관심` tab, and confirmed analyst / news-SEC / 13F delayed context / original-link sections render with no live-buying phrase.
  - Screenshot: `market-movers-market-interest-qa.png` generated locally and not intended for commit.
