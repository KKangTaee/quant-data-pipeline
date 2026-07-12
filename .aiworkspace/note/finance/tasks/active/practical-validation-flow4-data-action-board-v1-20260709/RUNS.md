# Runs

## Commands

- `npm install && npm run build` in `app/web/components/practical_validation_data_action_board/frontend`
  - Result: pass. Vite build generated `frontend/build`. npm audit reported 1 moderate and 1 high vulnerability in dependency tree; no forced dependency upgrade was applied.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests`
  - Result: pass, 74 tests. edgar deprecation warnings and Streamlit bare-mode warnings only.
- `.venv/bin/python -m py_compile app/services/backtest_practical_validation.py app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py app/web/backtest_practical_validation/components.py app/web/components/practical_validation_data_action_board/component.py`
  - Result: pass.
- `git diff --check`
  - Result: pass.
- Browser QA via local Streamlit `http://localhost:8562/backtest`
  - Result: pass. Flow 4 rendered `데이터 보강 대상`; `Final Review Readiness Preview`, `단계별 검증 소유권`, `수집 대상 근거`, old `근거 부록` were absent, and `상세 근거 / 원자료` remained.
  - Screenshot: `/Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev/practical-validation-flow4-data-action-board-v1-qa.png` generated artifact, not staged.
