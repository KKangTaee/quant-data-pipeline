# Runs

- `RED`: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_mover_research_snapshot_does_not_flag_nearby_fiscal_quarter_as_missing` failed with `CHECK_REQUIRED == CHECK_REQUIRED` before tolerance fix.
- `GREEN`: focused 10-test Market Movers / statement collection set passed.
- `GREEN`: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests` passed 86 tests.
- `GREEN`: `.venv/bin/python -m py_compile finance/loaders/financial_statements.py finance/loaders/__init__.py app/services/overview/why_it_moved.py app/web/overview/market_movers_helpers.py app/web/overview/components/market_movers.py app/web/overview/components/common.py` passed.
- `GREEN`: `git diff --check` passed.
- Browser QA: `http://localhost:8517/?page=overview&overview_tab=market-movers` desktop and 390px viewport checked; no horizontal overflow. Screenshot saved as generated artifact at `.aiworkspace/note/finance/run_artifacts/market-movers-statement-collection-status-qa.png`.
