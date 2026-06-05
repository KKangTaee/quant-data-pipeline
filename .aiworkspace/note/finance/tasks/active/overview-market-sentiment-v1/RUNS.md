# Overview Market Sentiment V1 Runs

| Time | Command | Result |
|---|---|---|
| 2026-06-05 | Browser check `http://localhost:8501` | Overview tabs confirmed: Market Movers, Futures Monitor, Sector / Industry, Events, Data Health, Candidate Ops |
| 2026-06-05 | Focused `tests.test_service_contracts` sentiment contracts | PASS: 6 tests, including CNN parser, AAII parser/header contract, ingestion job wrapper, Overview snapshot, Data Health freshness |
| 2026-06-05 | `app.jobs.ingestion_jobs.run_collect_market_sentiment()` | PASS: `success`, CNN 260 rows + AAII 88 rows = 348 rows stored in `finance_meta.macro_series_observation` |
| 2026-06-05 | Service smoke `build_market_sentiment_snapshot()` | PASS: `OK`, CNN 54.742857 / neutral, AAII bearish 37.0%, bull-bear spread -0.7pp, 0 missing / 0 stale |
| 2026-06-05 | Browser QA `http://127.0.0.1:8502` | PASS: Overview Sentiment tab renders OK cards, trend chart, CNN Components, Table; no traceback after Altair v6 `cornerRadiusEnd` fix. Screenshot: `overview-market-sentiment-v1-qa.png` |
| 2026-06-05 | `.venv/bin/python -m unittest tests.test_service_contracts` | PASS: 245 tests |
| 2026-06-05 | `py_compile` for sentiment / ingestion / Overview files and `git diff --check` | PASS |
| 2026-06-05 | Focused `OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_snapshot_summarizes_cnn_and_aaii_context` | RED: `analysis` key missing, then GREEN after adding the Sentiment interpretation read model |
| 2026-06-05 | Browser QA `http://127.0.0.1:8502` | PASS: Sentiment tab renders `시장 심리 컨텍스트`, `분석 체크`, `드라이버 분해`, `다음 확인`; no traceback / code block leak. Screenshot: `overview-market-sentiment-analysis-ux-final-qa.png` |
| 2026-06-05 | `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_snapshot_summarizes_cnn_and_aaii_context tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_collection_ops_snapshot_tracks_market_sentiment_freshness` | PASS: 2 tests |
| 2026-06-05 | `.venv/bin/python -m unittest tests.test_service_contracts` | PASS: 245 tests |
| 2026-06-05 | `.venv/bin/python -m py_compile app/services/overview_market_intelligence.py app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py` and `git diff --check` | PASS |
| 2026-06-05 | Browser DOM QA `http://127.0.0.1:8502` | PASS: `시장 심리 컨텍스트`, `분석 체크`, `혼합 중립`, `드라이버 분해`, `다음 확인` present; no traceback / code block leak |
| 2026-06-05 | Focused `OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_snapshot_summarizes_cnn_and_aaii_context` | RED: old step titles `데이터 상태 / 공포·탐욕 판정 / 내부 드라이버`; GREEN after 6-step learning read model and `component_explanations` |
| 2026-06-05 | Browser QA `http://127.0.0.1:8502` | PASS: `시장 심리 읽기 - 6단계`, all 6 step titles, `CNN 구성요소 학습 노트`, `보는 것 / 현재 읽기`, `다음 확인` visible; no traceback / code block leak / `안전자산가` particle issue. Screenshots: `overview-market-sentiment-learning-final-qa.png`, `overview-market-sentiment-learning-components-qa.png` |
