# Overview Futures Macro React UX Notes

- Current Futures Macro tab entrypoint is thin, but `render_futures_macro_tab()` calls `render_futures_macro_fragment(detail_expanded=True)`.
- `_render_futures_macro_panel()` calls `load_overview_futures_macro_snapshot()` without arguments.
- `load_overview_futures_macro_snapshot()` defaults `include_validation=True` and `lookback_days=365 * 5 + 90`.
- Local smoke timing on the current DB:
  - `include_validation=False`: about 0.21s
  - `include_validation=True`: about 7.59s
  - cached follow-up calls: about 0.03s
- The first-entry bottleneck is therefore synchronous historical validation, not the top-level tab selector.
- Phase 1 implementation:
  - `render_futures_macro_tab()` now opens the fragment with `detail_expanded=False`.
  - `_render_futures_macro_panel()` calls `load_overview_futures_macro_snapshot(include_validation=False)` so first tab entry renders current macro state only.
  - `과거 점검 불러오기` runs `build_futures_macro_validation_snapshot(...)` and `build_interpretation_confidence(...)` only on click, then stores the validation / confidence / loaded timestamp in session state.
  - `일봉 갱신` and `다시 읽기` clear the session validation keys along with the snapshot cache boundary.
  - The snapshot `symbols` payload is a pandas DataFrame in this path, so the on-demand validation action must extract unique values from its `Symbol` column instead of using `macro.get("symbols") or []`.
