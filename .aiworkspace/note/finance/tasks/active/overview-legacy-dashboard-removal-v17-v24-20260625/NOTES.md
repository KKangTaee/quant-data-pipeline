# Overview Legacy Dashboard Removal V17-V24 Notes

## 2026-06-25

- V11-V16 made each primary tab entrypoint thin and moved tab-local bridge code into `*_helpers.py`.
- This task goes further: helper modules should stop importing `legacy_dashboard.py`, and the wrapper should stop re-exporting it.

