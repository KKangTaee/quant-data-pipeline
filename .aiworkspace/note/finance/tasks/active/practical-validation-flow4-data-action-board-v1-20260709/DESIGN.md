# Design

## Boundary

`data_action_board`는 Practical Validation workspace read model의 표시용 계약이다. 기존 `build_provider_gap_collection_plan()`과 audit evidence rows를 읽어 사용자에게 지금 보강 가능한 항목을 분류하지만, 수집을 실행하거나 provider / DB를 직접 조회하지 않는다.

React component는 이 model을 props로 받아 category, ticker chips, reason, next action, availability를 표시한다. 실행 버튼은 1차 구현에서 만들지 않고, 기존 Python Provider / Data 보강 액션 버튼이 수집 실행 경계를 유지한다.

## Board Categories

- `immediate_collect`: 기존 provider collection plan / evidence row로 지금 수집 가능한 provider snapshot, holdings, exposure, macro gap.
- `source_map_discovery`: source map 자동 탐색이 먼저 필요한 holdings / exposure 항목.
- `connector_needed`: 자동 탐색 후에도 수동 connector mapping이 필요한 항목.
- `no_action`: 현재 수집으로 해결할 수 없는 항목. Final Review / Monitoring 전용 판단 항목은 PV 메인 보드에서 반복하지 않는다.

## UI Order

Flow 4는 `카테고리별 검증 결과`, `데이터 보강 대상 / 액션`, `상세 근거 / 원자료` 순서로 렌더링한다. Stage ownership inventory는 read model 내부나 task 문서의 분석 근거로만 유지하고 visible expander는 제거한다.
