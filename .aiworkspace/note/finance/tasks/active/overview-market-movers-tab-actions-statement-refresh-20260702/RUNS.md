# Runs

- 2026-07-02: `.venv/bin/python -m pytest ...` failed because `pytest` is not installed in the local `.venv`; switched to `unittest`.
- 2026-07-02: `.venv/bin/python -m unittest` focused red run failed as expected on missing `fetch_market_mover_news_metadata`, `fetch_market_mover_sec_metadata`, `merge_market_mover_metadata`, statement refresh action, and old combined button source contract.
- 2026-07-02: `.venv/bin/python -m py_compile app/services/overview/why_it_moved.py app/jobs/overview_actions.py app/web/overview/market_movers_helpers.py` passed.
- 2026-07-02: Focused green unittest for 8 new/changed contracts passed.
- 2026-07-02: Existing compact metadata regression unittest group passed.
- 2026-07-02: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests` passed: 227 tests OK.
- 2026-07-02: Browser QA on `http://localhost:8502` passed for tab-local action visibility and 1280px horizontal overflow check; screenshot saved as generated artifact `browser-qa-market-movers-sec-tab.png`.
- 2026-07-02: Fresh closeout verification passed: `py_compile`, OverviewAutomation / OverviewMarketIntelligence unittest classes (227 tests), and `git diff --check`.
