# Backtest Boundary Refactor V1 Runs

Command log for staged QA.

## V2-V8 final package refactor

- V2 commit: `d58d2c6d backtest V2 runtime 패키지 foundation 정리`
- V3 commit: `0d300369 backtest V3 runtime runner 패키지 분리`
- V4 commit: `507bf72a backtest V4 stores read-model 패키지 정리`
- V5 commit: `c427d87b backtest V5 single strategy UI 패키지 분리`
- V6 commit: `19081622 backtest V6 portfolio mix UI 패키지 분리`
- V7 commit: `39807f35 backtest V7 validation final-review UI 패키지 분리`

Final V8 QA:

- Diff check: `git diff --check`
  - Result: PASS.
- Boundary tests: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries`
  - Result: PASS, 11 tests.
- Service contracts: `.venv/bin/python -m unittest tests.test_service_contracts`
  - Result: PASS, 444 tests.
- GRS focused contracts: `.venv/bin/python -m unittest tests.test_global_relative_strength_strategy`
  - Result: PASS, 4 tests.
- ETF runtime strategy contracts: `.venv/bin/python -m unittest tests.test_etf_runtime_strategy_contracts`
  - Result: PASS, 4 tests.
- Compile: `find app/runtime/backtest app/services app/web -name "*.py" -print | sort | xargs .venv/bin/python -m py_compile`
  - Result: PASS.
- Browser QA: Streamlit `http://localhost:8509/backtest`
  - Result: first entry rendered Backtest Analysis / Single Strategy / Portfolio Mix Builder with no Traceback / ModuleNotFoundError / ImportError. Practical Validation and Final Review stage selectors opened successfully.
  - Screenshot artifact: `backtest-v8-browser-qa.png` (generated, not staged).

## 1차

- RED: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries -v`
  - Expected failure: missing `app.web.backtest_state`, missing `app.web.backtest_formatters`, and `backtest_page.py` still importing from `backtest_common.py`.
- GREEN QA: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries -v`
  - Result: PASS.
- Compile: `.venv/bin/python -m py_compile app/web/backtest_page.py app/web/backtest_state.py app/web/backtest_formatters.py app/web/backtest_common.py`
  - Result: PASS.
- Diff check: `git diff --check`
  - Result: PASS.

## 7차

- Boundary tests: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries -v`
  - Result: PASS, 8 tests.
- Service contracts: `.venv/bin/python -m unittest tests.test_service_contracts -v`
  - Result: PASS, 444 tests.
- Compile: `.venv/bin/python -m py_compile app/web/backtest_page.py app/web/backtest_state.py app/web/backtest_formatters.py app/web/backtest_single_runner.py app/web/backtest_compare.py app/services/backtest_single_payload.py app/services/backtest_portfolio_mix_readiness.py app/services/backtest_validation_status_policy.py app/services/backtest_practical_validation_modules.py app/services/backtest_final_review_policy.py app/services/backtest_selected_route_preflight.py app/runtime/backtest_runner_catalog.py app/services/backtest_execution.py app/services/backtest_compare_catalog.py`
  - Result: PASS.
- Diff check: `git diff --check`
  - Result: PASS.
- Browser QA: Streamlit `http://localhost:8507/backtest`
  - Result: Backtest title, `후보 분석 · Backtest Analysis`, `실전 검증 · Practical Validation`, `최종 검토 · Final Review`, Single Strategy, Portfolio Mix Builder rendered. No Traceback / ModuleNotFoundError / ImportError detected.
  - Screenshot artifact: `backtest-boundary-refactor-v1-browser-qa.png` (generated, not staged).

## 6차

- RED: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests.test_runtime_runner_catalog_identifies_strategy_owners -v`
  - Expected failure: missing `app.runtime.backtest_runner_catalog`.
- GREEN QA: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries -v`
  - Result: PASS.
- Compile: `.venv/bin/python -m py_compile app/runtime/backtest_runner_catalog.py app/services/backtest_execution.py app/services/backtest_compare_catalog.py app/runtime/backtest.py app/runtime/backtest_strict.py`
  - Result: PASS.
- Diff check: `git diff --check`
  - Result: PASS.

## 5차

- RED: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests.test_final_review_selected_route_policy_is_service_owned -v`
  - Expected failure: missing `app.services.backtest_final_review_policy`.
- GREEN QA: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries -v`
  - Result: PASS.
- Compile: `.venv/bin/python -m py_compile app/services/backtest_final_review_policy.py app/services/backtest_selected_route_preflight.py app/services/backtest_evidence_read_model.py app/web/backtest_final_review.py`
  - Result: PASS.
- Diff check: `git diff --check`
  - Result: PASS.

## 4차

- RED: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests.test_practical_validation_status_policy_is_service_owned -v`
  - Expected failure: missing `app.services.backtest_validation_status_policy`.
- GREEN QA: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries -v`
  - Result: PASS.
- Compile: `.venv/bin/python -m py_compile app/services/backtest_validation_status_policy.py app/services/backtest_practical_validation_modules.py app/services/backtest_practical_validation.py app/web/backtest_practical_validation.py`
  - Result: PASS.
- Diff check: `git diff --check`
  - Result: PASS.

## 3차

- RED: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests.test_portfolio_mix_role_flags_are_service_owned -v`
  - Expected failure: missing `app.services.backtest_portfolio_mix_readiness`.
- GREEN QA: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries -v`
  - Result: PASS.
- Compile: `.venv/bin/python -m py_compile app/services/backtest_portfolio_mix_readiness.py app/web/backtest_compare.py app/services/backtest_weighted_portfolio.py app/services/backtest_compare_execution.py`
  - Result: PASS.
- Diff check: `git diff --check`
  - Result: PASS.

## 2차

- RED: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests.test_single_strategy_payload_normalization_is_service_owned -v`
  - Expected failure: missing `app.services.backtest_single_payload`.
- GREEN QA: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries -v`
  - Result: PASS.
- Compile: `.venv/bin/python -m py_compile app/services/backtest_single_payload.py app/web/backtest_single_runner.py app/web/backtest_single_forms.py`
  - Result: PASS.
- Diff check: `git diff --check`
  - Result: PASS.
