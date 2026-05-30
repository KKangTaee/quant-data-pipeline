# Runs

- `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py app/jobs/run_history.py tests/test_service_contracts.py`
  - Result: PASS
- `uv run python -m unittest tests.test_service_contracts`
  - Result: PASS, 45 tests
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
  - Result: PASS, hard violations none, advisories none
- `uv run python - <<'PY' ... load_overview_collection_ops_snapshot() ... PY`
  - Result: PASS
  - Local DB snapshot: `REVIEW`, 6 targets, 3 OK, 3 stale, 0 missing, 0 failed, 0 partial
  - OK: S&P 500 Universe, FOMC Calendar, Earnings Calendar
  - Stale: S&P 500 Daily Snapshot, Top1000 Daily Snapshot, Top2000 Daily Snapshot
- `git diff --check`
  - Result: PASS
- Browser smoke on `http://localhost:8501`
  - Result: PASS
  - Verified top-level `Data Health` tab, `Ops Status=REVIEW`, `Healthy=3 / 6`, warning banner, status badges, and ops table rows.
