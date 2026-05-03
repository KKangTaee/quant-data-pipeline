# Phase 32 Phase33 Handoff Fourth Work Unit

## 목적

네 번째 작업은 Phase 32 결과가 Phase 33 `Paper Portfolio Tracking Ledger`로 넘어갈 수 있는지 요약하는 handoff를 만드는 것이다.

## 쉽게 말하면

"이 후보를 이제 paper tracking 장부에 올릴 준비가 되었나?"를 바로 승인하지 않고,
필요한 추적 조건이 준비되었는지 확인한다.

## 왜 필요한가

- Phase 33은 snapshot 비교가 아니라 시작일, 비중, benchmark, review cadence가 있는 paper ledger를 만들 단계다.
- Phase 32에서 stress gap과 blocker를 정리하지 않으면 Phase 33에서 무엇을 이어받아야 하는지 흐려진다.
- 사용자는 최종 실전 포트폴리오 선정 전에 paper tracking 준비 상태를 분명히 읽어야 한다.

## 구현 내용

- robustness validation result 안에 `phase33_handoff`를 추가했다.
- handoff route는 다음 세 가지로 나눈다.
  - `READY_FOR_PAPER_LEDGER_PREP`
  - `NEEDS_STRESS_INPUT_REVIEW`
  - `BLOCKED_FOR_PAPER_LEDGER`
- Phase 33 준비 기준으로 source id, component weight, tracking benchmark, stress summary contract를 확인한다.
- UI에는 `Phase 33 Handoff` route panel과 `Phase 33 paper ledger 준비 기준` expander를 추가했다.

## 이번 작업에서 하지 않는 것

- Phase 33 paper ledger row를 실제로 저장하지 않는다.
- paper PnL 시계열을 계산하지 않는다.
- 최종 portfolio selection decision을 만들지 않는다.

## 완료 기준

- Validation Pack에서 Phase33 handoff route와 next action이 보인다.
- handoff 요구사항 표에서 paper ledger에 필요한 입력을 확인할 수 있다.
- Phase32 checklist로 사용자 QA를 진행할 준비가 된다.
