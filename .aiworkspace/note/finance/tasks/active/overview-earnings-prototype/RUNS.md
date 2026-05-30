# Runs

- `uv run python -m py_compile finance/data/market_intelligence.py app/jobs/ingestion_jobs.py app/services/overview_market_intelligence.py app/web/overview_dashboard.py app/web/streamlit_app.py`
  - Result: pass.
- `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests`
  - Result: 14 tests passed.
- `uv run python -m unittest tests.test_service_contracts`
  - Result: 39 tests passed.
- `git diff --check`
  - Result: pass.
- `uv run python - <<'PY' ... run_collect_earnings_calendar(symbols=['AAPL','MSFT','NVDA'], symbol_source='manual', lookahead_days=180, max_symbols=10) ... PY`
  - Result: success, 3 rows written, 3 / 3 symbols processed, duration ~1.6 sec.
- `uv run python - <<'PY' ... load_latest_intraday_mover_symbols(universe_code='SP500', top_n=5) ... PY`
  - Result: returned latest mover symbols from stored S&P 500 intraday snapshot.
- Browser smoke at `http://localhost:8501`
  - Result: Overview Events renders All / FOMC / Earnings filter, refresh buttons, stored earnings events; Ingestion renders `Overview Market Event Calendar > Earnings Prototype` controls.
