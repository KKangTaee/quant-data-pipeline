# Phase 5. Ingestion Workflow Cleanup Plan

## 이걸 하는 이유?

Phase 4까지 backtest 기본 진입은 statement annual path로 옮겼지만, Ingestion UI에서는 broad yfinance fundamentals refresh가 여전히 재무제표 갱신의 자연스러운 시작점처럼 보였다.

이번 phase는 사용자가 새 재무제표 source를 갱신할 때 EDGAR annual refresh를 먼저 실행하고, broad yfinance path는 legacy / advanced compatibility로 이해하게 만드는 것이 목적이다.

## Scope

- `Workspace > Ingestion` operational refresh card order and labels.
- Statement refresh result interpretation summary.
- EDGAR refresh operating runbook.
- Focused service contract tests.

## Done Conditions

- EDGAR annual statement refresh appears before legacy broad yfinance refresh.
- Broad yfinance fundamentals / factors is visibly legacy compatibility and not canonical.
- Statement refresh result tells the user coverage, freshness, failed symbols, and next action.
- Verification and Browser QA are recorded before commit.

## Out Of Scope

- Provider additions.
- Statement table drops or destructive cleanup.
- Registry / saved JSONL rewrites.
- New run dashboard as a substitute for workflow improvement.
