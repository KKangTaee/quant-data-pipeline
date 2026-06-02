# Recommendation

## One-Line Recommendation

Build a DB-backed `Workspace > Overview > Futures Monitor` MVP using `yfinance` 1분봉 futures OHLCV, 60초 default polling, Altair candlestick charts, and visible provider freshness/staleness diagnostics.

## Why This Direction

The user goal is early awareness: identify steep futures moves before Korean or US cash markets open. The existing Overview surface already owns market intelligence, refresh status, and Data Health. A narrow futures tab can reuse those patterns without changing the core Backtest -> Practical Validation -> Final Review -> Selected Dashboard workflow.

The source decision should be conservative. Official real-time futures data is not generally available as a simple free API. `yfinance` is not official exchange-grade data, but it is already installed and the 2026-06-02 local smoke confirmed 1분봉 data for many liquid futures symbols. That makes it a good pilot source if the UI clearly labels provider risk.

## Data To Show First

Use these presets first:

| Group | Symbols | Purpose |
| --- | --- | --- |
| Equity Index | `ES=F`, `NQ=F`, `YM=F`, `RTY=F` | US cash-market pre-open direction. |
| Rates | `ZN=F`, `ZB=F` | Rate shock and risk appetite context. |
| Commodities | `CL=F`, `GC=F`, `SI=F`, `HG=F`, `NG=F` | Energy, metals, safe-haven, inflation context. |
| FX Futures | `6E=F`, `6J=F`, `6B=F`, `6A=F`, `6C=F` | Dollar/currency pressure context. |
| Optional | `MES=F`, `MNQ=F`, `M2K=F`, `MCL=F`, `BTC=F`, `MBT=F`, `ETH=F` | Micro or crypto futures, only if the user wants them. |

Exclude `DX=F` and `VX=F` from the initial default list because the local smoke returned no usable Yahoo data.

## Recommended 1st Build Scope

### Step 1. Add futures data boundary

```text
finance/data/futures_market.py
finance/data/db/schema.py
app/jobs/ingestion_jobs.py
```

Add a `yfinance` collector that fetches selected symbols with `period="1d"` and `interval="1m"`, normalizes OHLCV, and writes to DB with UPSERT.

### Step 2. Add service read model

```text
app/services/futures_market_monitoring.py
```

Build a Streamlit-free read model:

- instrument preset groups
- latest candle and provider status
- candle rows for selected symbol/time window
- 5m / 15m / 60m movement metrics
- range/volume spike diagnostics
- `Calm`, `Moving`, `Sharp`, `Stale`, `Missing` states

### Step 3. Add Overview tab

```text
app/web/overview_dashboard.py
app/web/overview_ui_components.py
```

Render:

- top status strip
- watchlist group selector
- selected candlestick chart
- shock board table
- refresh controls: `manual`, `60s auto`, optional `20s fast` for limited symbols
- latest run diagnostics

### Step 4. Add Data Health target

Extend Overview Data Health with futures:

- latest success
- latest candle age
- symbols requested/returned/failed
- next action

## Cadence Decision

Do not implement 1초 provider polling in the MVP.

Recommended cadence:

| Mode | Provider collection | Use case |
| --- | --- | --- |
| Default | 60s | All preset groups, normal monitoring. |
| Fast | 20s | 1 to 4 selected symbols during pre-open watch. |
| Experimental | 10s | Manual temporary check only. |
| 1s | Countdown/UI-only | Do not fetch provider every second. |

## Recommended Next Phase After 1st Build

| Phase | Output | Why |
| --- | --- | --- |
| Provider hardening | CME official source/paid API decision note | Decide whether exchange-grade data is worth cost/complexity. |
| Korean derivatives source | KRX Open API feasibility and symbol mapping | Support Korea-specific futures only after official source fit is clear. |
| Chart upgrade | TradingView Lightweight Charts or React surface | Needed only if Streamlit/Altair is too limited. |
| Alert policy | Visual/session-only alerts, no orders | Keep product boundary clear. |

## What Not To Do Yet

- Do not scrape public chart sites by default.
- Do not fetch provider data directly during Streamlit render.
- Do not promise exchange-grade real time from free data.
- Do not include broker orders, live approval, auto rebalance, or persistent push alerts.
- Do not treat futures shock states as investment advice or candidate recommendation.

## Decision Rules

Proceed when:

- The user approves `Overview > Futures Monitor` as the first surface.
- The first provider is accepted as `yfinance pilot, not guaranteed realtime`.
- The first cadence is accepted as 60s default with optional bounded fast mode.
- The first watchlist is limited to liquid Yahoo futures symbols that passed smoke.

## Final Recommendation

Start with an Overview tab, not a separate app. Use DB-backed `yfinance` polling to prove the workflow: "what is moving before the cash market opens, how sharp is it, and is the data fresh enough to trust as context?" After that works, decide whether the product needs official CME/paid data or a richer chart frontend.
