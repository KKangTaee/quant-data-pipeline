# Benchmarks

Evidence labels:

- `Observed`: official UI/docs directly show the pattern.
- `Documented`: official docs or repository describe the pattern.
- `Claimed`: product page or marketing copy claims the pattern.
- `Inferred`: synthesis from multiple supported facts.
- `Unknown`: evidence is missing or unclear.

## Benchmark Matrix

| Source / Product | Category | Evidence | Relevant pattern | Fit for MVP |
| --- | --- | --- | --- | --- |
| Yahoo Finance via `yfinance` | Free unofficial provider wrapper | Documented / Observed | Intraday OHLCV by symbol with intervals including `1m`; local smoke confirmed multiple futures symbols. | Best 1st pilot source, but must label as unofficial/delayed/coverage-risk. |
| CME Group delayed quotes | Official exchange web quote pages | Documented | Exchange-native delayed quote reference; delayed quotes across asset classes. | Good reference/source link. Not recommended as default scraper without terms review. |
| CME Market Data API | Official exchange API | Documented | Real-time/delayed market data API through CME self-service portal and websocket-style access. | Best quality future option, but not a free simple API path. |
| KRX Open API | Official Korean exchange API | Documented | 인증키, 비상업 목적, 일일 호출 제한이 있는 official data access. | Useful later for Korean derivatives reference, not first for 1m global futures monitoring. |
| Twelve Data | Market data API | Documented | Time series API, free basic quota, paid commodity market data tier. | Not first choice for futures. Could be later fallback for commodities/FX if paid tier accepted. |
| TradingView Lightweight Charts | Frontend chart library | Documented | Browser-native candlestick series and realtime `update()` pattern. | Good future UI upgrade if Streamlit chart becomes limiting. |
| Streamlit fragments | Existing app framework | Documented / Observed | `st.fragment(run_every=...)` reruns a page fragment on cadence. | Best MVP refresh mechanism inside current app. |

## Key Findings

### 1. Free real-time futures OHLCV is the hard part

Free, no-key, high-frequency futures OHLCV is not a stable commodity. `yfinance` is viable for a pilot because it already exists in the repo and local smoke showed 1분봉 rows for liquid futures. It is not an official Yahoo API, so the UI must show provider freshness and failure status instead of implying exchange-grade real time.

### 2. Official exchange data is available, but not as a simple free API

CME delayed quote pages and CME Market Data API are official directions. The delayed quote site is useful as a source link and manual reference. The API path is better for production quality, but requires account/entitlement/commercial terms work and should not be assumed free.

### 3. Crawling public chart sites is a last resort

Barchart, Investing.com, TradingView, and exchange quote pages may show futures charts, but their data is proprietary and heavily scripted. Scraping them would add terms-of-use, stability, captcha, and maintenance risk. It should only be considered after explicit user approval and caching/rate-limit guardrails.

### 4. Streamlit can support a monitoring MVP, not a professional trading chart

The existing app can render candlesticks in Altair and refresh via Streamlit fragments. For dense, interactive charting with realtime tick updates, a separate React/TradingView Lightweight Charts surface would be better. That should be a later UI-platform decision, not a blocker for the first pilot.

## Benchmark-Informed Gaps

| Gap | Source pattern | Finance implication |
| --- | --- | --- |
| Provider quality label | Free providers are unofficial or delayed | Every futures card needs provider, latest candle time, delay/staleness, and failure state. |
| Session semantics | Futures sessions differ by product | Do not reuse NYSE cash session status as futures session truth. Show "provider latest" and "watch window" instead. |
| Rate-limit protection | Free APIs have small quotas/unstated throttles | Default cadence should be 60s; fast mode should be bounded to a few symbols. |
| Chart interactivity | TradingView pattern is browser-native | Start with Altair, then evaluate Lightweight Charts if the user wants trading-terminal UX. |
