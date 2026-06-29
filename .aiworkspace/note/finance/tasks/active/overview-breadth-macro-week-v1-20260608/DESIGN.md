# Design

## Read Model

3차는 기존 snapshot을 재사용하는 얇은 read model이다.

- `build_overview_breadth_heatmap_summary(group_snapshot)`: `build_group_leadership_snapshot()` 결과를 받아 participation, concentration, top group, heatmap row를 만든다.
- `build_overview_macro_week_lane(events_snapshot)`: `build_market_events_snapshot()` 결과를 받아 향후 14일 주요 macro / earnings event lane과 cluster 요약을 만든다.

두 함수 모두 DB fetch, provider fetch, write side effect를 갖지 않는다. 호출자가 이미 로드한 snapshot을 넘기고, UI helper는 이 contract를 그대로 감싼다.

## UI Placement

- Sector / Industry 탭: snapshot status와 warning 다음, Trend / Table tab 전에 breadth summary band를 둔다. 기존 `_build_group_leadership_heatmap()`을 실제 화면에 노출해 top group heatmap을 빠르게 보게 한다.
- Events 탭: summary / source / warning 다음, agenda / calendar / quality tab 전에 macro week lane을 둔다.

## Boundary Copy

UI 문구는 "context", "watch", "review" 중심으로 제한한다. 승인, 매수/매도, validation pass/blocker, monitoring signal처럼 보이는 표현은 사용하지 않는다.
