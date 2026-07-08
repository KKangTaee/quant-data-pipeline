# Runs

## 2026-07-09

- `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_interest_fetches_yfinance_analyst_metadata_with_session_only_rows`
  - RED: failed before service function existed.
  - GREEN: passed after yfinance normalization implementation.
- `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_interest_read_model_embeds_structured_analyst_rows_and_source_cards`
  - RED: failed while summary still said `구조화 소스 미연결`.
  - GREEN: passed after read-model integration.
- `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_interest_renderer_shows_structured_analyst_evidence_and_source_cards`
  - RED: failed before analyst tables were rendered.
  - GREEN: passed after renderer update.
- `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_mover_market_interest_fetch_includes_yfinance_analyst_metadata`
  - RED: failed before button flow called yfinance metadata fetch.
  - GREEN: passed after button flow wiring.
- `.venv/bin/python -m py_compile app/services/overview/market_interest.py app/web/overview/market_movers_helpers.py`
  - Passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests`
  - Passed: 141 tests.
  - Noted existing edgartools deprecation warnings and Streamlit MemoryCache warning in test environment.
- Browser QA:
  - URL: `http://localhost:8507`
  - Path: Overview > Market Movers > selected AKAM > `시장 관심 근거 확인` > `시장 관심`
  - Result: rendered `애널리스트 5건`, `최근 애널리스트 액션`, `목표가 요약`, `의견 분포`, `공개 페이지 교차확인`, `뉴스 리스트`, `SEC 공시 촉매`, and 13F caveats.
  - Screenshot artifact: `market-interest-analyst-multisource-qa.png` (generated, not for commit).
