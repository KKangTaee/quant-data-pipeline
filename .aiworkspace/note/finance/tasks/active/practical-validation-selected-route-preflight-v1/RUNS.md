# Runs

## 2026-06-01

- `.venv/bin/python -m py_compile app/services/backtest_selected_route_preflight.py app/services/backtest_practical_validation_diagnostics.py app/services/backtest_practical_validation_modules.py app/services/backtest_practical_validation_board_registry.py app/web/backtest_final_review_helpers.py`
  - Result: PASS.
- `.venv/bin/python -m pytest tests/test_service_contracts.py -k "..."`
  - Result: FAILED because this venv does not have `pytest` installed.
- `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests.test_final_review_source_options_hide_blocked_practical_validation_results tests.test_service_contracts.PracticalValidationServiceContractTests.test_validation_module_gate_blocks_missing_required_runtime_replay tests.test_service_contracts.PracticalValidationServiceContractTests.test_validation_module_gate_allows_ready_with_review_modules tests.test_service_contracts.PracticalValidationServiceContractTests.test_validation_module_gate_blocks_selected_route_preflight_gaps tests.test_service_contracts.PracticalValidationServiceContractTests.test_service_imports_do_not_load_streamlit tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_practical_validation_selected_route_preflight_blocks_gross_only_review`
  - Result: PASS, 6 tests.
- `git diff --check`
  - Result: PASS.
- Registry spot check:
  - Existing `READY_WITH_REVIEW` row now evaluates as `selected_route_preflight.select_allowed=False`, `policy_outcome=hold_or_re_review`.
  - Existing blocked row remains ineligible.
- Browser QA:
  - URL: `http://localhost:8502/backtest`, Final Review tab.
  - Result: page showed `검토 후보 없음`, `Practical Validation 저장 기록 2개는 Final Review Gate를 통과하지 않아 검토 대상 목록에서 숨겼습니다.`
  - Screenshot: `/tmp/final-review-preflight-empty-20260601.png`.
