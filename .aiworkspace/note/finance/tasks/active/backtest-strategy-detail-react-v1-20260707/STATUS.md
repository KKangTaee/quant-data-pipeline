# Backtest Strategy Detail React V1 Status

Status: Active
Started: 2026-07-07

## Why

Quality / Value strict strategy 화면에서 Price Freshness Preflight React component가 blank iframe으로 남아 사용자가 실제 상태를 읽지 못한다. 이어서 전략 선택 후 상세 보기 영역도 전략별 advanced input 차이를 읽기 어렵기 때문에, 입력 state를 건드리지 않는 read-only React detail panel로 먼저 개선한다.

## Roadmap

1. 0차: Price Freshness Preflight blank iframe hotfix.
2. 1차: 전략 상세 read-model 생성.
3. 2차: React Strategy Detail Panel 연결.
4. 3차: 문서 동기화와 최종 검증.

## Current

- 2026-07-07: task opened.
- 2026-07-07: 0차 Price Freshness Preflight blank iframe hotfix implemented and Browser QA passed.
- 2026-07-07: 1차 strategy detail read-model implemented and focused service tests passed.
