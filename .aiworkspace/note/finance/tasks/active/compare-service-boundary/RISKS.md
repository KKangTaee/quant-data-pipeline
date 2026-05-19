# Compare Service Boundary Risks

Status: In progress
Created: 2026-05-19

## Residual Risks

| Risk | Status | Mitigation |
| --- | --- | --- |
| Runner catalog still lives in UI file | Open | Next slice should move `_strategy_compare_defaults` / `_run_compare_strategy` after strict preset dependencies are separated. |
| Weighted builder still depends on Streamlit-adjacent display helper module | Open | Move only after data-only helper dependency is extracted from `backtest_result_display.py`. |
| Saved replay still bypasses compare execution service | Open | Move after manual compare service pattern is stable. |
| Real DB-backed compare not executed in validation | Open | Current validation used compile/import/fake runner smoke. Run manual app compare QA when DB state is available. |
