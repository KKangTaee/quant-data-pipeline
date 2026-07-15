# Institutional Portfolios Workspace V1 Runs

## 2026-07-08 - TDD Red

Command:

```bash
/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/.venv/bin/python tests/test_institutional_portfolios.py
```

Result:

- Failed as expected before implementation.
- Missing modules / contracts: `finance.data.institutional_13f`, `app.services.institutional_portfolios`, `collect_sec_13f_dataset`, and `render_institutional_portfolios_page`.

## 2026-07-08 - Focused Green

Command:

```bash
/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/.venv/bin/python tests/test_institutional_portfolios.py
```

Result:

- Passed: 5 tests.
- Streamlit / EDGAR warnings appeared during imports only.

## 2026-07-08 - SEC Source Check

Checked the official SEC Form 13F data sets page.

Result:

- 2026-07-08 page state exposed `2026 March April May 13F` as the latest data download.
- Implementation keeps the URL explicit in Ingestion and does not download in normal UI render.

## 2026-07-08 - Final Focused QA

Commands:

```bash
/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/.venv/bin/python tests/test_institutional_portfolios.py
PYTHONPATH=. /Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/.venv/bin/python tests/test_ingestion_module_split_contracts.py
/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/.venv/bin/python -m py_compile finance/data/institutional_13f.py finance/loaders/institutional_13f.py app/services/institutional_portfolios.py app/web/institutional_portfolios.py app/web/streamlit_app.py app/jobs/ingestion_jobs.py app/web/ingestion/dispatcher.py app/web/ingestion/guides.py app/web/ingestion/registry.py app/web/ingestion/sections.py
git diff --check
/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
```

Result:

- `tests/test_institutional_portfolios.py`: passed 5 tests.
- `tests/test_ingestion_module_split_contracts.py`: passed 7 tests with `PYTHONPATH=.`.
- `py_compile`: passed.
- `git diff --check`: passed.
- UI / Engine Boundary Check: `Hard violations: none`, `Result: PASS`.
- Warnings: edgar dependency deprecation warnings and Streamlit bare-mode warnings appeared during imports only.

## 2026-07-08 - Browser QA

Command:

```bash
/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8563 --server.headless true --browser.gatherUsageStats false
```

Result:

- `Workspace > Institutional Portfolios` loaded at `http://localhost:8563/institutional-portfolios`.
- Verified source caveat band, manager search, missing-DB empty state, collapsed technical detail, and `Institutional Interest` search entry.
- Streamlit console script shebang pointed to another worktree venv, so Browser QA used `python -m streamlit`.
- Playwright screenshot was generated outside the git worktree output path and was not staged.
