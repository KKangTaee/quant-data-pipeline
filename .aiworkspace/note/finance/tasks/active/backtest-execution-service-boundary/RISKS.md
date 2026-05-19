# Backtest Execution Service Boundary Risks

Status: Complete
Created: 2026-05-19

## Residual Risks

| Risk | Status | Mitigation |
| --- | --- | --- |
| Dispatch copy missed a keyword | Reduced | Strategy key list was compared against the original runner and compile/import checks passed. A real DB-backed backtest smoke is still useful later. |
| Service imports UI helper indirectly | Reduced | Service imports `app.web.runtime.backtest`, not `app.web.backtest_common`; Streamlit reference and import-smoke checks passed. |
| `result.bundle` unexpectedly missing on success | Low | Service always returns bundle on success path; UI still guards on `result.ok`. |
| Compare extraction may be too broad | Open | Start next task with a narrow compare execution audit before moving code. |
