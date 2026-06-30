# Backtest Boundary Refactor V1 Runs

Command log for staged QA.

## 1차

- RED: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries -v`
  - Expected failure: missing `app.web.backtest_state`, missing `app.web.backtest_formatters`, and `backtest_page.py` still importing from `backtest_common.py`.
- GREEN QA: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries -v`
  - Result: PASS.
- Compile: `.venv/bin/python -m py_compile app/web/backtest_page.py app/web/backtest_state.py app/web/backtest_formatters.py app/web/backtest_common.py`
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
