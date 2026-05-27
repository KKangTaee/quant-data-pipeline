# UI Engine Boundary Cleanup Risks

Status: Active
Created: 2026-05-27

## Active Risks

| Risk | Why It Matters | Mitigation |
| --- | --- | --- |
| Moving helper modules can break import paths without changing behavior | service/runtime entry points are imported by UI and tests | Mitigated by import smoke, compatibility tests, and boundary lint |
| Practical Validation diagnostics file is large | accidental calculation changes are easy | Mitigated by helper-family split and shape/compatibility tests |
| Provider context helper lived under `app/web` but read loader output | naming could mislead future agents into treating it as UI | Mitigated by moving to `app/services/backtest_practical_validation_provider_context.py` |
| Runtime wrapper is very large | large split can introduce strategy result regressions | Mitigated by function-family map and low-risk result bundle helper extraction |
| Browser QA may be unnecessary for docs/import-only work | browser testing can waste time if no UI surface changed | Closed with task-level browser skip records for helper/import-only changes |

## Out Of Scope Risks

- Provider data completeness remains a Practical Validation V2 data issue, not this cleanup phase's target.
- Backtest numerical correctness remains covered by runtime / strategy tests; this phase should not alter formulas.
- Frontend framework migration is intentionally deferred.
