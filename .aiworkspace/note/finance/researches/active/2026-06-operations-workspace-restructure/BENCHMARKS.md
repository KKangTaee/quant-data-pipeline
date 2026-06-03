# Benchmarks

Access date: 2026-06-03

Evidence labels:

- `Observed`: official UI/docs directly show the pattern.
- `Documented`: official docs or repository describe the pattern.
- `Claimed`: product page or marketing copy claims the pattern.
- `Inferred`: synthesis from multiple supported facts.
- `Unknown`: evidence is missing or unclear.

## Benchmark Matrix

| Product / Service | Category | Evidence | Relevant pattern |
| --- | --- | --- | --- |
| QuantConnect | Quant research / backtesting platform | Documented | Research notebooks, backtesting, and live trading/deployment are distinct stages. |
| Bloomberg PORT | Institutional portfolio/risk analytics | Claimed / documented | Portfolio operations combine positions, risk, performance, attribution, data validation, scenarios, and reporting. |
| Interactive Brokers PortfolioAnalyst | Broker-adjacent portfolio analytics | Documented | Consolidated portfolio performance/risk/concentration reports with informational-purpose boundary. |
| Morningstar X-Ray / Rebalance | Portfolio analysis and allocation review | Documented | Holdings breakdown, benchmark-relative exposure, allocation/rebalance review. |
| Sharesight | Portfolio tracking/reporting | Documented | Report taxonomy separates performance, asset allocation, and tax/compliance. |
| Koyfin Portfolio Tools | Investor dashboard / portfolio monitor | Claimed | Custom portfolio grouping, notes, summary rows, performance monitoring. |
| Composer | Strategy builder / automation platform | Claimed | Strategy creation, backtest, historical allocation, costs/slippage, and execution are connected; useful mostly as boundary contrast. |

## Key Findings

### 1. Mature tools separate research, simulation, monitoring, reporting, and execution

- QuantConnect separates exploratory research from event-based backtesting and live trading.
- This supports keeping `Workspace > Backtest` as active candidate creation and `Operations > Selected Portfolio Dashboard` as post-selection monitoring.

### 2. Portfolio operations focus on current state, attribution, exposure, data quality, and reports

- Bloomberg PORT, IBKR PortfolioAnalyst, Morningstar X-Ray, Sharesight, and Koyfin all center portfolio views on holdings/performance/exposure/risk/reporting.
- This supports making `Selected Portfolio Dashboard` the primary portfolio monitoring surface inside Operations.

### 3. Archive/replay tools should be secondary support tools

- Benchmark products expose reports/libraries/history, but the main user mental model is current portfolio status and decision support.
- This supports demoting Backtest Run History and Candidate Library into Archive/Recovery.

### 4. Rebalance is a review target unless the product is explicitly execution-enabled

- Morningstar frames rebalancing as reviewing current allocation and adjusting toward a target.
- IBKR and Composer are closer to broker/automation boundaries, but this project explicitly excludes order and auto rebalance.

## Benchmark-Informed Gaps

| Gap | Source pattern | Finance implication |
| --- | --- | --- |
| No Operations landing page | Bloomberg/IBKR consolidated operations views | Add Operations Overview / Command Center. |
| Primary and archive tools are peers | Sharesight/Koyfin report/tool taxonomy | Separate Portfolio Monitoring, System/Data Health, Archive/Recovery, Reports. |
| Selected Dashboard naming is accurate but long | Portfolio monitor products emphasize portfolio/current status | Consider UI copy around "Portfolio Monitoring" while keeping route compatibility. |
| Rebalance target table can be misread | Morningstar rebalance review pattern | Keep read-only target/review wording and connect to actual allocation/drift evidence. |
| Legacy candidate tools still visible as first-class Operations tabs | Stage separation from QuantConnect and current project docs | Demote but do not delete until audit/replay replacement exists. |
