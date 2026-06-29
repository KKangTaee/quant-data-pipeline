# Design

## Before

```text
app/web/overview_dashboard.py
  compatibility wrapper + many private helper exports

app/web/overview_ui_components.py
  visual tokens, CSS, Market Context, Market Movers, Events, Data Health, layout renderer bodies

app/services/overview_market_intelligence.py
  compatibility facade over app/services/overview/*
```

## After

```text
app/web/overview_dashboard.py
  render_overview_dashboard only

app/web/overview_ui_components.py
  compatibility facade only

app/web/overview/components/
  common.py
  layout.py
  market_context.py
  market_movers.py
  events.py
  data_health.py

app/services/overview/
  market_context.py
  market_movers.py
  events.py
  sentiment.py
  data_health.py
  why_it_moved.py
  ia.py
```

## Data Health Scope

`build_collection_ops_snapshot` now labels rows with:

- `direct_market_context`: S&P 500 universe / S&P 500 daily snapshot / sentiment / FOMC / earnings / macro calendar.
- `reference_context`: Top1000 / Top2000 / Futures Monitor 1m OHLCV.

Coverage includes direct/reference total and review counts so consumers can avoid treating reference-only targets as blocking default Market Context.
