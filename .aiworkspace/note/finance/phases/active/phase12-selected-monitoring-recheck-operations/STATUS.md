# Phase 12 Selected Monitoring / Recheck Operations Status

Status: Active
Created: 2026-05-29

## Current State

Phase 12 board open is complete.

Completed:

- 12-0 `phase12-board-open`
- Phase scope, task split, storage boundary, immediate next task 정리

Next:

- 12-1 `selected-monitoring-source-map-v1`

## Latest Decision

Phase 12 focuses on selected monitoring / recheck operations after Final Review selection.
The phase starts with a source map because the product already has Selected Portfolio Dashboard surfaces for recheck readiness, symbol freshness, provider evidence, continuity check, timeline, review signals, recheck comparison, and optional allocation drift.

Immediate next target:

- `selected-monitoring-source-map-v1`

## Storage Boundary Reminder

- 검증 효력을 높이는 data collection은 DB-backed로 검토한다.
- workflow JSONL에는 기존 final decision / compact evidence boundary만 유지한다.
- `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl`는 explicit user action only로 유지한다.
- user memo, preset, time log, comment storage는 추가하지 않는다.
- broker order, live approval, auto rebalance는 이 phase의 scope가 아니다.
