# Sources

Access date: 2026-06-02

Evidence labels:

- `Observed`: official UI/docs directly show the pattern.
- `Documented`: official docs or repository describe the pattern.
- `Claimed`: product page or marketing copy claims the pattern.
- `Inferred`: synthesis from multiple supported facts.
- `Unknown`: evidence is missing or unclear.

## Local Sources

| Source | Evidence | Notes |
| --- | --- | --- |
| `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | Documented | Product is evidence-first and excludes live trading / broker orders / auto rebalance. |
| `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | Documented | Overview market intelligence ownership files and data/app boundaries. |
| `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md` | Documented | Existing Overview refresh, Data Health, browser-session cadence, and run history patterns. |
| `pyproject.toml` | Observed | `yfinance` and `streamlit` are project dependencies; Plotly is not. |
| `app/web/overview_dashboard.py` | Observed | Existing `st.fragment(run_every=...)` auto refresh pattern for Overview market movers. |
| Local command: `.venv/bin/python` yfinance smoke, 2026-06-02 | Observed | `ES=F`, `NQ=F`, `YM=F`, `RTY=F`, `CL=F`, `GC=F`, `SI=F`, `HG=F`, `NG=F`, `ZN=F`, `ZB=F`, `6E=F`, `6J=F`, `6B=F`, `6A=F`, `6C=F`, `MES=F`, `MNQ=F`, `M2K=F`, `MCL=F`, `BTC=F`, `MBT=F`, `ETH=F` returned 1분봉 rows. `DX=F`, `VX=F` returned empty/not found. |

## Web Sources

| Source | Evidence | Notes |
| --- | --- | --- |
| [yfinance API reference](https://ranaroussi.github.io/yfinance/reference/index.html) | Documented | Documents download/history APIs and websocket classes, but yfinance is a wrapper over Yahoo Finance, not an official exchange data feed. |
| [CME Group delayed quotes](https://www.cmegroup.com/market-data/browse-data/delayed-quotes.html) | Documented | Official CME delayed quote browsing surface; useful as reference, not assumed scrape-safe. |
| [CME Market Data APIs](https://www.cmegroup.com/market-data/market-data-api.html) | Documented | Official CME API direction for market data access; production-grade path likely requires account/entitlement work. |
| [CME Group trading hours](https://www.cmegroup.com/trading-hours.html) | Documented | Futures trading hours vary by product and should not be represented as NYSE cash session hours. |
| [KRX Open API guide](https://openapi.krx.co.kr/) | Documented | Official Korean Exchange Open API portal; requires API key and has usage/eligibility limits. |
| [Twelve Data pricing](https://twelvedata.com/pricing) | Documented | Free tier exists, but commodity/futures-like coverage is not a straightforward free replacement for CME futures OHLCV. |
| [Streamlit `st.fragment`](https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment) | Documented | Supports fragment reruns on cadence through `run_every`, fitting the current app pattern. |
| [TradingView Lightweight Charts series types](https://tradingview.github.io/lightweight-charts/docs/series-types) | Documented | Provides candlestick chart pattern for a future frontend upgrade. |

## Source Notes

- External API pricing, limits, and symbol coverage can change. Recheck before implementation.
- Treat `yfinance` as a free pilot source, not a durable production entitlement.
- Treat CME and KRX official sources as future hardening options.
- Scraping public chart sites needs separate terms-of-use review and user approval.
