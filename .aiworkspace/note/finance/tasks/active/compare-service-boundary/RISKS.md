# Compare Service Boundary Risks

Status: In progress
Created: 2026-05-19

## Residual Risks

| Risk | Status | Mitigation |
| --- | --- | --- |
| Preset source dictionaries still live in `backtest_common.py` | Reduced | Service receives `ComparePresetCatalog` from UI instead of importing the Streamlit-adjacent module. Later split can move preset constants into a Streamlit-free module. |
| Weighted builder still depends on Streamlit-adjacent display helper module | Open | Move only after data-only helper dependency is extracted from `backtest_result_display.py`. |
| Saved replay still bypasses compare execution service | Open | Move after manual compare service pattern is stable. |
| Real DB-backed compare not executed in validation | Open | Current validation used compile/import/service smoke. Run manual app compare QA when DB state is available. |
