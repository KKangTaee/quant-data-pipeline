# Runs

- 2026-05-29: `uv run python -m py_compile app/jobs/overview_automation.py tests/test_service_contracts.py` - PASS.
- 2026-05-29: `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests` - PASS, 6 tests.
- 2026-05-29: `uv run python -m app.jobs.overview_automation --profile browser_safe --dry-run --json` - PASS; plan included only `sp500_intraday` and skipped outside US market hours.
- 2026-05-29: `uv run python -m py_compile app/web/overview_dashboard.py tests/test_service_contracts.py` - PASS.
- 2026-05-29: `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests` - PASS, 7 tests.
- 2026-05-29: `uv run python -m app.jobs.overview_automation --profile browser_safe --dry-run --json` - PASS; plan still includes only `sp500_intraday`.
- 2026-05-29: `uv run python -m unittest tests.test_service_contracts` - PASS, 68 tests.
- 2026-05-29: `git diff --check` - PASS.
- 2026-05-29: Browser smoke at `http://localhost:8501` Overview top panel - PASS; toggle ON displayed `skipped` / `outside US market hours`, console errors 0. Toggle was turned back off after smoke.
- 2026-05-29: `uv run python -m py_compile app/jobs/overview_automation.py app/web/overview_dashboard.py app/services/overview_market_intelligence.py tests/test_service_contracts.py` - PASS.
- 2026-05-29: `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests` - PASS, 22 tests.
- 2026-05-29: `uv run python -m unittest tests.test_service_contracts` - PASS, 69 tests.
- 2026-05-29: `uv run python -m app.jobs.overview_automation --profile browser_safe --dry-run --json` - PASS.
- 2026-05-29: Browser smoke Data Health tab - PASS; `Latest Auto` card rendered, console errors 0.
