# Risks

## Product Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| User reads futures monitor as a trade signal | High | Label as market context; no candidate promotion, order, or auto rebalance. |
| Free provider data is mistaken for exchange-grade real time | High | Show provider, latest candle time, delay/staleness, failed symbols, and source disclaimer. |
| Feature expands into a trading terminal before the data boundary is stable | Medium | Start as Overview tab; defer professional charting and alerts. |
| Korea and US pre-open windows are conflated | Medium | Show watch windows separately and compute US open with timezone/DST awareness. |

## Technical Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| `yfinance` throttling or symbol failure | High | Bounded symbol list, 60s default cadence, run diagnostics, stale state. |
| 1m rows have gaps or delayed timestamps | High | Persist candle timestamp, compute latest age, display missing/stale instead of smoothing over it. |
| Per-second refresh overloads provider and Streamlit | High | Do not provider-fetch every second; use 60s default, 20s bounded fast mode. |
| Futures session hours differ by product | Medium | Avoid hard session claims in MVP; link to product/session source and show provider latest. |
| DB table growth | Medium | Store 1m bars with retention policy; consider rolling retention for high-frequency rows. |
| Chart performance | Medium | Limit displayed candles and selected symbols; defer frontend chart upgrade if needed. |

## Research Gaps

| Gap | Why it matters | Follow-up |
| --- | --- | --- |
| Exact CME API pricing/entitlement fit | Determines whether production source should move off yfinance. | Recheck CME account/API route if MVP proves useful. |
| KRX derivatives intraday API fit | Needed if Korean futures become first-class, not just global futures context. | Run a separate KRX source feasibility note. |
| Symbol canonicalization | Yahoo tickers are provider-specific and may differ from CME symbols. | Add instrument mapping table with display name, provider symbol, exchange, group. |
| Data license/terms | Determines whether any scraped source can be used. | Avoid scraping until reviewed and explicitly approved. |
| Alert policy | Visual alerts may become persistent notifications. | Define read-only/session-only alert boundary before implementing notifications. |
