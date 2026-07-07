# Status

- 2026-05-30: Task opened after user approved the Events UX redesign direction.
- 2026-05-30: Added Events-specific summary strip, source lane, and agenda section renderers to `overview_ui_components.py`.
- 2026-05-30: Reworked Events tab into `Agenda / Calendar / Quality / Raw`, removed the nested Focus tabs, and moved source quality concerns into the Quality view.
- 2026-05-30: Verified compile, service contract tests, diff hygiene, and browser smoke for the redesigned Events tab.
- 2026-05-30: Follow-up polish converted Events Type and Window controls from segmented controls to selectboxes so reduced-width layouts no longer wrap control options awkwardly.
- 2026-05-30: Follow-up polish improved only the Events top summary, source lane, and calendar visuals; Agenda and Quality views intentionally stayed unchanged.
- 2026-05-30: Follow-up polish moved event collection buttons into a compact Refresh popover, promoted summary cards above source status, and changed source status cards into a one-line strip.
- 2026-05-30: Follow-up polish replaced the compact source strip with low-height mini cards so source status values no longer clip at reduced widths.
- 2026-07-07: 1차 continuation analysis completed for Events React workbench. Current flow, read-model contract, UI weaknesses, React payload scope, ownership boundary, QA/commit sequence, and no-signal boundary are captured in `DESIGN.md`. No code implementation was performed in this phase.
- 2026-07-07: 2차 taxonomy/schema/read-model contract completed. `market_event_calendar` now accepts nullable taxonomy fields, `build_market_events_snapshot()` returns `market_events_snapshot_v2` with taxonomy columns and coverage count maps, and data docs/runbook/task docs were aligned. No new external collectors or React scaffold were added in this phase.
- 2026-07-07: 3차 official macro / fixed-income collector expansion completed. BLS JOLTS/ECI, BEA PCE, Census indicators, ISM PMI, and Treasury auction parser/fetch paths were added to the macro calendar collector with official taxonomy metadata. No Events React scaffold was added in this phase.
- 2026-07-07: 4차 Earnings universe expansion completed. Earnings rows now persist `event_family`, `event_subtype`, `universe_scope`, and `source_authority`; S&P 500 / large-cap batch collection is canonicalized for the workbench payload, and portfolio/watchlist/Nasdaq-100 symbol sources have explicit loader boundaries. No market-structure collectors or React scaffold were added in this phase.
