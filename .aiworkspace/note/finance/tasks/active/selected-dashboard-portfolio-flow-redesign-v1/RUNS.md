# Runs

- 2026-06-01: Read finance docs, flow docs, current dashboard code, helpers, runtime saved-state functions, and focused service contract tests.
- 2026-06-01: `.venv/bin/python -m py_compile app/runtime/final_selected_portfolios.py app/runtime/__init__.py app/web/final_selected_portfolio_dashboard.py app/web/final_selected_portfolio_dashboard_helpers.py` passed.
- 2026-06-01: `.venv/bin/python -m unittest tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests -v` passed 35 tests.
- 2026-06-01: `.venv/bin/python -m unittest tests.test_service_contracts -v` passed 222 tests.
- 2026-06-01: `git diff --check` passed.
- 2026-06-01: Started current worktree Streamlit with `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8504 --server.headless true`; `.venv/bin/streamlit` was not usable because its shebang points at another worktree.
- 2026-06-01: Browser QA on `http://localhost:8504/selected-portfolio-dashboard` verified portfolio card shelf, ready saved portfolio selection, strategy slot settings, portfolio-level monitoring scenario section, scenario setup, lower evidence detail, and no `StreamlitDuplicateElementId` / traceback after the scoped key fix.
- 2026-06-01: Saved Browser QA screenshot as `/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/selected-dashboard-portfolio-flow-redesign-v1-qa.png`; treat as generated artifact, not a commit target.
