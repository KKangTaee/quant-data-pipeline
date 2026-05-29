# Phase 11 Portfolio Construction Risk Controls Status

Status: Active
Created: 2026-05-29

## Current State

Phase 11 board is open.

Completed:

- 11-0 `phase11-board-open`
- Phase scope, task split, storage boundary, immediate next task 정리

Next:

- 11-1 `construction-risk-source-map-v1`

## Latest Decision

Phase 11은 신규 저장 기능을 먼저 만들지 않는다.
Phase 10 closeout 결과, next hardening target은 portfolio construction risk controls다.
다음 구현은 concentration / overlap / correlation / risk contribution / role / weight discipline source map이다.

## Storage Boundary Reminder

- 검증 효력을 높이는 data collection은 DB-backed로 검토한다.
- workflow JSONL에는 기존 흐름의 compact evidence boundary만 유지한다.
- user memo, preset, time log, comment storage는 추가하지 않는다.
- broker order, live approval, auto rebalance는 이 phase의 scope가 아니다.
