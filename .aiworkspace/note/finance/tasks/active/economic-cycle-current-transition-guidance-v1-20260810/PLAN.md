# Economic Cycle Current Transition Guidance Plan

## 이걸 하는 이유?

현재 관측 국면은 위축인데 과거 회복 앵커를 기준으로 확장 조건이 primary로 표시되어, 사용자가 향후 방향을 확장으로 오해할 수 있다. 정식 현재 관측에서 다음 인접 국면과 실제 확인 근거를 한 흐름으로 읽게 만든다.

## Roadmap

- 1차: current transition read model과 조건 값 계약
- 2차: 승인된 Before/After UI 구현
- 3차: 실제 DB/Browser QA와 문서 closeout

## Scope

- Overview service와 Economic Cycle React component만 변경한다.
- observed-state state machine, asset cards, freshness는 유지한다.

## Stop Condition

실제 화면이 `현재 위축 → 다음 확인 회복 · 0/3`을 primary로 표시하고 기존 회복 앵커는 secondary로 내려가며, focused regression/build/Browser QA가 통과하면 종료한다.
