# Backtest Real-Money Readiness Efficacy V1 Runs

## 2026-05-30

- `.venv/bin/python -m py_compile app/runtime/backtest.py app/web/backtest_result_display.py app/web/backtest_compare.py app/web/backtest_history.py tests/test_service_contracts.py`
  - Result: passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_execution_preview_ignores_later_stage_probation_monitoring_fields tests.test_service_contracts.BacktestRuntimeContractTests.test_candidate_readiness_scores_source_checks_not_legacy_deployment_status`
  - Result: passed.
  - Notes: edgar package emitted upstream deprecation warnings; test passed.
- `rg -n "Probation|Monitoring|Shortlist|Out-of-Sample|Out-Of-Sample|OOS Review|Out-Sample|표본외|비중 확대" app/runtime/backtest.py app/web/backtest_result_display.py app/web/backtest_compare.py app/web/backtest_history.py`
  - Result: no matches.
- `git diff --check`
  - Result: passed.
- Browser smoke on `http://127.0.0.1:8502/backtest`
  - Restarted the main-dev Streamlit server on port 8502 after code changes.
  - Ran Equal Weight backtest and opened the `Real-Money` tab.
  - Result: Real-Money panel showed Promotion / 실행 원천 / 검증 원천 readiness wording, split-period wording, turnover estimation status, no derived `Execution Preview: blocked` fallback blocker, and no `Probation`, `Monitoring`, `Shortlist`, `OOS Review`, `표본외`, or `비중 확대` user-facing matches.
