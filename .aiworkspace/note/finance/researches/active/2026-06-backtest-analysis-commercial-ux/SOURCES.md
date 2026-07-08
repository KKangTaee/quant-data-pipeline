# Sources

Status: Active
Last Updated: 2026-06-29 KST

## Local Sources

| Source | Type | Evidence | Confidence | Limitations |
|---|---|---|---|---|
| `AGENTS.md` | Repo instruction | Workflow, UX approval, real-use improvement rule, Backtest boundaries | High | Session-specific policy |
| `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | Durable docs | Evidence-first / DB-backed / no live trading product boundary | High | Last verified 2026-06-08 |
| `.aiworkspace/note/finance/docs/ROADMAP.md` | Durable docs | Recent Backtest 4C, 5A, 5B state | High | Latest overall work is Overview |
| `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | Durable docs | Backtest file ownership and workflow boundaries | High | May lag minor code changes |
| `.aiworkspace/note/finance/docs/architecture/BACKTEST_RUNTIME_FLOW.md` | Durable docs | runtime/result bundle contracts | High | Focuses architecture, not UX critique |
| `.aiworkspace/note/finance/docs/architecture/STRATEGY_IMPLEMENTATION_FLOW.md` | Durable docs | strategy implementation ownership and contracts | High | Not a test report |
| `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` | Durable docs | Backtest UI and downstream flow | High | Last verified 2026-06-09 |
| `app/web/pages/backtest.py` | Code | top usage guide and workflow selector | Observed | No live browser run in research pass |
| `app/web/backtest_analysis.py` | Code | Reference/research panels and default analysis render | Observed | UI state can affect visibility |
| `app/web/backtest_result_display.py` | Code | Latest Run, Data Trust, readiness, handoff display | Observed | Need runtime sample for full QA |
| `app/services/backtest_result_read_model.py` | Code | data trust rows | Observed | Limited handoff logic currently in UI file |
| `app/services/backtest_execution.py` | Code | strategy dispatch | Observed | Does not prove data availability |
| `finance/strategy.py`, `finance/swing.py`, `app/runtime/backtest*.py` | Code | strategy logic ownership | Observed | Full correctness needs tests/smoke |

## Web Sources

Access date: 2026-06-29 KST.

| Source | URL | Owner | What It Supports | Evidence Label | Confidence | Limitations |
|---|---|---|---|---|---|---|
| QuantConnect Backtesting Results | https://www.quantconnect.com/docs/v2/cloud-platform/backtesting/results | QuantConnect | Result page has runtime stats, charts, key stats, reports, orders, trades, logs, downloads | Documented | High | Product includes live trading concepts out of current boundary |
| TradingView Pine Script Strategies / Strategy Tester | https://www.tradingview.com/pine-script-docs/concepts/strategies/ | TradingView | Strategy Tester uses Overview, Performance Summary, List of Trades, Properties | Documented | High | Chart/trading context differs from portfolio research workflow |
| TradingView backtesting and forward testing help | https://www.tradingview.com/support/solutions/43000562362-what-are-strategies-backtesting-and-forward-testing/ | TradingView | Strategy report has metrics/list of trades and report updates with data | Documented | High | Trading script execution semantics differ |
| Koyfin Model Portfolios feature page | https://www.koyfin.com/features/model-portfolios/ | Koyfin | Model portfolio performance, risk exposures, reports, rebalancing, fees, benchmarks | Documented / Claimed | Medium-High | Public page is marketing-oriented |
| Koyfin Model Portfolios help | https://www.koyfin.com/help/model-portfolios/ | Koyfin | Summary snapshot, exposure, performance chart, rolling returns, historical returns, risk metrics, drawdown, holdings matrix | Documented | High | Requires product account for full UI observation |
| Interactive Brokers PortfolioAnalyst overview | https://www.interactivebrokers.com/en/portfolioanalyst/overview.php | Interactive Brokers | portfolio performance, concentration, risk, drilldowns by asset/sector/region/time | Documented / Claimed | Medium-High | Broker/account-linked workflow out of boundary |
| Portfolio123 public product page | https://www.portfolio123.com/ | Portfolio123 | idea -> ranking system -> fine tune/backtest/robustness -> launch/monitor flow | Claimed | Medium | Public marketing page, not full docs |
| Composer backtest article | https://www.composer.trade/learn/how-do-backtests-work-in-composer | Composer | backtest settings, fees/slippage, chart, benchmarks, metrics, allocations, overfitting, past-performance caution | Documented | Medium-High | Broker/autotrading context out of boundary |
| testfol.io public page | https://testfol.io/ | testfol.io | multi-portfolio comparison, rebalancing, cashflows, drawdowns, rolling returns | Claimed | Medium | Terminal extraction limited |
