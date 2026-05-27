# UI Engine Boundary Cleanup Audit Risks

Status: Complete
Created: 2026-05-27

## Residual Risks

- Task 6 may require broad import updates because docs and service modules name the current `app/web` helper paths.
- Task 7 can accidentally change diagnostics behavior if helper extraction is mixed with calculation cleanup.
- Task 8 is the highest regression risk because `app/runtime/backtest.py` owns multiple strategy-family runtime entry points.
- Browser testing is not useful for Task 0, but future UI-visible helper changes should include manual browser QA.
