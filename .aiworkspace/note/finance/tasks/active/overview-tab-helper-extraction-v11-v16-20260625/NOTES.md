# Overview Tab Helper Extraction V11-V16 Notes

## 2026-06-25

- The previous V6-V10 task made `app/web/overview/page.py` and tab entry modules the active owners, removed old standalone tab wrappers, and added guard tests against Candidate Ops overview snapshot reintroduction.
- This task continues from that state and focuses on moving tab-local helper bodies out of `legacy_dashboard.py`.
- V11 audit confirmed that the active tabs no longer call old full-tab wrappers; the remaining dependency is narrower tab-local helper/Streamlit glue. This makes the one-helper-per-tab direction reasonable without adding many files.
- V12 keeps the Market Context user flow unchanged: header, refresh reflection, cockpit render, then refresh bar. The entrypoint now expresses that order, while the helper owns the legacy bridge until deeper body deletion is safe.
- V13 keeps the Events user flow unchanged: filter/refresh tools, source/summary/macro week lanes, then agenda/calendar/quality/raw tabs. The entrypoint now reads as that sequence and the helper owns the calendar transform/UI bridge.
