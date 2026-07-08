# Runs

- 2026-07-09 RED:
  - `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_interest_read_model_embeds_structured_analyst_rows_and_source_cards`
  - `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_interest_renderer_shows_structured_analyst_evidence_and_source_cards`
- 2026-07-09 GREEN / regression:
  - `.venv/bin/python -m py_compile app/services/overview/market_interest.py app/web/overview/market_movers_helpers.py`
  - `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests`
  - `git diff --check`
- 2026-07-09 Browser QA:
  - `http://localhost:8509`에서 Overview > Market Movers > 선택 종목 조사 > 시장 관심 근거 확인 > 시장 관심 탭을 확인했다.
  - 확인 문구: `출처별 확인 상태`, `Yahoo Finance / yfinance`, `MarketWatch`, `WSJ Markets`, `Nasdaq.com`, `원문 교차확인`.
  - generated screenshot: `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev/market-interest-source-board-qa.png`
