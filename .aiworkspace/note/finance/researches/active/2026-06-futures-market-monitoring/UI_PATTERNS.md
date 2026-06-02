# UI And Workflow Patterns

## Product Goal

Give the user a compact read-only surface for checking whether major futures markets are moving sharply before Korean or US cash-market open.

## Recommended Surface

Add a new `Workspace > Overview > Futures Monitor` tab first.

If the feature grows into watchlists, alerts, multi-pane charting, and source diagnostics, promote it later to a dedicated `Workspace > Futures` page.

## Pattern 1. Watchlist First

Start with preset groups:

| Group | Symbols | Why |
| --- | --- | --- |
| Equity Index | `ES=F`, `NQ=F`, `YM=F`, `RTY=F`, optional micro `MES=F`, `MNQ=F` | Pre-US open direction and risk appetite. |
| Rates | `ZN=F`, `ZB=F` | Yield/rate shock proxy before equities open. |
| Commodities | `CL=F`, `GC=F`, `SI=F`, `HG=F`, `NG=F` | Inflation, energy, metals, safe-haven context. |
| FX Futures | `6E=F`, `6J=F`, `6B=F`, `6A=F`, `6C=F` | Dollar/risk/currency pressure proxy. |
| Optional Crypto Futures | `BTC=F`, `MBT=F`, `ETH=F` | 24h risk sentiment, but show as optional/noisy. |

Do not include `DX=F` or `VX=F` in the first preset because local smoke returned no data.

## Pattern 2. Top Strip Before Chart

The top of the tab should show:

- provider status: latest successful run, failed symbols, cadence
- global watch window: `Korea pre-open`, `US pre-open`, `US cash open`, `overnight`
- most extreme move: symbol, 15m %, 60m %, range spike
- stale/missing warning count

## Pattern 3. Candlestick Plus Movement Diagnostics

Each selected symbol should show:

- OHLCV candlestick chart for `1m`, `5m`, `15m`, and `1h` views, derived from stored 1m rows when possible
- latest price, latest candle time UTC/KST, provider delay label
- 5m / 15m / 60m percentage move
- candle body ratio and high-low range
- volume or dollar-volume spike when volume exists
- "not a trade signal" boundary label

## Pattern 4. Shock Board

Create a compact table beside or below the chart:

| Column | Meaning |
| --- | --- |
| Symbol | Yahoo futures ticker and display name. |
| Group | Equity index, rates, commodities, FX, crypto. |
| Latest | Last stored close. |
| 15m % | Fast directional move. |
| 60m % | Pre-open context move. |
| Range Spike | Current 15m range versus recent rolling range. |
| Volume Spike | Current volume versus recent rolling volume when available. |
| State | `Calm`, `Moving`, `Sharp`, `Stale`, `Missing`. |

## Pattern 5. Cadence Controls

Recommended default:

- `60s` auto refresh for all preset symbols
- `20s` fast mode for 1 to 4 selected symbols
- `10s` experimental mode only with a warning
- no `1s` provider polling in MVP

The UI can still update a countdown every second. Provider collection should not run every second.

## Pattern 6. Data Health Integration

Add a Futures row to Overview Data Health:

- latest successful futures OHLCV run
- symbols requested / returned / failed
- latest candle age
- provider failure count
- recommended next action

## Pattern Conflicts With Current Boundaries

| Pattern | Conflict | Handling |
| --- | --- | --- |
| Real-time trading chart | Current app is Streamlit + DB-backed read model | Build polling MVP first; consider frontend chart migration later. |
| Provider fetch on every render | Architecture says UI should not directly fetch external providers | Use ingestion job wrapper and stored DB rows. |
| Alert/notification automation | Product boundary avoids live trading/auto actions | Keep alert state visual/session-only in MVP. |
| Scraping public chart sites | Terms/stability risk | Treat as last-resort, user-approved source experiment only. |
