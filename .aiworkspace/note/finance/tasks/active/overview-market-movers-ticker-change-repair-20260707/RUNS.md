# Runs

- 2026-07-07: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_react_actions_include_ticker_alias_repair_when_candidates_exist tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_react_event_bridge_dispatches_ticker_alias_repair_once tests.test_service_contracts.MarketIntelligenceIngestionContractTests.test_market_symbol_alias_schema_tracks_ticker_change_repair_contract tests.test_service_contracts.MarketIntelligenceIngestionContractTests.test_market_symbol_alias_upsert_and_loader_are_idempotent tests.test_service_contracts.MarketIntelligenceIngestionContractTests.test_ticker_alias_candidates_are_detected_from_missing_quote_rows tests.test_service_contracts.MarketIntelligenceIngestionContractTests.test_top_universe_snapshot_uses_active_alias_for_quote_lookup_but_keeps_universe_symbol`
  - RED: expected failures confirmed missing `market_symbol_alias` schema, alias writer/loader, Market Movers alias probe, UI action, and snapshot alias resolution.
- 2026-07-07: Same focused unittest command.
  - GREEN: 6 tests passed.
- 2026-07-07: `.venv/bin/python -m py_compile finance/data/db/schema.py finance/data/market_intelligence.py app/services/overview/market_movers.py app/jobs/overview_actions.py app/web/overview/market_movers_helpers.py`
  - PASS.
- 2026-07-07: `git diff --check`
  - PASS.
- 2026-07-07: Browser QA at `http://localhost:8503`
  - PASS: Overview -> Market Movers rendered without app error; default DB state had no ticker alias candidate so `티커 변경 복구 적용` remained hidden as expected.
  - Screenshot: `browser-qa-market-movers-ticker-alias-repair.png`
