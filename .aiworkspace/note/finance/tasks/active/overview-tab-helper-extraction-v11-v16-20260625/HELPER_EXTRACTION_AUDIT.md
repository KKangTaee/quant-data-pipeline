# Overview Tab Helper Extraction Audit

## Active Legacy Helper Calls

2026-06-25 기준 active Overview 탭 entrypoint는 `app/web/overview/page.py` 아래에서 선택 탭만 렌더링한다. 남은 의존성은 탭 전체 wrapper가 아니라, 각 탭 entrypoint가 `app/web/overview/legacy_dashboard.py`의 세부 Streamlit helper를 직접 호출하는 형태다.

| Active tab | Current file | Legacy dependency shape | Target owner |
|---|---|---|---|
| Market Context | `app/web/overview/market_context.py` | header/caption, market context refresh reflection, session payload, cockpit loader, refresh bar | `app/web/overview/market_context_helpers.py` (V12 extracted) |
| Events | `app/web/overview/events.py` | event refresh toolbar, events snapshot load, calendar frame/filters, agenda/calendar/quality render helpers, Streamlit/pandas bridge | `app/web/overview/events_helpers.py` (V13 extracted) |
| Futures Macro | `app/web/overview/futures_macro.py` | header/caption and futures macro fragment render bridge | `app/web/overview/futures_macro_helpers.py` |
| Market Movers | `app/web/overview/market_movers.py` | controls, auto-refresh browser checks, snapshot load, refresh bar, snapshot panel | `app/web/overview/market_movers_helpers.py` |
| Sentiment | `app/web/overview/sentiment.py` | refresh actions, snapshot load, job result panel, status cards, charts, tables, Streamlit/pandas bridge | `app/web/overview/sentiment_helpers.py` |

Detailed active call groups:

- Market Context: `_render_overview_market_context_refresh_reflection`, `_market_context_session_payload`, `load_overview_macro_context_cockpit`, `_render_overview_market_context_refresh_bar`, `st`.
- Events: `_render_event_refresh_toolbar`, `load_overview_market_events_snapshot`, `_prepare_event_calendar_frame`, `_has_event_refresh_result`, `_render_market_job_result`, `_event_summary_items`, `_event_source_items`, `load_overview_macro_week_lane`, `_filter_event_rows_for_calendar`, `_event_agenda_sections`, `_render_event_month_grid`, `_build_event_calendar_chart`, `_event_quality_sections`, `_event_quality_rows`, `_event_focus_display_columns`, `pd`, `st`.
- Futures Macro: `_render_futures_macro_fragment`, `st`.
- Market Movers: `_render_market_movers_controls`, `BROWSER_AUTO_REFRESH_JOB_CONFIG`, `BROWSER_AUTO_REFRESH_SECONDS`, `_get_browser_auto_refresh_state`, `_should_run_browser_auto_refresh_check`, `MARKET_COVERAGE_LABELS`, `_run_browser_auto_refresh_check`, `_load_market_movers_snapshot`, `_render_market_movers_refresh_bar`, `_render_market_movers_snapshot_panel`, `st`.
- Sentiment: `_store_overview_job_result`, `run_overview_market_sentiment`, `load_overview_market_sentiment_snapshot`, `_render_market_job_result`, `_render_sentiment_analysis_panel`, `_render_sentiment_analysis_steps`, `render_status_card_grid`, `_sentiment_tone`, `_safe_float`, `_render_sentiment_driver_groups`, `_render_sentiment_component_learning_cards`, `_render_sentiment_next_checks`, `_sentiment_trend_chart`, `_sentiment_component_chart`, `pd`, `st`.

## Target Helper Modules

The target shape stays intentionally small:

- `market_context.py` + `market_context_helpers.py`
- `events.py` + `events_helpers.py`
- `futures_macro.py` + `futures_macro_helpers.py`
- `market_movers.py` + `market_movers_helpers.py`
- `sentiment.py` + `sentiment_helpers.py`

The tab entrypoint should read as the user workflow for that tab. The helper module should own tab-local Streamlit controls, rendering helpers, and lightweight UI transformation glue. Cross-tab read-model building remains in `app/services/overview/*`; bounded refresh jobs remain in `app/jobs/overview_actions.py`.

## Extraction Order

1. V12: Move Market Context tab helper bridge first because it is the default Overview entry surface and has the highest perceived latency impact.
2. V13: Move Events helpers next because Market Context depends on event context and the code currently mixes calendar transforms with UI rendering.
3. V14: Move Futures Macro helpers after the default tab path is settled; it is a separate primary tab but has a compact entrypoint.
4. V15: Move Market Movers helpers after auto-refresh guard behavior is isolated.
5. V16: Move Sentiment helpers last, then run final structure/docs QA because it has the densest chart/table UI glue.

## Guard Rules

- Active tab entry modules should not call removed standalone wrappers in `legacy_dashboard.py`.
- Active tab entry modules should import their tab helper module instead of growing new `legacy_dashboard.py` calls.
- `legacy_dashboard.py` should not regain deleted primary tab wrapper bodies.
- Helper modules may contain Streamlit UI glue, but service/read-model calculation must remain outside `app/web`.
- Do not move `top1000`, `top2000`, or futures collection work back into Market Context refresh scope.
- Generated Browser QA screenshots are local artifacts and are not part of this task commit.

## Completed Extractions

- V12 Market Context: `market_context.py` now imports `market_context_helpers.py` and no longer imports `legacy_dashboard.py` directly. The helper module owns the remaining Market Context Streamlit bridge calls while keeping the user-facing render order unchanged.
- V13 Events: `events.py` now imports `events_helpers.py` and no longer imports `legacy_dashboard.py` or event components directly. The helper module owns refresh result display, event lanes, calendar filtering, and detail tabs.
