# Runs

Status: Active
Last Updated: 2026-06-18

| Command | Result |
|---|---|
| `git status --short` | Existing unrelated local changes only: `finance/.DS_Store`, `.superpowers/`. |
| `uv run python -m py_compile app/services/overview_market_intelligence.py app/services/overview_market_context_analog.py app/web/overview_ui_components.py app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py app/jobs/overview_actions.py` | Passed. |
| `uv run python -m pytest tests/test_service_contracts.py -q` | Failed: current venv had no `pytest` module. |
| `uv run --with pytest python -m pytest tests/test_service_contracts.py -q` | Passed: 354 passed, 3 warnings from existing `edgar` deprecations. |
| `git diff --check` | Passed. |
| `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true` | Started local Browser QA server. Stopped after QA. |
| Browser QA `http://localhost:8525` | Passed: Market Context rendered summary, market brief, source/action next checks, historical analog metadata, source footer, and secondary refresh assist. Console errors: 0. Screenshot: `overview-market-context-next-checks-qa.png`. |
