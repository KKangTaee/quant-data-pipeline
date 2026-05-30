# Runs

- 2026-05-28: `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_dashboard.py tests/test_service_contracts.py` - PASS.
- 2026-05-28: `uv run python -m unittest tests.test_service_contracts` - PASS, 54 tests.
- 2026-05-28: Read-model smoke for TOP1000 daily snapshot refresh state - PASS.
- 2026-05-28: `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` - PASS.
- 2026-05-28: `git diff --check` - PASS.
- 2026-05-28: Browser smoke at `http://localhost:8501` - PASS; Market Movers rendered DB-only status text, `Next Check`, and enabled `Status Check` control.
