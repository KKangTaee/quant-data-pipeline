# Runs

- 2026-06-02: Read AGENTS, docs index, roadmap, project map, script structure map, Backtest UI flow, Portfolio Selection flow, and Backtest UI boundary reference.
- 2026-06-02: Inspected `app/web/final_selected_portfolio_dashboard.py` render functions with `rg` and focused `sed` reads.
- 2026-06-02: Ran `.venv/bin/python -m py_compile app/web/final_selected_portfolio_dashboard.py`.
- 2026-06-02: Ran `.venv/bin/python -m py_compile app/web/final_selected_portfolio_dashboard.py app/runtime/final_selected_portfolios.py app/web/final_selected_portfolio_dashboard_helpers.py`.
- 2026-06-02: Ran `.venv/bin/python -m unittest tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests`; 35 tests passed.
- 2026-06-02: Ran `git diff --check`; passed.
- 2026-06-02: Browser QA on `http://localhost:8503/selected-portfolio-dashboard` confirmed heading order: Selected Portfolio Dashboard, Active Portfolio Monitoring Scenario, 나의 포트폴리오, 포트폴리오 상세 / 전략 보드, 포트폴리오 시나리오 업데이트, 상세 점검, 전환 비교.
- 2026-06-02: Saved Browser QA screenshot at `selected-dashboard-monitoring-first-ux-v1-qa.png`.
