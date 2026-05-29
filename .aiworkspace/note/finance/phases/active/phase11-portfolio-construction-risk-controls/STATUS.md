# Phase 11 Portfolio Construction Risk Controls Status

Status: Active
Created: 2026-05-29

## Current State

Phase 11 concentration / overlap / exposure contract is complete.

Completed:

- 11-0 `phase11-board-open`
- Phase scope, task split, storage boundary, immediate next task 정리
- 11-1 `construction-risk-source-map-v1`
- Current Practical Validation / provider look-through / Robustness Lab / Final Review gate source map and gap audit
- 11-2 `concentration-overlap-exposure-contract-v1`
- Read-only Construction Risk Audit V1 for component weight concentration, provider look-through coverage, top holding, holdings overlap, and asset bucket exposure

Next:

- 11-3 `correlation-risk-contribution-contract-v1`

## Latest Decision

11-2 implemented `construction_risk_audit_v1` as a read-only contract.
Provider holdings / exposure missing or partial evidence does not become `PASS`.
The audit is visible in Practical Validation and Final Review, and Final Review snapshots preserve it.
Selected-route gate enforcement remains 11-5 scope.

Immediate next task:

- `correlation-risk-contribution-contract-v1`

## Storage Boundary Reminder

- 검증 효력을 높이는 data collection은 DB-backed로 검토한다.
- workflow JSONL에는 기존 흐름의 compact evidence boundary만 유지한다.
- user memo, preset, time log, comment storage는 추가하지 않는다.
- broker order, live approval, auto rebalance는 이 phase의 scope가 아니다.
