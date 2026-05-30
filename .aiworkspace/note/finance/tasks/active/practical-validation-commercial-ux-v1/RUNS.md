# Runs

Commands and verification notes will be recorded during implementation.

## 2026-05-30

- `.venv/bin/python -m py_compile app/web/backtest_ui_components.py app/web/backtest_practical_validation.py` PASS
- `git diff --check` PASS
- `.venv/bin/python -m unittest tests.test_service_contracts` PASS, 193 tests
- Browser QA on `http://127.0.0.1:8502/backtest` PASS: Practical Validation renders Control Center, Fix Queue, summary-first Evidence Workspace tabs, Provider Action Center, and browser console error log is empty.
- 2차 visual shell pass: `.venv/bin/python -m py_compile app/web/backtest_practical_validation_components.py app/web/backtest_practical_validation.py app/web/backtest_ui_components.py` PASS
- 2차 visual shell pass: `git diff --check` PASS
- 2차 visual shell pass: `.venv/bin/python -m unittest tests.test_service_contracts` PASS, 193 tests
- 2차 visual shell pass: `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` PASS
- 2차 visual shell pass: `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` PASS
- 2차 visual shell pass Browser QA on `http://127.0.0.1:8502/backtest` PASS: workbench shell, Gate / module section, Evidence Board, Save & Move control render and browser console error log is empty. Screenshot: `practical-validation-product-shell.png`
- 선택 후보 backtest mini report: `.venv/bin/python -m py_compile app/web/backtest_practical_validation.py` PASS
- 선택 후보 backtest mini report: `git diff --check` PASS
- 선택 후보 backtest mini report: `.venv/bin/python -m unittest tests.test_service_contracts` PASS, 193 tests
- 선택 후보 backtest mini report: `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` PASS
- 선택 후보 backtest mini report: `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` PASS
- 선택 후보 backtest mini report Browser QA on `http://127.0.0.1:8502/backtest` PASS: Summary / Equity Curve / Result Table / Components tabs render, Candidate and Benchmark curve lines render, and browser console error log is empty. Screenshot: `practical-validation-source-snapshot.png`
- 선택 후보 backtest mini report final guard rerun: empty curve snapshot fallback added, then `py_compile`, `git diff --check`, boundary / hygiene checks, and `tests.test_service_contracts` PASS.
- 선택 후보 backtest mini report final Browser recheck PASS: Equity Curve still renders Candidate / Benchmark lines after fallback patch. Console includes Streamlit `_stcore/health` / `_stcore/host-config` 404 entries and Vega extent warnings, but the target view rendered correctly. Screenshot refreshed: `practical-validation-source-snapshot.png`

## 2026-05-31

- Final Review 이동 저장 오류 재현: latest Practical Validation source로 `build_practical_validation_result` 후 raw `json.dumps`가 `Object of type Decimal is not JSON serializable`로 실패함. 최초 위치는 `root.input_evidence.data_coverage_context.price_window_rows[0].window_row_count`.
- JSON-safe registry append fix focused test: `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests.test_practical_validation_registry_serializes_db_scalar_payloads` PASS.
- JSON-safe registry append fix smoke: `_json_ready(build_practical_validation_result(latest_source))` 후 `json.dumps` PASS.
- JSON-safe registry append fix compile: `.venv/bin/python -m py_compile app/runtime/portfolio_selection_v2.py app/services/backtest_practical_validation.py` PASS.
- JSON-safe registry append fix full checks: `py_compile`, `git diff --check`, `check_ui_engine_boundary.py`, `check_finance_refinement_hygiene.py`, and `.venv/bin/python -m unittest tests.test_service_contracts` PASS, 194 tests.
- Final Review handoff service smoke: latest source로 `prepare_final_review_handoff_from_validation(..., persist_validation=True)`를 temp registry에 저장 PASS.
- Browser QA: 기존 Streamlit process가 이전 code를 물고 있어 재시작 후 `검증 결과만 저장` 클릭 PASS. 화면에 `저장했습니다` 표시, TypeError / Traceback 없음. 현재 session에서는 Final Review 이동 button이 gate blocker 때문에 disabled라 같은 persistence path인 save-only와 service handoff smoke로 확인함. Screenshot: `practical-validation-save-json-safe.png`
- Final Decimal finite guard tweak: `.venv/bin/python -m py_compile app/runtime/portfolio_selection_v2.py`, focused JSON-safe registry test, and `git diff --check` PASS.
- Final full service contract rerun after guard tweak: `.venv/bin/python -m unittest tests.test_service_contracts` PASS, 194 tests.
