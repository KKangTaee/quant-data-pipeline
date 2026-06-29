# Runs

## 2026-06-16

- `git branch --show-current` -> `codex/sub-dev`.
- `git status --short` -> pre-existing `finance/.DS_Store`, `.superpowers/`, and multiple QA screenshots are present.
- Read required docs and inspected Market Movers render / service / action files.
- Red test: `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_movers_refresh_action_collects_eod_history_through_ohlcv_job tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_movers_refresh_action_uses_large_universe_loader_for_top1000 tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_movers_refresh_bar_renders_eod_action_for_non_daily_without_auto_mode` -> failed because the EOD action facade and non-daily refresh helper were missing.
- Green test: same focused unittest command -> OK, 3 tests.
- `git diff --check` -> OK.
- `uv run python -m py_compile app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py app/services/overview_market_intelligence.py app/jobs/overview_actions.py app/jobs/ingestion_jobs.py` -> OK.
- Requested pytest command `uv run python -m pytest tests/test_service_contracts.py -k "overview and market and refresh" -q` -> failed because `pytest` is not installed in the current environment.
- Substitute focused unittest command -> OK, 3 tests. It emits existing `edgar` deprecation warnings.
- `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true` -> local app started for Browser QA, then stopped after QA.
- Browser QA: Daily retained intraday snapshot refresh / universe refresh / manual-auto mode; Weekly, Monthly, and Yearly each showed `가격 이력 갱신` with EOD period copy and no auto refresh selector.

## 2026-06-16 Hot-Reload Import Follow-Up

- User reported `ImportError: cannot import name 'run_overview_market_movers_eod_history' from 'app.jobs.overview_actions'`.
- `uv run python - <<'PY' ... from app.jobs.overview_actions import run_overview_market_movers_eod_history ... PY` -> direct import from the current worktree succeeds.
- `ps` showed an older Streamlit process still running on port 8501. Root cause is consistent with Streamlit hot-reload re-importing `overview_dashboard.py` while an already-loaded `overview_actions` module object did not yet have the new symbol.
- Added regression guard so `overview_dashboard.py` does not direct-import the new action symbol at import time; the action helper resolves it from the module at execution time and reloads the module if needed.
- `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_movers_refresh_bar_renders_eod_action_for_non_daily_without_auto_mode` -> red before patch, then green after patch.
- Focused 3-test unittest command -> OK.
- Direct app import check -> `overview_actions_import_ok=True`, `overview_dashboard_import_ok=True`.
- `uv run python -m py_compile app/web/overview_dashboard.py app/jobs/overview_actions.py tests/test_service_contracts.py` -> OK.
