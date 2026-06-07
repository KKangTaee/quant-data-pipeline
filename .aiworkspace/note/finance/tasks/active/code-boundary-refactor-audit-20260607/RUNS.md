# Runs

Status: Complete
Last Updated: 2026-06-07

| Time | Command | Result |
|---|---|---|
| 2026-06-07 | `git status --short --branch` | Clean, `master...origin/master` |
| 2026-06-07 | `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` | PASS; hard violations none, advisories none |
| 2026-06-07 | `rg -n "(import streamlit|from streamlit)" app finance tests` | Streamlit imports only in `app/web` |
| 2026-06-07 | `rg -n "from app\\.web|import app\\.web|app\\.web\\." app/runtime app/services finance app/jobs tests` | Production reverse import not found; tests import some web helpers |
| 2026-06-07 | `rg -n "requests\\.|urllib|urlopen|httpx|aiohttp|yfinance|FRED|EDGAR|Google News" app/web` | Text / job-trigger evidence found; no direct provider library import in UI |
| 2026-06-07 | `wc -l app/web/*.py app/web/pages/*.py app/services/*.py app/runtime/*.py app/jobs/*.py finance/*.py finance/data/*.py finance/loaders/*.py` | Largest files: `backtest_compare.py`, `app/runtime/backtest.py`, `overview_dashboard.py`, `final_selected_portfolios.py`, `streamlit_app.py` |
| 2026-06-07 | Python AST function/class length scan | Largest functions: `_render_ingestion_console`, `_render_strategy_compare_workspace`, `build_practical_validation_result`, `_render_real_money_details` |
| 2026-06-07 | `git ls-files .aiworkspace/note/finance/run_history .aiworkspace/note/finance/run_artifacts .aiworkspace/note/finance/backtest_artifacts .playwright-mcp` | Only `run_history/README.md` tracked |
| 2026-06-07 | `rg -n "\\.note/finance|\\.note\\/finance|Path\\([^)]*\\.note|FINANCE_NOTE_DIR.*\\.note" app finance tests` | Code does not recreate legacy `.note/finance`; test has negative assertion only |
| 2026-06-07 | `curl -fsS http://localhost:8501/_stcore/health` | `ok` |
| 2026-06-07 | `git diff --check` | PASS |
| 2026-06-07 | `.venv/bin/python -m py_compile app/web/streamlit_app.py app/web/overview_dashboard.py app/web/backtest_compare.py app/web/backtest_result_display.py app/web/backtest_single_forms.py app/web/pages/backtest.py app/runtime/backtest.py app/runtime/final_selected_portfolios.py app/services/overview_market_intelligence.py app/services/backtest_practical_validation_diagnostics.py app/jobs/ingestion_jobs.py` | PASS |
| 2026-06-07 | `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests.test_service_imports_do_not_load_streamlit tests.test_service_contracts.PracticalValidationServiceContractTests.test_runtime_package_import_does_not_load_streamlit tests.test_service_contracts.BoundaryContractHardeningTests.test_app_web_import_is_hard_boundary_violation` | PASS; 3 tests |
| 2026-06-07 | `rg -n "5차|code-boundary-refactor-audit-20260607" .aiworkspace/note/finance/docs .aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md .aiworkspace/note/finance/tasks/active/README.md .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md` | Expected pointers found |
| 2026-06-07 | `! rg -n "현재 4차|Latest completed task: .*post-merge-verification|Do not stage .*\\.note" .aiworkspace/note/finance/docs/INDEX.md .aiworkspace/note/finance/docs/ROADMAP.md .aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md .aiworkspace/note/finance/tasks/active/README.md .aiworkspace/note/finance/tasks/active/post-merge-verification-handoff-20260607/HANDOFF.md .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md` | No stale current-state pointers found |
