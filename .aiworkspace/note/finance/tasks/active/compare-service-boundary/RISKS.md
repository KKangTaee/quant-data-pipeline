# Compare Service Boundary Risks

Status: In progress
Created: 2026-05-19

## Residual Risks

| Risk | Status | Mitigation |
| --- | --- | --- |
| Preset source dictionaries still live in `backtest_common.py` | Reduced | Service receives `ComparePresetCatalog` from UI instead of importing the Streamlit-adjacent module. Later split can move preset constants into a Streamlit-free module. |
| Weighted builder service has no DB-backed app run validation yet | Reduced | Compile/import/in-memory bundle smoke passed. Run manual app weighted builder QA when DB state is available. |
| Saved replay still owns orchestration side effects in the UI file | Open | Next slice should separate saved replay execution/data assembly from session state and render side effects. |
| Real DB-backed compare not executed in validation | Open | Current validation used compile/import/service smoke. Run manual app compare QA when DB state is available. |
