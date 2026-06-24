# Overview Futures Macro Tab Split V1 Design

## Current Structure

- `app/web/streamlit_app.py` makes `Overview` the default Streamlit page.
- `app/web/overview_dashboard.py` owns the internal Overview primary tab selector and selected-tab lazy renderer.
- `app/web/overview_dashboard_helpers.py::load_overview_macro_context_cockpit` previously loaded the Market Context cockpit, futures macro, and historical analog in the default path.
- `app/services/overview_market_intelligence.py::build_overview_macro_context_cockpit` assumes movement, breadth, futures, sentiment, events, and data cards.
- `app/web/overview_dashboard.py` already contains `_render_futures_macro_tab`, but the primary tab list does not expose it.

## Target Flow

```text
Overview
  -> 시장 맥락: fast brief from movers / breadth / events / source state
  -> 변동 종목: market movers
  -> 선물 매크로: futures macro current diagnosis + historical validation
  -> 심리: sentiment
  -> 일정: events
```

## Service Boundary

`build_overview_macro_context_cockpit` should remain usable with futures macro when explicitly requested, but Market Context first load should call it with `include_futures_macro=False` and `include_historical_analog=False` at the helper boundary. When futures is excluded, the service builds five cards instead of six and avoids macro-specific brief/cue rows. Source confidence and refresh plan receive an empty futures snapshot so existing boundary logic remains defensive.

## DB Optimization

`_query_latest_raw_date` should use latest-date ordering rather than `MAX(date)` with `timeframe` filter. Local EXPLAIN showed the existing query scanning a large covering index, while `ORDER BY date DESC LIMIT 1 FORCE INDEX(ix_date)` returns immediately.

## Testing

Use existing `tests/test_service_contracts.py` Overview contract tests. Add tests before implementation for:

- `Futures Macro` appears between `Market Movers` and `Sentiment`.
- slug/display contract maps `futures-macro` to `Futures Macro`.
- selected renderer dispatch includes `_render_futures_macro_tab`.
- Market Context helper source does not call `load_overview_futures_macro_snapshot`.
- Market Context helper source does not call `load_overview_market_context_historical_analog`.
- Cockpit can be built without futures macro and omits macro rail/brief/cue.
- `_query_latest_raw_date` uses an ordered latest row query.
