# Phase 33 Phase34 Handoff Fourth Work Unit

## 목적

네 번째 작업은 저장된 paper ledger record가 Phase 34 `Final Portfolio Selection Decision Pack`으로 넘어갈 수 있는지 읽히게 만드는 것이다.

## 쉽게 말하면

paper tracking 장부에 적힌 후보나 proposal이
다음 단계에서 최종 선정 검토 대상으로 볼 수 있는지,
아니면 관찰 조건을 더 보강해야 하는지,
또는 blocker 때문에 아직 넘기면 안 되는지를 화면에 표시한다.

## 왜 필요한가

- Phase 33은 최종 선정 자체가 아니라 최종 선정 전의 관찰 기록을 만드는 단계다.
- Phase 34가 시작될 때 어떤 ledger record를 읽어야 하는지 판단 기준이 있어야 한다.
- 사용자가 저장 record를 보면서 "이제 다음 단계로 가도 되는가"를 확인할 수 있어야 한다.

## 구현 내용

- 저장 row에 `phase34_handoff` 값을 계산해 포함했다.
- 저장된 ledger review detail에서 다음 handoff route를 표시한다.
  - `READY_FOR_FINAL_SELECTION_REVIEW`: Phase 34 최종 선정 검토 후보로 읽을 수 있음
  - `NEEDS_PAPER_TRACKING_REVIEW`: tracking 조건이나 기록을 더 확인해야 함
  - `BLOCKED_FOR_FINAL_SELECTION_REVIEW`: 저장 전 blocker나 필수 조건 문제 때문에 다음 단계 차단
- `Open Final Selection` 버튼은 Phase 34에서 연결할 예정인 disabled placeholder로 유지했다.

## 완료 기준

- 저장 ledger detail에서 Phase34 handoff route와 next action이 보인다.
- Phase 33 화면만으로 live approval이나 주문 지시가 수행되지 않는다.
- Phase 34에서 읽어야 할 최소 입력이 row 안에 남는다.

## 이번 작업에서 하지 않는 것

- Phase 34 final decision UI를 만들지 않는다.
- 최종 선정 결과를 registry에 저장하지 않는다.
- broker 연동, 주문, live trading approval을 만들지 않는다.
