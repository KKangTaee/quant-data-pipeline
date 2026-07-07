# Backtest Factor Readiness Panel V1 Runs

## Runs

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_factor_readiness_model_separates_base_price_statement_and_actions tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_factor_readiness_model_marks_ready_when_price_and_statement_pass -v`
  - Expected failure confirmed: `build_strict_factor_readiness_panel_model` did not exist.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_factor_readiness_model_separates_base_price_statement_and_actions tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_factor_readiness_model_marks_ready_when_price_and_statement_pass -v`
  - Passed.
- Regression: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_preset_basis_model_names_current_dynamic_source tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_preset_basis_model_marks_public_default_cleanly tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_price_freshness_preflight_model_builds_react_payload tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_factor_readiness_model_separates_base_price_statement_and_actions tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_factor_readiness_model_marks_ready_when_price_and_statement_pass -v`
  - Passed.
- Compile: `.venv/bin/python -m py_compile app/web/backtest_common.py tests/test_service_contracts.py`
  - Passed.
- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_factor_readiness_panel_react_component_is_ui_only -v`
  - Expected failure confirmed: component wrapper did not exist.
- Build: `npm install && npm run build` in `app/web/components/backtest_factor_readiness_panel/frontend`
  - Passed. npm audit reported 1 moderate and 1 high dev dependency vulnerability in the Vite dependency set.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_factor_readiness_panel_react_component_is_ui_only -v`
  - Passed.
- Compile: `.venv/bin/python -m py_compile app/web/components/backtest_factor_readiness_panel/component.py tests/test_service_contracts.py`
  - Passed.
