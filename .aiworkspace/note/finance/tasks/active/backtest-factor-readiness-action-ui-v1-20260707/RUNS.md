# Runs

## 2026-07-07

- RED: `unittest` focused Factor Readiness tests failed against old contract as expected.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_preset_basis_model_names_current_dynamic_source tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_factor_readiness_model_prioritizes_problem_tickers_and_actions tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_factor_readiness_model_marks_ready_when_price_and_statement_pass tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_factor_readiness_panel_react_component_is_action_oriented tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_factor_readiness_actions_wire_price_and_statement_refresh`
- Build: `npm run build` in `app/web/components/backtest_factor_readiness_panel/frontend`
- Compile: `.venv/bin/python -m py_compile app/web/backtest_common.py app/web/backtest_single_forms/strict_factor.py app/web/backtest_compare/page.py app/web/components/backtest_factor_readiness_panel/component.py`
- Browser QA: `streamlit run app/web/streamlit_app.py --server.port 8510 --server.headless true`, then Playwright navigate to `/backtest`, select Quality, confirm compact Base Universe caption and Factor Readiness cards.

Notes: `npm install` was needed locally because this component folder did not have Vite installed. `node_modules` remains a local artifact and should not be staged.
