# Overview Market Context Load Gate Removal V1 Notes

## Loading Path

`_render_overview_market_context_tab` calls `load_overview_macro_context_cockpit` before rendering the cockpit.
The first load gathers these snapshots:

- `load_overview_market_movers_snapshot(universe_code="SP500", period="daily", top_n=10)`
- `load_overview_group_leadership_snapshot(universe_code="SP500", group_by="sector", period="daily", top_n=20)`
- `load_overview_futures_macro_snapshot()`
- `load_overview_market_sentiment_snapshot()`
- `load_overview_market_events_snapshot(event_type=None, horizon_days=60, limit=100)`
- `load_overview_collection_ops_snapshot()`
- `load_overview_market_context_historical_analog(...)`
- `build_overview_macro_context_cockpit(...)`

## Timing Snapshot

Local cold timing on 2026-06-24:

- `load_overview_macro_context_cockpit`: about 15.8s.
- `futures_macro_snapshot`: about 7.9s.
- `group_leadership_snapshot`: about 4.4s.
- `market_movers_snapshot`: about 2.2s.
- `historical_analog_snapshot`: about 1.3s.
- sentiment / events / collection ops / final assembly were small by comparison.

`load_overview_futures_macro_snapshot` defaults to `include_validation=True` and `lookback_days=365 * 5 + 90`.
Measured separately, futures macro with validation took about 7.8s, while `include_validation=False` took about 0.2s.
