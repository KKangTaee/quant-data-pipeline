# Overview Market Movers Quality V5 Runs

| Date | Command / QA | Result |
|---|---|---|
| 2026-06-29 | `PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_market_movers_coverage_trust_ui_keeps_raw_diagnostics_secondary tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_coverage_trust_model_groups_missing_diagnostics tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_coverage_trust_model_explains_nasdaq_no_universe` | RED confirmed: missing service function and UI wiring. |
| 2026-06-29 | Same command | PASS after implementation. |
| 2026-06-29 | `git diff --check` | PASS. |
| 2026-06-29 | `uv run python -m py_compile app/web/overview/market_movers.py app/web/overview/market_movers_helpers.py app/web/overview/components/market_movers.py app/services/overview/market_movers.py app/services/overview/why_it_moved.py` | PASS. |
| 2026-06-29 | `uv run python -m pytest tests/test_service_contracts.py -q -k "market_mover or market_movers or why_it_moved"` | Could not run: local venv has no `pytest` module. |
| 2026-06-29 | `PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_mover` | PASS: 43 tests. |
| 2026-06-29 | `PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k why_it_moved` | PASS: 6 tests. |
| 2026-06-29 | Browser QA on `http://localhost:8525` | PASS: S&P 500 Daily stale trust, S&P 500 Weekly partial trust/raw diagnostics, Nasdaq no-universe trust/action/empty state, and 390px narrow viewport. Screenshot: `.aiworkspace/note/finance/run_artifacts/overview-market-movers-quality-v5-qa.png`. |
