# Inflation Policy Yield Path Status

State: active

## Current Position

- 전체 5차 중 1차 데이터 기반·2차 Core PCE/정책/금리 backend 완료
- 현재 단위: 3차 순방향·10년물 목표 역산 workbench 준비
- 사용자 승인: 순방향/역산 개념과 UI 시안 확인 완료
- 1차 actual source gate: 필수 source/series gap 0, `materialization_allowed=true`
- 독립성 gate: 기존 경제 사이클 결과·확률·artifact·snapshot 재사용 없음
- 실제 2026-07-29 replay: 1개월 Core PCE artifact와 통합 snapshot 모두 `LIMITED`
- 동적 10년물 기준: 당시 active 4.58~4.65%, next overhead 4.67%; 4.7 고정 상수 없음
- 연말 Q4/Q4·정책·저항 event probability는 `LIMITED`, reverse·침체는 `NOT_AVAILABLE`

## Next

저장 snapshot을 읽는 workbench에서 순방향과 10년물 목표 역산을 한 흐름으로
연결한다. `LIMITED/NOT_AVAILABLE`을 숨기지 않고 자동 기준과 사용자 저장 기준을
구분한다. 주식 스트레스와 침체는 각각 4차·5차 범위다.
