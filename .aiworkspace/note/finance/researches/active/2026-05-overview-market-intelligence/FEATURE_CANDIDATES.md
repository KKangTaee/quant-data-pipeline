# Feature Candidates

Scoring: 1 low, 5 high.

| Priority | Candidate | Impact | Effort | Risk | Confidence | Fit | Recommendation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| P0 | DB-backed market movers | 5 | 3 | 3 | 5 | 5 | Build first. |
| P0 | Monthly sector / industry leadership | 5 | 3 | 3 | 5 | 5 | Build with market movers. |
| P1 | FOMC read-only event calendar | 3 | 2 | 2 | 5 | 5 | Add after first DB-backed scan. |
| P1 | Earnings calendar ingestion | 3 | 5 | 4 | 3 | 3 | Decide provider before build. |
| P2 | Heatmap visualization | 3 | 3 | 3 | 3 | 3 | Add after table contracts stabilize. |

## P0. DB-backed market movers

Goal:

- Show daily / weekly / monthly Top N rising stocks from Coverage 1000 or 2000.

Evidence:

- Audit: local DB has enough US active stock profile and daily price coverage.
- Benchmark: market scan products expose leaders/laggards and sector grouping.

Dependencies:

- Effective market date selection from usable daily price rows.
- Coverage 1000/2000 universe resolver.
- Returnable-symbol count and stale-data labels.

Success criteria:

- User can select period, coverage, and Top N.
- UI displays exact start/end dates and coverage counts.
- Missing rows do not crash or produce misleading rankings.

## P0. Monthly sector / industry leadership

Goal:

- Show monthly top sectors and industries so the user can judge which groups are currently strong.

Evidence:

- Audit: asset profile contains sector / industry / market cap fields.
- Local SQL proof produced sector and industry monthly rankings from the existing DB.

Dependencies:

- Minimum symbol count per group.
- Equal-weight and market-cap-weighted group returns.
- Missing sector/industry handling.

Success criteria:

- User can switch sector vs industry and Top N.
- UI shows symbol count, equal-weight return, market-cap-weighted return, and date window.

## P1. FOMC read-only event calendar

Goal:

- Show upcoming FOMC meetings in Overview Events as context for market movement.

Evidence:

- Federal Reserve publishes official meeting calendars with projection markers.

Dependencies:

- Static source file or DB-backed event table.
- Source URL and last verified date.

Success criteria:

- Event rows include date, event type, source, confidence, and notes.
- UI is read-only and does not imply trading actions.

## P1. Earnings calendar ingestion

Goal:

- Show major upcoming earnings events for covered symbols.

Evidence:

- Alpha Vantage, Financial Modeling Prep, Finnhub, and Nasdaq-style calendar surfaces exist.
- Source quality and access terms differ.

Dependencies:

- Provider choice.
- API key/config.
- New collector, persistence, loader, and source-confidence labels.

Success criteria:

- Overview reads earnings rows from local persisted data.
- User can filter to Coverage 1000/2000 or selected symbols.
- UI distinguishes confirmed, estimated, vendor, and unknown timing.

## P2. Heatmap visualization

Goal:

- Add a more visual broad-market scan after tables are correct.

Evidence:

- TradingView heatmaps use size/color to detect market shifts quickly.

Dependencies:

- Stable service payload.
- Layout verification on desktop and mobile.

Success criteria:

- Heatmap adds insight without replacing sortable tables.
- Text and labels remain readable in Streamlit.

## Parking Lot

- Live alerts / trading triggers.
- Automatic candidate promotion from top movers.
- Broker order or rebalance actions.
- UI-side provider scraping.
