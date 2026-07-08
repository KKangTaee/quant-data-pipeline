# Practical Validation Flow4 Outcome Taxonomy V1

## 이걸 하는 이유?

Practical Validation Flow 4가 `PASS / REVIEW / NEEDS_INPUT / BLOCKED`를 기술 상태 그대로 노출하면서 사용자가 실제 의미를 구분하기 어렵다. 특히 `REVIEW`가 보강 실패처럼 보이고, 실제 replay가 실행된 뒤에도 Flow 4에서 `NEEDS_INPUT`처럼 읽히는 문제가 있다.

## Goal

- Flow 4에 사용자-facing 결론 layer를 추가한다.
- `READY`는 UI 결론에서 `PASS`와 같은 통과로 읽히게 유지한다.
- `REVIEW`는 제거하지 않고 `Final Review 판단 필요`로 명확히 노출한다.
- `NEEDS_INPUT / NOT_RUN`은 `보강 후 재검증 필요`로 묶는다.
- `BLOCKED`는 현재 상태로 `실전 사용 어려움` 결론으로 분리한다.
- `Current=REVIEW`인 input check를 `NEEDS_INPUT`으로 강등하지 않는다.

## Scope

- `app/services/backtest_practical_validation_modules.py`
- `app/services/backtest_practical_validation_workspace.py`
- `app/web/backtest_practical_validation/page.py`
- `tests/test_service_contracts.py`
- 작업 기록 / closeout 문서

## Stop Condition

- 신규 회귀 테스트가 RED -> GREEN으로 통과한다.
- Flow 4 summary가 통과 / 보강 후 재검증 / Final Review 판단 / 실전 사용 어려움을 구분한다.
- 기존 Practical Validation service contract 테스트와 py_compile, diff check를 통과한다.
- 가능하면 Browser QA screenshot을 남긴다.
