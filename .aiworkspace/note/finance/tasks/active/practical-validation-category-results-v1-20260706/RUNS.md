# Runs

Status: Completed
Date: 2026-07-06

## Red

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups
```

Result: failed as expected because `criteria_group_count` was still 3 and included `Final Review Readiness Preview`.

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_fix_queue_react_component_is_ui_only tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board
```

Result: failed as expected because page / React copy still used `Final Review로 넘기기 전 확인 기준`.

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_fix_queue_react_component_is_ui_only
```

Result: failed as expected after adding the build artifact assertion because the tracked Streamlit component build still contained the old `Final Review로 넘기기 전 확인 기준` copy.

```bash
.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests.test_validation_module_gate_reviews_missing_default_robustness_without_blocking tests.test_service_contracts.PracticalValidationServiceContractTests.test_validation_module_gate_skips_construction_risk_for_single_factor_source tests.test_service_contracts.PracticalValidationServiceContractTests.test_validation_module_gate_uses_macro_regime_without_sentiment_context_status
```

Result: failed as expected because stress / construction / sentiment status still behaved like the old policy.

## Green

```bash
.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests
```

Result: 25 tests passed.

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_fix_queue_react_component_is_ui_only tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_issue_queue_items tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board
```

Result: 4 tests passed.

```bash
cd app/web/components/practical_validation_fix_queue/frontend
npm ci
npm run build
```

Result: dependency install and Vite production build completed. `npm ci` reported 2 audit findings in existing frontend dependencies; no package upgrade was applied in this UI copy / gate-policy task.

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_fix_queue_react_component_is_ui_only
```

Result: passed after rebuilding the Streamlit component build artifact with `카테고리별 검증 결과` copy.

```bash
.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries
```

Result: 17 tests passed.

```text
Browser QA
- URL: http://localhost:8509/backtest
- Action: clicked `실전 검증 · Practical Validation`
- Snapshot: pv-category-results-after-click.md, pv-category-results-groups.md
- Screenshot: pv-category-results-flow4-qa.png
```

Result: Practical Validation Flow 4 rendered `카테고리별 검증 결과`; category cards showed `상태`, `통과한 기준`, `남은 문제`, `판정`; `Final Review 이동 요약` rendered as a separate handoff summary below the validation categories.

## Final Verification

```bash
.venv/bin/python -m py_compile app/services/backtest_practical_validation_modules.py app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py
.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_fix_queue_react_component_is_ui_only tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_issue_queue_items tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board tests.test_backtest_refactor_boundaries
git diff --check
```

Result: py_compile passed; 46 unittest cases passed; diff whitespace check passed.
