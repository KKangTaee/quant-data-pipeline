# Runs

- 2026-05-29: `uv run python -m py_compile finance/data/market_intelligence.py app/jobs/ingestion_jobs.py app/jobs/run_history.py app/web/overview_dashboard.py tests/test_service_contracts.py` - PASS.
- 2026-05-29: `uv run python -m unittest tests.test_service_contracts.MarketIntelligenceIngestionContractTests` - PASS, 4 tests.
- 2026-05-29: Direct smoke `run_diagnose_market_quote_gaps(symbols=['BK','PSTG'], universe_code='TOP1000')` - PASS; both classified as `provider_quote_gap`.
- 2026-05-29: Optimized direct smoke for current TOP1000 14 missing symbols - PASS; 4.78 sec, `provider_quote_gap: 14`.
- 2026-05-29: `uv run python -m unittest tests.test_service_contracts` - PASS, 58 tests.
- 2026-05-29: `git diff --check` - PASS.
- 2026-05-29: Browser smoke at `http://localhost:8501` - PASS; Overview rendered without import/runtime errors, console errors 0.
