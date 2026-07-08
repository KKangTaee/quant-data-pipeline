# Backtest Handoff Readiness V2-V6 Plan

## 이걸 하는 이유?

V1에서 `2차 실전성 검증 Handoff` UI 중복은 정리했지만, handoff 판정은 아직 UI 파일에 있고 `Policy Signal Meta`와 source handoff 기록이 같은 의미를 반복한다.
최종 목표는 사용자가 다음 단계로 갈 수 있는지 한 곳에서 이해하고, 코드상으로는 UI / service / handoff source 책임을 나누는 것이다.

## Staged Scope

- V2: `build_next_step_readiness_evaluation`을 Streamlit-free service로 분리한다.
- V3: handoff panel의 blocker / review 표시를 service의 gate summary에 맞춰 중복을 줄인다.
- V4: `Policy Signal Meta`를 사용자용 요약과 technical detail로 분리한다.
- V5: Practical Validation으로 넘기는 source에 handoff readiness snapshot을 함께 남긴다.
- V6: 전체 회귀 QA, Browser QA, docs closeout을 수행한다.

## Non-Goals

- strategy runtime 계산식, validation threshold, registry row format, DB schema는 바꾸지 않는다.
- Practical Validation / Final Review의 live approval, 주문, broker 연동, 자동 리밸런싱 의미를 추가하지 않는다.
