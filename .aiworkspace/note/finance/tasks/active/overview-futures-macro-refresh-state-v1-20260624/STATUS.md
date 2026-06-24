# Overview Futures Macro Refresh State V1 Status

## 2026-06-24

- Root-cause check found local DB daily futures rows already reached `2026-06-24 00:00:00` for all 16 core symbols.
- Latest daily collection run was `manual_macro_daily` success with 16/16 symbols and latest candle `2026-06-24 00:00:00`.
- Issue narrowed to UI/cache behavior: `load_overview_futures_macro_snapshot()` used a 15-minute in-process cache and `Futures Macro` primary tab did not expose its own daily refresh/cache reload controls.
- Implemented cache key invalidation using latest stored 1D futures candle marker.
- Added `일봉 매크로 갱신` and `최신 데이터 다시 읽기` controls to the `Futures Macro` tab.
- Verification completed: focused red/green tests, related Overview/Futures Macro contract tests, py_compile, `git diff --check`, and Browser QA.
- Status: Complete.
