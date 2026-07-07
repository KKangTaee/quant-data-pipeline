# Practical Validation Flow4 Action Steps V3 Status

Status: Completed
Date: 2026-07-07

## Summary

Flow 4 `검증 기준 상세`의 `해결 방법`을 단일 문단에서 번호형 action steps로 변경했다.

## Implemented

- `app/services/backtest_practical_validation_workspace.py`
  - `resolution_guide.action_steps`를 추가했다.
  - non-PASS audit row의 `Next Action`을 먼저 단계화하고, 기준별 기본 보강 절차를 후속 단계로 붙였다.
  - `next_action`은 호환용 첫 단계 요약으로 유지했다.
- `app/web/backtest_practical_validation/page.py`
  - `action_steps`가 있으면 Flow 4 criteria card에서 `<ol class="pv-criteria-steps">`로 렌더링한다.
- `app/web/backtest_practical_validation/components.py`
  - 단계 목록이 카드 안에서 읽히도록 spacing / wrapping CSS를 추가했다.
- `tests/test_service_contracts.py`
  - Flow 4 workspace guide가 `action_steps`를 내려주고, page source가 단계형 UI를 렌더링하는지 확인한다.

## Boundaries

- validation threshold, module severity, selected-route policy는 변경하지 않았다.
- replay 실행 로직, provider ingestion orchestration, registry / saved JSONL rewrite는 변경하지 않았다.
- Final Review, live approval, broker order, auto rebalance 의미는 추가하지 않았다.

## Verification

- `.venv/bin/python -m py_compile app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py app/web/backtest_practical_validation/components.py`
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_issue_queue_items tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board`
- Browser QA: `http://localhost:8512/backtest`에서 Practical Validation Flow 4 Data Quality detail을 열고 `해결 방법`이 번호형 list로 보이는 것을 확인했다. Screenshot artifact: `practical-validation-flow4-action-steps-v3-action-list-qa.png`.
