# Overview Macro Context Cockpit V1 Notes

## Findings

- `PROJECT_MAP.md` identifies Overview market movers / sector leadership / futures / sentiment / events / data health ownership across `app/services/overview_market_intelligence.py`, futures services, and `app/web/overview_dashboard*.py`.
- `SYSTEM_BOUNDARIES.md` says Overview is context / investigation only and refresh actions must route through `app/jobs/overview_actions.py`.
- Research recommendation selects Cockpit V1 as the first implementation candidate because the current weakness is fragmented summary context, not missing raw panels.
- Current worktree already has unrelated local artifacts: `finance/.DS_Store` and previous Operations QA screenshots. They must remain untouched and unstaged.
- Browser QA found actual `coverage.refresh_state` is a dict with `status` / `label` / `detail` / `tone`, not always a string. Cockpit now normalizes it before display.
- Browser QA also found `--ov-mi-color-text-subtle` was missing from UI CSS tokens, which made cockpit detail text inherit low-contrast dark-theme color. The token is now defined and cockpit shell uses a surface background.

## Design Decisions

- Put cockpit synthesis in a Streamlit-free service function.
- Keep UI rendering in `overview_ui_components.py` and call it from the top of `render_overview_dashboard`.
- Do not change existing deep tabs.
- Keep "Next Deep Tabs" as guidance only; it does not switch tabs, run jobs, write registries, or make validation/monitoring decisions.
