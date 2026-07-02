# Backtest Handoff Readiness V2-V6 Runs

## 2026-07-02 V2

- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_candidate_readiness_scores_source_checks_not_legacy_deployment_status tests.test_service_contracts.BacktestRuntimeContractTests.test_handoff_readiness_policy_lives_in_streamlit_free_service`
  - RED result: failed because `app.services.backtest_handoff_readiness` did not exist.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_candidate_readiness_scores_source_checks_not_legacy_deployment_status tests.test_service_contracts.BacktestRuntimeContractTests.test_handoff_readiness_policy_lives_in_streamlit_free_service tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_handoff_gate_blocks_hold_candidates tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_handoff_gate_allows_ready_candidates`
  - GREEN result: passed after service extraction. Existing edgar deprecation warnings observed, unrelated.
- `.venv/bin/python -m py_compile app/services/backtest_handoff_readiness.py app/web/backtest_result_display.py app/web/backtest_compare/page.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Result: passed, 451 tests. Existing edgar deprecation warnings and Streamlit no-runtime cache warnings observed, unrelated.
- `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries`
  - Result: passed, 11 tests. Existing edgar deprecation warnings observed, unrelated.
- `git diff --check`
  - Result: passed after V2 docs update.

## 2026-07-02 V3

- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_handoff_gate_summary_groups_blockers_for_user_display tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_handoff_gate_blocks_hold_candidates tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_handoff_gate_allows_ready_candidates tests.test_service_contracts.BacktestRuntimeContractTests.test_candidate_readiness_scores_source_checks_not_legacy_deployment_status`
  - RED result: initial expectation treated `validation_status=caution` as review, but the existing policy correctly treats it as a blocker.
- Same focused command after aligning the test with rolling/split review signals and grouped handoff action text.
  - Result: passed, 4 tests. Existing edgar deprecation warnings observed, unrelated.
- `.venv/bin/python -m py_compile app/services/backtest_handoff_readiness.py app/web/backtest_result_display.py`
  - Result: passed.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - RED result: one structure assertion expected a single-line handoff readiness import.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Result: passed, 452 tests after updating the service contract assertion for the grouped import.
- `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries`
  - Result: passed, 11 tests. Existing edgar deprecation warnings observed, unrelated.
- `git diff --check`
  - Result: passed.

## 2026-07-02 V6

- `lsof -nP -iTCP:8501 -sTCP:LISTEN`
  - Result: an existing Streamlit server was listening on 8501, but Browser QA showed it was serving older UI state.
- `.venv/bin/streamlit run app/web/streamlit_app.py --server.port 8502 --server.headless true`
  - Result: current worktree app started on `http://localhost:8502`.
- Browser QA at `http://localhost:8502/backtest`
  - Result: Backtest entry showed Korean-first workflow tabs and no old Backtest guide / capability / reference panels.
- Browser QA after running Equal Weight / Dividend ETFs
  - Result: result header, `데이터 기준 요약`, `2차 실전성 검증 Handoff`, grouped Promotion / execution / validation chips, `검증 신호 · Policy Signals`, and `기술 상세 · Technical Policy Meta` rendered. Old `Policy Signal Meta` and `Latest Backtest Run` labels were not present.
  - Screenshot: `backtest-handoff-readiness-v6-browser-qa.png` generated locally and intentionally not staged.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Result: passed, 454 tests. Existing edgar deprecation warnings and Streamlit no-runtime cache warnings observed, unrelated.
- `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries`
  - Result: passed, 11 tests. Existing edgar deprecation warnings observed, unrelated.
- `.venv/bin/python -m py_compile app/services/backtest_handoff_readiness.py app/web/backtest_result_display.py app/web/backtest_candidate_review_helpers.py app/services/backtest_practical_validation_source.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.

## 2026-07-02 V5

- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_candidate_review_draft_captures_handoff_readiness_snapshot tests.test_service_contracts.PracticalValidationServiceContractTests.test_selection_source_preserves_cost_and_turnover_snapshots_without_new_registry`
  - RED result: draft/source handoff readiness snapshot fields did not exist yet.
- Same focused command after adding `handoff_readiness_snapshot` to candidate drafts, Practical Validation source, and component replay contract.
  - Result: passed, 2 tests. Existing edgar deprecation warnings observed, unrelated.
- `.venv/bin/python -m py_compile app/web/backtest_candidate_review_helpers.py app/services/backtest_practical_validation_source.py`
  - Result: passed.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Result: passed, 454 tests. Existing edgar deprecation warnings and Streamlit no-runtime cache warnings observed, unrelated.
- `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries`
  - Result: passed, 11 tests. Existing edgar deprecation warnings observed, unrelated.
- `git diff --check`
  - Result: passed.

## 2026-07-02 V4

- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_policy_signal_tab_prioritizes_grouped_signal_summary tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_handoff_uses_single_integrated_action_surface tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_latest_run_view_prioritizes_result_over_pre_result_guides`
  - Result: passed, 3 tests.
- `.venv/bin/python -m py_compile app/web/backtest_result_display.py`
  - Result: passed.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Result: passed, 453 tests. Existing edgar deprecation warnings and Streamlit no-runtime cache warnings observed, unrelated.
- `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries`
  - Result: passed, 11 tests. Existing edgar deprecation warnings observed, unrelated.
- `git diff --check`
  - Result: passed.
