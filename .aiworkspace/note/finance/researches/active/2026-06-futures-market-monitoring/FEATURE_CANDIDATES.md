# Feature Candidates

Scoring: 1 low, 5 high.

| Priority | Candidate | Impact | Effort | Risk | Confidence | Fit | Recommendation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| P0 | Futures Monitor MVP in Overview | 5 | 3 | 3 | 4 | 5 | Build first after user approval. |
| P0 | Futures OHLCV DB-backed collector | 5 | 3 | 4 | 4 | 5 | Required foundation. |
| P1 | Futures Data Health and run history | 4 | 2 | 2 | 4 | 5 | Build with MVP, or immediately after. |
| P1 | Shock scoring and watch windows | 4 | 3 | 3 | 3 | 4 | Build after base chart works. |
| P2 | KRX derivatives source research | 3 | 4 | 4 | 2 | 3 | Later, if Korean futures are needed. |
| P2 | Professional chart frontend | 4 | 5 | 3 | 3 | 3 | Later, if Streamlit chart UX is insufficient. |
| Parking | Public-site scraping | 2 | 4 | 5 | 2 | 1 | Avoid unless explicitly approved. |

## P0. Futures Monitor MVP in Overview

Goal:

- Add a `Futures Monitor` tab to Overview.
- Show major futures groups, selected candlestick chart, movement table, provider status, and refresh controls.

Evidence:

- Audit: Overview is already the finance market-intelligence surface.
- Benchmark: Streamlit fragments support timed refresh; yfinance smoke confirms liquid futures 1m rows.

Dependencies:

- Futures instrument preset list.
- DB-backed futures OHLCV collector.
- Read model service for latest candles and movement score.

Success criteria:

- User can pick a futures group and symbol.
- The app shows stored OHLCV candles and latest provider timestamp.
- Default refresh updates every 60s without blocking the whole page.
- Missing/stale data is visible.
- No live order, auto rebalance, or persistent alert action is added.

## P0. Futures OHLCV DB-Backed Collector

Goal:

- Add a collector using `yfinance` for 1m futures bars.
- Store compact OHLCV rows and provider run diagnostics.

Suggested files:

```text
finance/data/futures_market.py
finance/data/db/schema.py
app/jobs/ingestion_jobs.py
app/services/futures_market_monitoring.py
app/web/overview_dashboard.py
```

Suggested tables:

```text
finance_meta.futures_instrument
finance_price.futures_ohlcv
finance_meta.futures_market_monitor_run
```

Success criteria:

- Collector can refresh only selected symbols.
- UPSERT avoids duplicate candles.
- Run result reports requested, returned, failed, latest candle, duration, provider message.
- UI reads stored rows, not direct provider calls.

## P1. Futures Data Health And Run History

Goal:

- Extend Overview Data Health with futures monitoring targets.
- Append refresh results to existing local run history conventions.

Success criteria:

- Stale/missing status is visible before the chart.
- Failed symbols are actionable.
- Generated run history stays uncommitted.

## P1. Shock Scoring And Watch Windows

Goal:

- Compute simple, explainable movement states.

Suggested scoring:

| Signal | Calculation |
| --- | --- |
| 15m move | `(latest close / close 15m ago - 1) * 100` |
| 60m move | `(latest close / close 60m ago - 1) * 100` |
| Range spike | current 15m high-low range divided by rolling median range |
| Volume spike | latest volume divided by rolling median volume when volume exists |
| State | thresholded `Calm`, `Moving`, `Sharp`, `Stale`, `Missing` |

Watch windows:

- Korea pre-open: KST morning focus before 09:00.
- US pre-open: NYSE open minus configurable 2 hours, DST-aware through existing market-session helper.
- Overnight: provider latest outside the two pre-open windows.

## Parking Lot

- Public-site scraping from Investing.com, Barchart, TradingView, or CME delayed quote pages.
- Live websocket tick aggregation.
- Broker or order integration.
- Persistent push notifications.
- Treating futures moves as candidate selection or investment recommendation.
