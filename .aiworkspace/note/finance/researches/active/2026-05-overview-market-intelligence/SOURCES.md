# Sources

Access date: 2026-05-28

Evidence labels:

- `Observed`: official UI/docs directly show the pattern.
- `Documented`: official docs or repository describe the pattern.
- `Claimed`: product page or marketing copy claims the pattern.
- `Inferred`: synthesis from multiple supported facts.
- `Unknown`: evidence is missing or unclear.

## Local Sources

| Source | Evidence | Notes |
| --- | --- | --- |
| `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | Documented | Defines evidence-first product boundary and no-live-trading non-goal. |
| `.aiworkspace/note/finance/docs/architecture/README.md` | Documented | Confirms ingestion -> DB -> loader/service -> Streamlit architecture. |
| `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md` | Documented | Confirms price/profile/provider/macro persistence and loader boundaries. |
| `app/web/overview_dashboard.py` | Observed | Current Overview product surface and candidate-priority UI. |
| `app/web/overview_dashboard_helpers.py` | Observed | Current Overview data contract reads registry/history sources only. |
| `finance/loaders/price.py` | Observed | Existing DB-backed price loader functions. |
| `finance/data/asset_profile.py` | Observed | Existing market-cap-ordered top-symbol helper and asset profile fields. |
| `app/web/backtest_common.py` | Observed | `US Statement Coverage 1000` managed preset already uses top US stock asset profiles by market cap. |
| Local MySQL diagnosis | Observed | `finance_meta.nyse_asset_profile`: 4,441 US active stock profiles and 4,316 US active stocks with market cap. `finance_price.nyse_price_history`: daily rows from 2006-02-07 to 2026-05-19, with effective usable date 2026-05-18. |

## Web Sources

| Source | Evidence | Notes |
| --- | --- | --- |
| Federal Reserve FOMC calendars, https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm | Observed | Official meeting calendars include 2026/2027 dates and Summary of Economic Projections markers. |
| Alpha Vantage API documentation, https://www.alphavantage.co/documentation/ | Documented | `EARNINGS_CALENDAR` CSV endpoint with horizon options and API key requirement. |
| Financial Modeling Prep Earnings Calendar API, https://site.financialmodelingprep.com/developer/docs/stable/earnings-calendar | Documented | Earnings calendar endpoint for announcement dates, EPS estimates, and actual EPS where available. |
| Nasdaq Earnings Calendar, https://www.nasdaq.com/market-activity/earnings | Observed | Public earnings calendar page; page notes expected releases are algorithm-derived and data provider is Zacks. |
| TradingView Heatmaps support, https://www.tradingview.com/support/solutions/43000766446-tradingview-heatmaps-from-global-trends-to-details/ | Documented | Heatmap pattern: size by weight metrics, color by performance/change/volatility, stocks grouped by sector. |
| TradingView Heatmap Widgets, https://www.tradingview.com/widget-docs/widgets/heatmaps/ | Documented | Stock heatmap positioned for segmentation by sector, country, or market cap. |

## Source Notes

- Prefer current, official, primary sources.
- Treat product marketing pages as feature-pattern evidence, not verified technical capability.
- Earnings calendar sources may have licensing, rate-limit, and redistribution constraints. Provider choice should happen before implementation.
