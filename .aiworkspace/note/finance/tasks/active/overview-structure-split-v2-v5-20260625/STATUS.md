# Overview Structure Split V2-V5 Status

## 2026-06-25

- Started V2-V5 sequential structure work after user approved unattended execution with QA after each phase.
- V2 complete: primary tab modules now own tab-level orchestration instead of delegating directly to legacy `_render_*_tab()` functions. Legacy still owns detailed helpers and low-level render functions.
- V3 complete: active page / Market Context / Events now import visual renderers through `app/web/overview/components/` domain component surfaces.
- V4 complete: `overview_dashboard_helpers.py` now imports Overview market read models through `app/services/overview/` domain service surfaces instead of directly importing the monolithic market intelligence service.
