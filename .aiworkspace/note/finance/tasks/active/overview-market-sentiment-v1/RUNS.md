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
