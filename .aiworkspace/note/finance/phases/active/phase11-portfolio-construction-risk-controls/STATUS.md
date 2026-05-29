# Phase 11 Portfolio Construction Risk Controls Status

Status: Active
Created: 2026-05-29

## Current State

Phase 11 source map is complete.

Completed:

- 11-0 `phase11-board-open`
- Phase scope, task split, storage boundary, immediate next task 정리
- 11-1 `construction-risk-source-map-v1`
- Current Practical Validation / provider look-through / Robustness Lab / Final Review gate source map and gap audit

Next:

- 11-2 `concentration-overlap-exposure-contract-v1`

## Latest Decision

11-1 결과, data source 자체보다 ownership과 gate visibility가 더 큰 gap이다.
concentration / overlap / exposure는 이미 Practical Validation diagnostics와 provider look-through board에 존재한다.
다음 구현은 새 저장 기능이 아니라 기존 compact evidence를 읽는 read-only Construction Risk Audit contract부터 시작한다.

Immediate next task:

- `concentration-overlap-exposure-contract-v1`

## Storage Boundary Reminder

- 검증 효력을 높이는 data collection은 DB-backed로 검토한다.
- workflow JSONL에는 기존 흐름의 compact evidence boundary만 유지한다.
- user memo, preset, time log, comment storage는 추가하지 않는다.
- broker order, live approval, auto rebalance는 이 phase의 scope가 아니다.
