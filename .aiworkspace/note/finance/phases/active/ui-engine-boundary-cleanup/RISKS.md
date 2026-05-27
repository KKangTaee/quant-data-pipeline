# UI Engine Boundary Cleanup Risks

Status: Active
Created: 2026-05-27

## Active Risks

| Risk | Why It Matters | Mitigation |
| --- | --- | --- |
| Moving helper modules can break import paths without changing behavior | service/runtime entry points are imported by UI and tests | use import smoke, service contract tests, and boundary lint after each sub-step |
| Practical Validation diagnostics file is large | accidental calculation changes are easy | split by helper family, keep return shapes stable, avoid logic changes inside move commits |
| Provider context helper currently lives under `app/web` but reads loader output | naming can mislead future agents into treating it as UI | move to service-oriented module name and update docs |
| Runtime wrapper is very large | large split can introduce strategy result regressions | characterize and map before splitting; prefer low-risk helper extraction |
| Browser QA may be unnecessary for docs/import-only work | browser testing can waste time if no UI surface changed | only open browser when a task changes visible Streamlit flow or displayed data shape |

## Out Of Scope Risks

- Provider data completeness remains a Practical Validation V2 data issue, not this cleanup phase's target.
- Backtest numerical correctness remains covered by runtime / strategy tests; this phase should not alter formulas.
- Frontend framework migration is intentionally deferred.
