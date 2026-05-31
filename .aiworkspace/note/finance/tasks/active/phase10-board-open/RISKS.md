# Phase 10 Board Open Risks

Status: Complete
Created: 2026-05-29

## Risks

- The board-open task does not implement walk-forward / OOS / regime validation yet.
- Phase 10 implementation could accidentally expand workflow JSONL or memo-like storage if the storage boundary is not checked at each task.
- Regime validation may need additional DB-backed source work after 10-1 source map confirms gaps.

## Mitigation

- Start with `walkforward-oos-source-map-v1` before implementation.
- Keep storage boundary in each Phase 10 task plan.
- Use `finance-backtest-web-workflow`, `finance-strategy-implementation`, and `finance-db-pipeline` only where the task scope actually needs them.
