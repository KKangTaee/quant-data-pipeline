# Sources

Access date: 2026-06-07

Evidence labels:

- `Observed`: official UI/docs directly show the pattern.
- `Documented`: official docs or repository describe the pattern.
- `Claimed`: product page or marketing copy claims the pattern.
- `Inferred`: synthesis from multiple supported facts.
- `Unknown`: evidence is missing or unclear.

## Local Sources

| Source | Evidence | Notes |
| --- | --- | --- |
| `README.md` | Documented | Describes product purpose, current user flow, Reference navigation, and no-live-trading boundaries. |
| `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | Documented | Current product direction and user-facing surface list. |
| `.aiworkspace/note/finance/docs/ROADMAP.md` | Documented | Active roadmap and completed UI / engine boundary direction. |
| `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | Documented | Ownership of `app/web/reference_guides.py`, `app/web/streamlit_app.py`, and product boundary files. |
| `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` | Documented | Existing Reference Guide flow notes and legacy/current drift. |
| `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md` | Documented | Current canonical Backtest -> Practical Validation -> Final Review -> Portfolio Monitoring flow. |
| `.aiworkspace/note/finance/docs/architecture/SYSTEM_BOUNDARIES.md` | Documented | Layer ownership, no direct UI provider fetch, no live approval/order/rebalance boundaries. |
| `app/web/reference_guides.py` | Observed | Current Guides render, static content, route selector, timeline, gates, drawer. |
| `app/web/streamlit_app.py` | Observed | Current Reference navigation includes Guides and Glossary. |
| Browser audit: `http://localhost:8501/guides` | Observed | Current first screen is portfolio-selection oriented and does not expose product-wide task entry. |

## Web Sources

| Source | Evidence | Notes |
| --- | --- | --- |
| QuantConnect Research Guide: `https://www.quantconnect.com/docs/v2/cloud-platform/backtesting/research-guide` | Documented | Hypothesis-driven research, research panel, overfitting and out-of-sample guidance. |
| QuantConnect Research Engine: `https://www.quantconnect.com/docs/v2/research-environment/key-concepts/research-engine` | Documented | Research environment before backtests, research-to-backtest separation, notebooks. |
| TradingView Strategy Report: `https://www.tradingview.com/support/solutions/43000764138-tradingview-strategy-report-how-to-start/` | Documented | Strategy report tabs: Overview, Performance, Trades analysis, Risk/performance ratios, List of trades. |
| TradingView Strategy report metrics: `https://my.tradingview.com/support/folders/43000599093-backtesting-report/` | Documented | Metric index for strategy reports. |
| Koyfin Help Center: `https://www.koyfin.com/help/` | Documented | Category/search style help center: Getting Started, Functionality, Release Notes, How do I, FAQ. |
| Koyfin My Dashboards: `https://www.koyfin.com/help/mydashboards-myd/` | Documented | Custom dashboards, widgets, watchlists, charts, grouping. |
| Koyfin Model Portfolios: `https://www.koyfin.com/help/model-portfolios/` | Documented | Model portfolio snapshots, exposure, performance, risk, drawdown, holdings matrix, settings. |
| Koyfin Watchlist Views: `https://www.koyfin.com/help/my-views/` | Documented | Reusable views, table settings, dashboard/screener reuse. |
| Interactive Brokers PortfolioAnalyst features: `https://www.interactivebrokers.com/en/portfolioanalyst/features.php` | Claimed | Dashboard widgets, reporting, allocation goals, custom benchmarking, consolidated reporting. |
| IBKR PortfolioAnalyst guides: `https://www.ibkrguides.com/portfolioanalyst/performanceandstatements/pa-performance.htm` and related guide pages | Documented | Performance widget, allocation, report limitations, default/custom reports. |
| testfolio home: `https://testfol.io/` | Claimed | Portfolio backtester, model inputs, inspectable outputs, related research tools. |
| testfolio terms: `https://testfol.io/terms` | Documented | Educational/research purpose and no investment advice boundary. |
| Composer Backtesting Tutorial: `https://help.composer.trade/article/93-tutorial-backtesting` | Documented | Short backtest tutorial and related articles. |

## Source Notes

- Prefer current, official, primary sources.
- Treat product marketing pages as feature-pattern evidence, not verified technical capability.
- Portfolio Visualizer direct page was not used as a primary benchmark source because accessible current official content was limited during this pass.
- Browser screenshot capture timed out during audit, but DOM snapshot verified the current local Guides structure.
