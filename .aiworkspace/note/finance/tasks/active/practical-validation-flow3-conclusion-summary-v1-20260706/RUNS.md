# Runs

Status: Completed
Date: 2026-07-06

## Red

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_fix_queue_react_component_is_ui_only tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow3_uses_conclusion_summary
```

Result: failed as expected because the React component still rendered `Final Review 이동을 막는 이슈`, `현재 문제`, `완료 기준`, `보강 위치`, and the page still titled Flow 3 as `2차 검증 결론 / Fix Queue`.

## Build

```bash
cd app/web/components/practical_validation_fix_queue/frontend
npm ci
npm run build
rm -rf node_modules
```

Result: Vite production build completed. Existing frontend dependency audit still reports 2 findings; no package upgrade was applied in this UI-role change.

## Green

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_fix_queue_react_component_is_ui_only tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow3_uses_conclusion_summary
```

Result: 2 tests passed.

## Verification

```bash
git diff --check
.venv/bin/python -m py_compile app/web/backtest_practical_validation/page.py app/web/backtest_practical_validation/workspace_panel.py
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_fix_queue_react_component_is_ui_only tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow3_uses_conclusion_summary tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_issue_queue_items tests.test_backtest_refactor_boundaries
.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests tests.test_service_contracts.PracticalValidationDiagnosticsServiceContractTests tests.test_service_contracts.PracticalValidationReplayServiceContractTests
```

Result: passed. The unittest runs emitted existing third-party `edgar` deprecation warnings and Streamlit bare-mode `ScriptRunContext` warning.

## Browser QA

```bash
.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8510 --server.headless true --server.runOnSave false --server.fileWatcherType none
```

Result: Practical Validation tab rendered Flow 3 as `검증 결론`, with `Practical Validation 검증 결론`, `카테고리별 검증 요약`, and Flow 4 detail prompt visible in the browser snapshot. Removed Flow 3 copies `Final Review 이동을 막는 이슈` and `최종 선택, 투자 추천...` were not present. QA artifacts were saved locally as generated files:

- `pv-flow3-conclusion-summary-qa.png`
- `pv-flow3-conclusion-summary-snapshot.md`
