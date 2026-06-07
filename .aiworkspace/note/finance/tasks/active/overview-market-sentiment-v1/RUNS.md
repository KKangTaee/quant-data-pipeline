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
| 2026-06-06 | `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests.test_market_sentiment_overlay_is_context_only_for_practical_validation` | RED: `build_market_sentiment_context_overlay` missing; then GREEN after adding Practical Validation sentiment overlay read model |
| 2026-06-06 | `.venv/bin/python -m unittest tests.test_service_contracts` | PASS: 255 tests |
| 2026-06-06 | `.venv/bin/python -m py_compile app/services/backtest_practical_validation.py app/services/overview_market_intelligence.py app/web/backtest_practical_validation.py app/web/backtest_practical_validation_components.py finance/loaders/sentiment.py` and `git diff --check` | PASS |
| 2026-06-06 | Browser QA `http://localhost:8507/backtest` | PASS: `Practical Validation`, `시장 심리 Context Overlay`, `Context only`, `Gate Effect`, `Trade Signal Disabled`, `Registry Write No` visible; no traceback / exception. Screenshot: `.aiworkspace/note/finance/run_artifacts/overview-market-sentiment-v1-pv-overlay-qa.png` |
| 2026-06-07 | `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests.test_market_sentiment_overlay_remains_context_only_on_downstream_surfaces` | RED: `surface` argument missing; then GREEN after adding surface-aware boundary fields `saved_setup_write=false` and `monitoring_signal=false` |
| 2026-06-07 | `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests.test_market_sentiment_overlay_remains_context_only_on_downstream_surfaces tests.test_service_contracts.PracticalValidationServiceContractTests.test_market_sentiment_overlay_is_context_only_for_practical_validation` | PASS: 2 tests |
| 2026-06-07 | `.venv/bin/python -m py_compile app/services/backtest_practical_validation.py app/web/backtest_practical_validation.py app/web/backtest_final_review.py app/web/final_selected_portfolio_dashboard.py` | PASS |
| 2026-06-07 | `.venv/bin/python -m unittest tests.test_service_contracts` | PASS: 256 tests |
| 2026-06-07 | `git diff --check` | PASS |
| 2026-06-07 | Browser QA `http://127.0.0.1:8508/backtest` | PASS: `Final Review` stage shows `시장 심리 Context Overlay`, `Context only`, `Gate Effect none`, `Trade Signal Disabled`, `Registry Write No`, `Saved Setup No write`; no traceback |
| 2026-06-07 | Browser QA `http://127.0.0.1:8508/selected-portfolio-dashboard` | PASS: `Portfolio Monitoring` shows `시장 심리 Context Overlay`, `Monitoring Signal Disabled`, `Saved Setup No write`, `PASS / BLOCKER No effect`, `Registry Write No`, `Order / Rebalance Disabled`; no traceback. Screenshot: `.aiworkspace/note/finance/run_artifacts/overview-market-sentiment-v1-stage3-qa.png` |
