# Phase 11 Board Open Risks

Status: Complete
Created: 2026-05-29

## Risks

- The board-open task does not implement construction risk controls yet.
- Phase 11 implementation could duplicate existing Practical Diagnostics if source ownership is not clarified first.
- Holdings / exposure coverage may be partial and should not become automatic PASS evidence.
- Component return matrix coverage may differ by source type.

## Mitigation

- Start with `construction-risk-source-map-v1` before implementation.
- Keep storage boundary in each Phase 11 task plan.
- Use `finance-backtest-web-workflow`, `finance-db-pipeline`, and `finance-strategy-implementation` only where the task scope actually needs them.
