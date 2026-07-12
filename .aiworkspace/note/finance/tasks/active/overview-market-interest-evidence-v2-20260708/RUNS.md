# Overview Market Interest Evidence V2 Runs

## Commands

- `2026-07-08` RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_interest_read_model_classifies_public_sources_without_recommendation tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_interest_summary_uses_conservative_statuses_from_existing_metadata tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_interest_v2_builds_evidence_sections_from_existing_metadata`
  - Result: failed as expected because V1 model still returned `market_interest_evidence_v1` and duplicated `원문 확인` states.
- `2026-07-08` GREEN: same three service tests.
  - Result: passed after adding V2 summary states, evidence sections, and source disclosure.
- `2026-07-08` RED/GREEN action fetch: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_mover_market_interest_react_event_fetches_existing_metadata_before_building_model`
  - Result: failed before the action called existing metadata fetchers; passed after `fetch_market_interest` fetched news / Korean news / SEC metadata before building the panel.
- `2026-07-08` RED/GREEN tab consolidation: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_market_movers_redesign_v2_phase5_uses_investigation_pane tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_selected_investigation_consolidates_market_interest_tabs`
  - Result: failed while old `뉴스` / `SEC 공시` / `외부 검색` tabs remained; passed after selected-symbol clue tabs were consolidated to `기본 지표` / `시장 관심`.
- `2026-07-08` RED/GREEN renderer: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_interest_renderer_uses_evidence_sections_not_original_link_tab`
  - Result: failed while renderer used V1 link tables; passed after rendering V2 evidence sections and lower `출처/원문 링크` disclosure.
- `2026-07-08` focused closeout: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests tests.test_service_contracts.OverviewAutomationContractTests.test_market_movers_redesign_v2_phase5_uses_investigation_pane tests.test_service_contracts.OverviewAutomationContractTests.test_market_mover_investigation_react_payload_hides_statement_action_when_current`
  - Result: passed, 138 tests.
- `2026-07-08` compile: `.venv/bin/python -m py_compile app/services/overview/market_interest.py app/web/overview/market_movers_helpers.py`
  - Result: passed.
- `2026-07-08` diff hygiene: `git diff --check`
  - Result: passed.
- `2026-07-09 KST` Browser QA: `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8518 --server.headless true --server.runOnSave false --server.fileWatcherType none`
  - Result: passed. Opened `http://localhost:8518/?overview_tab=market-movers`, confirmed selected-symbol clue tabs are `기본 지표` / `시장 관심`, clicked the React investigation `시장 관심 근거 확인` button, opened `시장 관심`, and verified summary cards plus news / Korean news / SEC filing rows and `기관 보유 배경 · 13F 지연 자료`.
  - Screenshots: `market-movers-market-interest-v2-qa.png`, `market-movers-market-interest-v2-rows-qa.png` generated locally and not intended for commit.
