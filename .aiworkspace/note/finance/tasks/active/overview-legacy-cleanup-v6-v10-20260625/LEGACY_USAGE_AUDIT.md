# Overview Legacy Usage Audit

Status: V7 Updated

This document records active, retained, and removable legacy candidates for V6 cleanup.

## Active Legacy Calls

These names are still called directly from active `app/web/overview/*` page / tab modules and must be moved before deletion.

| Area | Active legacy calls |
|---|---|
| Page navigation | `_market_session_banner_model` |
| Market Context | `_market_context_session_payload`, `load_overview_macro_context_cockpit`, `_render_overview_market_context_refresh_reflection`, `_render_overview_market_context_refresh_bar` |
| Market Movers | `_render_market_movers_controls`, `_load_market_movers_snapshot`, `_render_market_movers_refresh_bar`, `_render_market_movers_snapshot_panel`, browser auto-refresh helpers / constants |
| Futures Macro | `_render_futures_macro_fragment` |
| Sentiment | `run_overview_market_sentiment`, `load_overview_market_sentiment_snapshot`, `_render_sentiment_analysis_panel`, `_render_sentiment_analysis_steps`, `_render_sentiment_driver_groups`, `_render_sentiment_component_learning_cards`, `_render_sentiment_next_checks`, sentiment charts / tone helpers |
| Events | `_render_event_refresh_toolbar`, `load_overview_market_events_snapshot`, `load_overview_macro_week_lane`, `_prepare_event_calendar_frame`, `_event_*` row helpers, `_build_event_calendar_chart`, `_render_event_month_grid`, `_has_event_refresh_result` |

## Retained Compatibility

These names are no longer active tab bodies, but they are currently retained because `app/web/overview_dashboard.py` re-exports `legacy_dashboard.py` private helpers for existing tests and older imports.

| Name | Reason |
|---|---|
| `_overview_active_tab_label`, `_overview_tab_label_from_slug`, `_overview_tab_seed_label`, `_overview_tab_display_label` | Implementation body moved to `app/web/overview/navigation.py` in V7. Existing imports via `app.web.overview_dashboard` remain compatibility exports through `legacy_dashboard.py`. |
| `OVERVIEW_DEEP_TAB_OPTIONS`, `OVERVIEW_DEEP_TAB_SLUGS`, `OVERVIEW_DEEP_TAB_DISPLAY` | Implementation constants moved to `app/web/overview/navigation.py` in V7. Legacy still imports them for compatibility. |
| `_render_overview_market_context_tab`, `_render_market_movers_tab`, `_render_futures_macro_tab`, `_render_market_sentiment_tab`, `_render_events_tab` | Standalone legacy tab wrappers. Active tab modules no longer delegate to them, but older tests still inspect these bodies. V7/V9 should move tests to active modules and then remove these wrappers. |
| `_render_futures_monitor_tab`, `_render_sector_industry_tab` | Soft-removed standalone tabs. They are not in primary navigation. Remove only after confirming helper-level tests do not depend on the wrapper body. |

## Removable Candidates

These are not called by the active Overview page path and are cleanup candidates once tests are moved to the new surfaces.

| Candidate | Why removable |
|---|---|
| `legacy_dashboard.render_overview_dashboard` | Active wrapper overrides it with `app.web.overview.page.render_overview_dashboard`; keeping an old render body risks future drift. |
| `_render_overview_market_context_tab`, `_render_market_movers_tab`, `_render_futures_macro_tab`, `_render_market_sentiment_tab`, `_render_events_tab` | Active tab modules own orchestration after V2. |
| `_render_futures_monitor_tab` | `Futures Monitor` is soft-removed from primary navigation; relevant futures macro context now lives in `Futures Macro`. |
| `_render_sector_industry_tab` | `Sector / Industry` is soft-removed from primary navigation; sector evidence is read inside Market Context read models. |
| `load_overview_dashboard_snapshot`, `build_overview_top_candidates`, `build_overview_funnel_rows`, `build_overview_next_actions`, `build_overview_activity_rows` | Candidate Ops dashboard snapshot path is no longer rendered in Overview. Candidate Ops should stay in Backtest / Operations workflows, not Overview. |

## Next Extraction Order

1. Move active Market Context / Events tests from legacy bodies to active tab modules.
2. Move a small read-model body out of `overview_dashboard_helpers.py` or `overview_market_intelligence.py` into `app/services/overview/*`.
3. Delete confirmed unused legacy wrappers and Candidate Ops snapshot helpers.
4. Add final guard tests so removed standalone tabs do not re-enter primary dispatch.
