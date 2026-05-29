# Phase 12 Board Open Risks

Status: Complete
Created: 2026-05-29

## Risks

- The board-open task does not implement selected monitoring improvements yet.
- Phase 12 implementation could duplicate existing dashboard helper logic if source ownership is not clarified first.
- Review Signals may hide missing recheck, stale DB prices, stale provider evidence, or partial coverage unless severity policy is made explicit.
- Optional Actual Allocation could drift into account integration or order workflow if the boundary is not repeated in each task.
- Legacy `FINAL_PORTFOLIO_SELECTION_DECISIONS` naming and V2 final decision registry naming may confuse source-of-truth handling.

## Mitigation

- Start with `selected-monitoring-source-map-v1` before implementation.
- Keep storage boundary in each Phase 12 task plan.
- Use `finance-backtest-web-workflow` and `finance-db-pipeline` only where the task scope actually needs them.
- Treat missing / stale / failed / partial evidence as `NEEDS_INPUT`, `WATCH`, or `BREACHED`, never as pass.
