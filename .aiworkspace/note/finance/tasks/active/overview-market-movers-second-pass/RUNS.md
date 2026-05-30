# Runs

- 2026-05-30: Opened task; verification pending.
- 2026-05-30: `uv run python -m py_compile app/services/overview_market_intelligence.py` passed.
- 2026-05-30: Focused Market Movers / browser auto tests passed.
- 2026-05-30: Altair return / volume chart JSON serialization smoke passed.
- 2026-05-30: `uv run python -m app.jobs.overview_automation --profile browser_safe --dry-run --json` passed; current KST time is outside US market hours so no jobs ran.
- 2026-05-30: Browser QA on `http://localhost:8501` confirmed Market Movers and Volume Rank render without `KeyError`; screenshot saved to `/tmp/overview-market-movers-second-pass.png`.
- 2026-05-30: `uv run python -m py_compile app/web/overview_dashboard.py app/web/overview_ui_components.py app/jobs/overview_automation.py app/services/overview_market_intelligence.py` passed.
- 2026-05-30: `uv run python -m unittest tests.test_service_contracts` passed, 79 tests.
- 2026-05-30: `git diff --check` passed.
- 2026-05-30: Focused `OverviewMarketIntelligenceServiceContractTests` passed after adding daily and weekly `volume_rows` assertions.
- 2026-05-30: Actual DB timing after optimization: Top2000 weekly about 2.66s, monthly about 3.07s, yearly about 20.57s for Market Movers snapshot build; yearly remains dominated by eligible-date resolution.
- 2026-05-30: `uv run python -m unittest tests.test_service_contracts` passed, 80 tests.
- 2026-05-30: Browser QA on fresh Streamlit server `http://localhost:8510` confirmed `Volume Rank` and `Volume Table` render dedicated daily volume rows with console error count 0; screenshot saved to `/tmp/overview-volume-rank-period-aware-fresh.png`.
