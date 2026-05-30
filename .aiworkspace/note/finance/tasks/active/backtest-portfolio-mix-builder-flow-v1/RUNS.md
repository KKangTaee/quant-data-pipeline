# Runs

## 2026-05-30

- `rg`로 Compare / Portfolio Builder route, label, handoff call site 확인.
- `sed`로 Backtest route / analysis wrapper / compare workspace / weighted mix handoff / docs ownership 확인.
- `.venv/bin/python -m py_compile app/web/backtest_workflow_routes.py app/web/backtest_analysis.py app/web/pages/backtest.py app/web/backtest_compare.py app/web/backtest_candidate_review.py app/web/backtest_candidate_review_helpers.py app/web/backtest_practical_validation.py app/web/backtest_result_display.py app/web/overview_dashboard_helpers.py app/web/reference_guides.py` 통과.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_portfolio_mix_candidate_gate_allows_ready_mix tests.test_service_contracts.BacktestRuntimeContractTests.test_portfolio_mix_candidate_gate_blocks_hold_component tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_handoff_gate_blocks_hold_candidates tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_handoff_gate_allows_ready_candidates` 통과.
- `.venv/bin/python -m unittest tests.test_service_contracts` 통과, 133 tests.
- `git diff --check` 통과.
- `STREAMLIT_BROWSER_GATHER_USAGE_STATS=false .venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8502 --server.headless true`로 8502 smoke 서버 실행. `.venv/bin/streamlit` 직접 실행은 shebang이 stale phase venv를 가리켜 실패했으므로 python module 실행으로 대체.
- Browser smoke: `http://127.0.0.1:8502/backtest`에서 Backtest Analysis mode `Portfolio Mix Builder`, submode `새 Mix 만들기` / `저장된 Mix`, `구성 포트폴리오 실행`, `Component Period & Shared Inputs`, `구성 포트폴리오 실행` 버튼이 보이는 것을 확인.
