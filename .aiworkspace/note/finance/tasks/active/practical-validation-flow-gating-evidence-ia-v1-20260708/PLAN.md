# Practical Validation Flow Gating / Evidence IA V1 Plan

Status: Active
Date: 2026-07-08

## 이걸 하는 이유?

Practical Validation 탭에 들어오자마자 Flow 3 / Flow 4가 보이면 사용자는 `전략 재검증 실행`을 누르기 전에도 검증이 끝난 것처럼 읽는다. 또한 Flow 4 하단 evidence tabs와 Provider 부족근거가 prototype 시절 구조를 유지해, 지금 정리한 `검증 결론 -> 기준 상세 -> 보강 액션` 흐름과 겹친다.

## Roadmap

1. Flow 2 재검증 실행 전에는 Flow 1 / Flow 2만 보여준다.
2. 데이터 수집으로 해결 가능한 기준만 수집 action과 연결한다.
3. Backtest Analysis / Practical Validation / Final Review 단계별 검증 소유권을 inventory로 고정한다.
4. Flow 4 하단 evidence tabs와 Provider 부족근거를 근거 부록 / 데이터 보강 action 중심으로 정리한다.

## Boundaries

- 변경 화면: Backtest > Practical Validation.
- 변경 파일 후보: `app/web/backtest_practical_validation/page.py`, `app/services/backtest_practical_validation_workspace.py`, `tests/test_service_contracts.py`, durable docs / task logs.
- 변경하지 않음: validation threshold, strategy runtime, provider collector implementation, Final Review selected-route policy, registry / saved JSONL rewrite, live approval / broker order / auto rebalance.

## Completion

- 각 차수는 개발, QA, commit 순으로 닫는다.
- Browser QA는 가능한 범위에서 Practical Validation 화면으로 확인하고 screenshot은 generated artifact로만 둔다.
