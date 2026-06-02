# External Validation Evidence Benchmarks

Last updated: 2026-06-01

## Purpose

This note compares current external products/services against the local Backtest Analysis -> Practical Validation -> Final Review -> Selected Dashboard validation chain. It is not a vendor recommendation.

## Comparison

| Product/service | Evidence they emphasize | Cost / slippage / execution assumption treatment | PIT / survivorship / data-quality treatment | OOS / robustness treatment | Takeaway for current product |
| --- | --- | --- | --- | --- | --- |
| Portfolio Visualizer | Historical portfolio backtest, risk/return statistics, correlation, drawdown, Monte Carlo/factor features in public secondary descriptions; PV-generated reports include assumptions/disclaimers. | Public PV-generated reports state hypothetical returns do not reflect trading costs, transaction fees, or taxes. | Public generated report says data is from sources considered reliable but not guaranteed complete; direct official site was not accessible in this audit. | Primarily historical/statistical analysis; robustness depends on user changing periods or tools. | Keep hypothetical labels. Current product has better cost proof potential, but must not overstate backtests. |
| Composer | Strategy/symphony backtests, adjusted close simulation, benchmark comparisons, live-vs-backtest distinction. | Official help discusses slippage and optional Trading Pass cost estimates; backtests differ from live trading. | Uses daily adjusted closes for stocks/ETFs and notes historical decisions differ from real-time trading data. | Backtests are framed as hypothetical and not recommendations. | Good model for separating simulation price basis from live trade basis. |
| QuantConnect | Event/streaming backtests, LEAN engine, cloud/local backtests, reports, optimization, WFO, historical data APIs. | Official docs support brokerage/fee/fill/slippage models and warn default/no-slippage behavior in some modes. | Official research guide warns to use dynamic universes and point-in-time data to avoid look-ahead and survivorship bias. | Official WFO docs describe periodic parameter optimization and tradeoff with overfitting. | Benchmark for code-level reproducibility and explicit reality models. Current product should add data/code hashes and richer slippage/capacity models. |
| AllocateSmartly | Tactical allocation strategy tracking, near-real-time allocations, model portfolios, long-history backtests with strict shared assumptions. | Official FAQ assumes close execution and 0.10% per trade fee+slippage, reinvested dividends/gains, cash return, no individual taxes. | Uses large liquid ETF proxies and simulated asset data to extend history; explains proxy limitations and daily-vs-monthly checks. | Explicitly discusses overfitting, daily-vs-monthly alternate trading days, out-of-sample concerns, and underperformer watchlist. | Best benchmark for transparent assumptions, proxy labeling, and overfit language. |
| Portfolio123 | Stock screens/ranking/simulations with point-in-time data, historical universe, ranking systems, simulation assumptions. | Official help describes Monday close execution assumptions and variable slippage by liquidity. | Official data methodology says Portfolio123 backtesting is point-in-time and not impacted by survivorship bias for its standard data handling. | Blog and platform materials mention rank performance tests, rolling screen backtests, simulations, and OOS concerns. | Strong benchmark for explicit historical universe and liquidity-dependent slippage. |

## External Standard Pattern

The best external patterns have three traits:

1. They label historical results as hypothetical and not recommendations.
2. They spell out shared assumptions: trade time, price basis, dividends, fees/slippage, taxes, cash return, and proxy/simulated data.
3. They separate "selection/monitoring candidate" from "live execution readiness".

The current product already implements more internal gate plumbing than many portfolio backtesting tools, but it should strengthen labels and assumptions before using words like "real-money", "deployment", or "ready".
