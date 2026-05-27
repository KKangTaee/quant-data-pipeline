# Runtime Wrapper Cleanup Risks

Status: Active
Created: 2026-05-27

| Risk | Status | Mitigation |
| --- | --- | --- |
| Public runtime imports break after helper split | Mitigated | Kept compatibility exports from `app.runtime.backtest` and added identity/import tests |
| Strategy result numbers change during refactor | Mitigated | Avoided strategy algorithm changes; split pure result bundle helper only |
| DB-backed smoke tests are expensive or environment-dependent | Open | Use pure characterization tests first; keep DB runtime unchanged |
| Browser QA may not show helper-only changes | Closed | Helper-only split has no visible Streamlit layout / interaction change |
