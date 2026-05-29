# Phase 12 Selected Monitoring / Recheck Operations Status

Status: Active
Created: 2026-05-29

## Current State

Phase 12 selected monitoring source map is complete.

Completed:

- 12-0 `phase12-board-open`
- Phase scope, task split, storage boundary, immediate next task 정리
- 12-1 `selected-monitoring-source-map-v1`
- Current Selected Dashboard / Final Review / runtime monitoring source ownership and gap audit
- 12-2 `recheck-readiness-freshness-contract-v1`
- Readiness, selected replay contract source, DB latest market date, and symbol freshness are now combined into a read-only operations preflight contract.
- 12-3 `selected-provider-evidence-staleness-contract-v1`
- Provider evidence now applies selected-monitoring policy to diagnostic status, coverage, coverage weight, freshness, required provider areas, and look-through coverage.
- 12-4 `recheck-comparison-review-signal-policy-v1`
- Review Signals now uses Recheck Comparison as the performance threshold policy owner and includes preflight / provider routes in the read-only signal board.

Next:

- 12-5 `allocation-drift-evidence-boundary-v1`

## Latest Decision

12-4 added `selected_review_signal_policy_v1`.
Review Signals no longer owns duplicate CAGR / MDD / benchmark spread threshold logic; those rows are derived from Recheck Comparison.
Recheck Preflight and Provider Evidence routes now feed the same read-only signal board.

Immediate next target:

- `allocation-drift-evidence-boundary-v1`

## Storage Boundary Reminder

- 검증 효력을 높이는 data collection은 DB-backed로 검토한다.
- workflow JSONL에는 기존 final decision / compact evidence boundary만 유지한다.
- `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl`는 explicit user action only로 유지한다.
- user memo, preset, time log, comment storage는 추가하지 않는다.
- broker order, live approval, auto rebalance는 이 phase의 scope가 아니다.
