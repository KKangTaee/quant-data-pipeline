# Plan

## Purpose

Market Movers Redesign V2 4차는 섹터 / 시장 확산 맥락을 metric-card 중심 요약에서 시장 breadth map 형태로 바꾼다.

## Scope

- 기존 `sector_breadth` read model만 사용한다.
- 상승 참여율 rail, sector lane, leader strip을 추가한다.
- 기존 상세 sector breadth 표는 expander 안에 유지한다.
- 예측, 추천, sector rotation signal, 새 provider, 새 DB schema는 추가하지 않는다.

## Completion Criteria

- SP500 Daily/Weekly에서 sector market map이 실제로 보인다.
- NASDAQ No Universe 상태에서 섹터 map이 화면을 깨지 않는다.
- 좁은 화면에서 lane과 leader strip이 1열로 접힌다.
- 공통 검증, Browser QA, coherent commit을 완료한다.
