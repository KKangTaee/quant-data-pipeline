# Sources

Access date: 2026-05-14

Evidence labels:

- `Observed`: 공식 화면/문서에서 직접 확인한 기능 또는 UI 구조
- `Documented`: 공식 문서/repository에 설명된 기능
- `Claimed`: 제품 마케팅 페이지의 주장
- `Inferred`: 여러 근거를 종합한 해석

## Local Sources

| Source | Evidence | Notes |
| --- | --- | --- |
| `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | Documented | evidence-first product direction, no live trading boundary |
| `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | Documented | app/web, finance runtime, reports/backtests ownership |
| `.aiworkspace/note/finance/docs/ROADMAP.md` | Documented | product research model and active research location |
| `.aiworkspace/note/finance/docs/architecture/BACKTEST_RUNTIME_FLOW.md` | Documented | result bundle, metadata, warnings, data trust flow |
| `.aiworkspace/note/finance/reports/backtests/INDEX.md` | Documented | report workspace structure |
| `.aiworkspace/note/finance/reports/backtests/TEMPLATE.md` | Documented | current durable report template |
| `app/web/backtest_result_display.py` | Observed | current Streamlit result display behavior |
| `app/web/runtime/history.py` | Observed | run history helper and possible path drift to review |
| `finance/performance.py` | Observed | current core performance summary metric set |
| `app/web/backtest_practical_validation_replay.py` | Observed | validation replay/evidence source |
| `app/web/runtime/final_selected_portfolios.py` | Observed | selected portfolio replay/source summary behavior |

## Web Sources

| Source | Evidence | Notes |
| --- | --- | --- |
| [QuantConnect Backtesting Results](https://www.quantconnect.com/docs/v2/cloud-platform/backtesting/results) | Observed / Documented | results page, runtime stats, charts, orders/trades/logs, share/download patterns |
| [QuantConnect Backtest Report](https://www.quantconnect.com/docs/v2/cloud-platform/backtesting/report) | Documented | returns, monthly heatmap, drawdown periods, rolling beta/Sharpe, exposure, crisis-period report patterns |
| [QuantRocket Usage Guide](https://www.quantrocket.com/docs/) | Documented | Moonshot backtests can produce CSV and PDF/pyfolio tear sheets |
| [TradingView Strategy Report: How to start](https://www.tradingview.com/support/solutions/43000764138-tradingview-strategy-report-how-to-start/) | Observed / Documented | Overview, Performance, Trades analysis, Risk/performance ratios tab pattern |
| [QuantStats GitHub](https://github.com/ranaroussi/quantstats) | Documented | metrics, plots, reports, HTML tear sheets, risk metric breadth |
| [pyfolio GitHub](https://github.com/quantopian/pyfolio) | Documented | portfolio/risk analytics and tear sheet pattern |
| [NautilusTrader Reports](https://nautilustrader.io/docs/latest/concepts/reports/) | Documented | structured report provider from orders, fills, positions, account states |
| [Portfolio Backtest](https://www.portfoliobacktest.com/) | Claimed | AI-assisted portfolio backtesting, comparisons, metrics, shareable insights; used as market signal only |

## Source Notes

- QuantConnect and TradingView were weighted more heavily for UI/report structure because they expose product-facing result surfaces.
- QuantRocket, QuantStats, pyfolio, and NautilusTrader were weighted more heavily for artifact and analytics structure.
- Portfolio Backtest was used as a market-direction signal only because the public page is primarily marketing copy.
- Pricing and packaging were not used for priority decisions in this research.
