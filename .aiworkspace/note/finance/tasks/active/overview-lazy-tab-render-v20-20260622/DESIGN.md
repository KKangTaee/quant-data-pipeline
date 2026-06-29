# Design

## Files

- `app/web/overview_dashboard.py`
  - Add a small top-level Overview tab option model.
  - Add a selector helper that uses `st.segmented_control` when available and falls back to horizontal `st.radio`.
  - Add `_render_selected_overview_tab(...)` so tests can prove one renderer is called.
  - Move `load_overview_dashboard_snapshot()` from unconditional top-level render into the `Candidate Ops` branch.

- `tests/test_service_contracts.py`
  - Replace the old top-level `st.tabs` source test with lazy selector / dispatch tests.

## Boundary

- This changes when existing render functions execute, not what each tab computes.
- No provider fetch, schema, DB, loader, registry, saved setup, validation, monitoring, or trade semantics are added.
