# Runs

- 2026-05-29: `uv run python -m py_compile app/jobs/overview_automation.py tests/test_service_contracts.py` - PASS.
- 2026-05-29: `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests` - PASS, 4 tests.
- 2026-05-29: `uv run python -m app.jobs.overview_automation --profile standard --dry-run --json` - PASS; printed due/skip plan without provider calls.
- 2026-05-29: `uv run python -m app.jobs.overview_automation --profile events --dry-run` - PASS; events-only plan printed 3 due calendar jobs without provider calls.
- 2026-05-29: `uv run python -m app.jobs.overview_automation --profile safe --job sp500_intraday --dry-run --json` - PASS; outside-hours guard skipped intraday job.
- 2026-05-29: `uv run python -m py_compile app/jobs/overview_automation.py app/jobs/ingestion_jobs.py app/jobs/run_history.py app/web/overview_dashboard.py app/services/overview_market_intelligence.py finance/data/market_intelligence.py tests/test_service_contracts.py` - PASS.
- 2026-05-29: `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` - PASS.
- 2026-05-29: `uv run python -m unittest tests.test_service_contracts` - PASS, 62 tests.
- 2026-05-29: `git diff --check` - PASS.
