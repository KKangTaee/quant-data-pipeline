# Runs

- `rg -n "Events tab is intentionally a placeholder|first build에서는 next-slice|earnings collector remains|현재 slice에서는 DB-backed snapshot reload|Calendar ingestion remains a later task|FOMC / earnings ingestion is implemented" .aiworkspace/note/finance/phases/active/overview-market-intelligence .aiworkspace/note/finance/docs -S`
  - Result: no stale wording matches after cleanup.
- `uv run python -m py_compile app/web/overview_dashboard.py app/web/streamlit_app.py app/jobs/ingestion_jobs.py finance/data/market_intelligence.py`
  - Result: pass.
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
  - Result: PASS, hard violations none, advisories none.
- `uv run python -m unittest tests.test_service_contracts`
  - Result: 39 tests passed.
- `git diff --check`
  - Result: pass.
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
  - Result: no missing checklist items; generated artifacts not detected.
