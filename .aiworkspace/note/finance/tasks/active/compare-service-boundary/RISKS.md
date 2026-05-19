# Compare Service Boundary Risks

Status: Implementation complete
Created: 2026-05-19

## Residual Risks

| Risk | Status | Mitigation |
| --- | --- | --- |
| Preset source dictionaries still live in `backtest_common.py` | Reduced | Service receives `ComparePresetCatalog` from UI instead of importing the Streamlit-adjacent module. Later split can move preset constants into a Streamlit-free module. |
| Dynamic PIT universe replay resolver still lives in UI/common helpers | Reduced | Saved replay service accepts `resolve_dynamic_inputs` as a callback to avoid importing `backtest_common.py`. Later split can move the resolver into a Streamlit-free helper. |
| Weighted builder service has no DB-backed app run validation yet | Reduced | Compile/import/in-memory bundle smoke passed. Run manual app weighted builder QA when DB state is available. |
| Saved replay service has no DB-backed app run validation yet | Reduced | Compile/import/fake replay smoke passed. Run manual saved replay QA when DB state is available. |
| Real DB-backed compare not executed in validation | Open | Current validation used compile/import/service smoke. Run manual app compare QA when DB state is available. |
