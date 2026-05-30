# Practical Validation Module Gate V1 Runs

Status: Active
Created: 2026-05-30

## Commands

- `.venv/bin/python -m py_compile app/services/backtest_practical_validation_modules.py app/services/backtest_practical_validation_diagnostics.py app/web/backtest_practical_validation.py app/services/backtest_practical_validation_source.py`
  - Result: pass.
- `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests.test_validation_source_traits_classify_single_etf_tactical_candidate tests.test_service_contracts.PracticalValidationServiceContractTests.test_validation_module_gate_blocks_missing_required_runtime_replay tests.test_service_contracts.PracticalValidationServiceContractTests.test_validation_module_gate_allows_ready_with_review_modules tests.test_service_contracts.PracticalValidationServiceContractTests.test_service_imports_do_not_load_streamlit`
  - Result: 4 tests pass.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Result: 192 tests pass. Non-fatal edgar deprecation warnings and one Streamlit MemoryCache warning observed.
- `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8507 --server.headless true --browser.gatherUsageStats false`
  - Result: launched local UI for Browser QA.
- Browser QA at `http://localhost:8507/backtest`
  - Result: Practical Validation rendered `Final Review Gate`, module board, blocking module table, and disabled save-and-move state. Console errors: 0. Console warnings: 6 Vega infinite extent warnings from empty chart fields.
