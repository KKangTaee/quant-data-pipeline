# Status

Status: Completed
Last Verified: 2026-06-08

## Current

- User requested Backtest 4차 work.
- Scope classified as Backtest 4차 4A ETF current-anchor workbench.
- 3A-3D closeout, roadmap, project map, runtime flow, UI flow, portfolio selection flow, and ETF research bundle were reviewed.
- Task docs opened.
- Streamlit-free ETF current-anchor read model was added.
- Backtest Analysis read-only panel was added after the ETF Evidence Expansion panel.
- Focused regression tests, py_compile, UI-engine boundary check, diff check, and Browser QA passed.

## Handoff

- 4A does not run ETF rerun matrix, collect provider snapshots, write current candidates, or create Practical Validation results.
- Browser QA showed the current local target strategies have no matching local latest run/source rows, so the workbench correctly reports `RERUN_REQUIRED` gaps.
- 4B can be opened as ETF DB-backed rerun matrix / strategy hub update if the user wants to move from readiness display to actual evidence generation.
