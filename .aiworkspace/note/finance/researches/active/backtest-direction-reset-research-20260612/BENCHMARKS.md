# Benchmarks

Status: Active
Last Updated: 2026-06-12 KST

## Research Question

Backtest 제품은 전략 실행 결과, evidence/diagnostics, replay/history/saved setup, validation handoff, prototype/research labels를 어떻게 분리해야 하는가?

## Selection Criteria

이번 pass는 5개만 본다. 각 benchmark는 서로 다른 각도를 대표한다.

- Quant research / backtesting platform: QuantConnect
- Portfolio analytics / backtesting tool: Portfolio Visualizer
- Rules-based stock strategy platform: Portfolio123
- Portfolio / ETF analytics platform: Koyfin
- Broker-adjacent portfolio monitoring / reporting: Interactive Brokers PortfolioAnalyst

## Benchmark Matrix

| Product Or Framework | Category | Target User | Relevant Workflow | Evidence Label | Applicability |
| --- | --- | --- | --- | --- | --- |
| QuantConnect | Quant research / cloud backtesting / notebook workflow | Quant developers and systematic researchers | Project -> backtest results -> reports/history -> research notebook meta-analysis -> live deployment is separate. | Documented | Strong pattern for separating run results, historical backtest list, research notebook diagnostics, and OOS holdout. |
| Portfolio Visualizer | Portfolio backtest / analytics web tool | Portfolio researchers, advisors, DIY allocators | Configure portfolios -> run asset allocation backtest -> compare historical/realized return and risk characteristics. | Claimed / Documented | Strong fit for Backtest Analysis as an execution and comparison surface, weak fit for validation governance. |
| Portfolio123 | Rules-based stock screening / ranking / simulation | Fundamental/systematic stock strategy builders | Idea -> ranking system / buy-sell rules -> simulation / screen backtest -> robustness thinking -> manage/live features. | Claimed / Documented | Strong pattern for separating ranking model, simulation rules, robustness, and live strategy launch. |
| Koyfin | Model portfolio / ETF research / analytics | Advisors, research teams, investors | Build model portfolio -> track performance/risk/exposure/drift -> benchmark comparison -> reports; ETF holdings/contribution has caveats. | Claimed / Documented | Strong pattern for Portfolio Monitoring and provider/holdings caveats; not a direct strategy runtime model. |
| IBKR PortfolioAnalyst | Broker-adjacent portfolio analytics/reporting | Investors/advisors with broker and external accounts | Consolidated portfolio -> performance/risk/concentration -> default/custom reports -> saved report definitions. | Documented / Claimed | Strong pattern for Operations monitoring/reporting; should not pull broker-order behavior into this project. |

## Product Notes

### QuantConnect

- Category: quant research and backtesting platform.
- Target user: developers building systematic strategies.
- Main workflow: create project, run cloud backtest, open result page/history table, inspect report statistics, use Research Environment for deeper meta-analysis.
- Relevant features:
  - Backtests are launched from a project and open a result page when they run.
  - Project backtest history can be filtered, sorted, renamed, and reopened.
  - Reports summarize turnover, CAGR, drawdown, Sharpe, capacity, returns, allocation, drawdown, rolling stats, exposure, and crisis events.
  - Backtest results can be loaded into a notebook research environment for trade-level and raw-data comparison.
  - Organization managers can enforce out-of-sample holdout periods.
- UI/workflow patterns:
  - Result page is not the same as research notebook.
  - History table is not the same as report.
  - Out-of-sample policy is an organizational gate, not a chart decoration.
- Data/evidence model:
  - Backtest result has an ID and can be read by API.
  - Reports aggregate key statistics and diagnostics.
  - Research notebooks can load prior result data.
- Strong ideas for this project:
  - Keep Backtest Analysis as run/result/history surface.
  - Move deep diagnostics into a research/reference lane or validation stage.
  - Treat OOS / holdout as a gate, not as optional prose.
- Ideas to avoid:
  - Do not copy a live deployment workflow; this project has no live trading boundary.
- Evidence label: Documented.
- Evidence limits: Source docs describe platform workflow, not direct UI inspection inside a live account.
- Sources: QuantConnect Backtesting Getting Started, Report, Research Backtest Analysis.

### Portfolio Visualizer

- Category: web portfolio backtesting and portfolio analytics.
- Target user: allocation researchers, advisors, independent investors.
- Main workflow: construct one or more portfolios from funds/ETFs/stocks or asset class allocations, run backtest, compare return/risk characteristics.
- Relevant features:
  - Public pages emphasize portfolio asset allocation backtesting and comparison of historical/realized returns and risk.
  - Analysis catalog separates backtesting, Monte Carlo, tactical asset allocation, optimization, and other tools.
- UI/workflow patterns:
  - The first screen is task-specific: choose a backtest/analysis tool and configure inputs.
  - Backtest result comparison is core; governance/approval is outside the tool.
- Data/evidence model:
  - The publicly visible source does not expose detailed persistence/replay internals.
- Strong ideas for this project:
  - Backtest Analysis should make strategy execution and portfolio mix comparison fast and uncluttered.
  - Keep analysis tools task-specific rather than putting every diagnostic in one surface.
- Ideas to avoid:
  - Do not collapse validation handoff into a simple "nice chart means candidate-ready" model.
- Evidence label: Claimed / Documented.
- Evidence limits: Portfolio Visualizer blocked direct `curl` access with 403 during this pass; notes rely on official search result snippets and public page availability, not live UI inspection.
- Sources: Portfolio Visualizer Backtest Portfolio, Analysis Tools.

### Portfolio123

- Category: rules-based stock strategy research, screening, ranking, simulation.
- Target user: systematic stock investors and portfolio managers.
- Main workflow: start with investment idea, create ranking system, build buy/sell rules, simulate/backtest, inspect robustness, optionally manage/live strategy.
- Relevant features:
  - Public product page separates portfolio simulations, stock screener, AI/ML, advanced charts, data, models, and manage/live strategy.
  - Tutorials separately list simulated strategy basics/refinement/launching, screen backtest, ranking, macro charts, and rolling tests.
  - Official blog warns against optimizing only on CAGR, short/fixed periods, small position counts, and in-sample overfitting.
- UI/workflow patterns:
  - Ranking model, screen backtest, simulation, rolling tests, and live launch are separate learning/workflow objects.
  - Robustness is part of strategy design, not an afterthought after promotion.
- Data/evidence model:
  - Claims point-in-time historical data and a broad backtesting data set, but this pass does not verify data methodology deeply.
- Strong ideas for this project:
  - Strict quarterly prototypes need explicit PIT / filing lag / replay robustness before candidate readiness.
  - Mature strategies should have a robustness gate beyond best CAGR/MDD.
- Ideas to avoid:
  - Do not add broker/trade management features just because the benchmark has a manage/live area.
- Evidence label: Claimed / Documented.
- Evidence limits: Some details come from marketing and tutorial index, not an authenticated workspace.
- Sources: Portfolio123 home, tutorials, fundamentals backtesting principles blog.

### Koyfin

- Category: portfolio analytics, model portfolios, ETF/fund research.
- Target user: advisors, research teams, independent investors.
- Main workflow: build model portfolios, adjust allocation/rebalancing/fees/currency, compare against benchmarks, inspect risk/exposure/drift, create reports.
- Relevant features:
  - Model portfolio page emphasizes summary snapshots, drift analysis, benchmark comparisons, sleeves, performance, risk, exposure, and reports.
  - ETF holdings contribution help page explicitly states caveats about current constituents, missing delisted/acquired holdings, and reconciliation.
- UI/workflow patterns:
  - Monitoring uses a summary snapshot first, then drilldowns.
  - Exposure and benchmark comparison are distinct from allocation editing.
  - Provider/holdings caveats are visible and precise.
- Data/evidence model:
  - Model portfolio analytics include target allocations and benchmark comparisons.
  - ETF contribution uses estimated weights and current constituents when historical constituent data is unavailable.
- Strong ideas for this project:
  - Portfolio Monitoring should keep "summary first, detail on demand."
  - Provider evidence caveats should be first-class, especially for ETF holdings/exposure and survivorship assumptions.
  - Sleeves map well to strict annual + ETF bridge framing.
- Ideas to avoid:
  - Do not treat current holdings contribution as perfect historical evidence.
- Evidence label: Claimed / Documented.
- Evidence limits: Product page is marketing; ETF caveat source is stronger because it documents calculation limitations.
- Sources: Koyfin Model Portfolios, Koyfin ETF Holdings / Contribution help.

### Interactive Brokers PortfolioAnalyst

- Category: broker-adjacent consolidated portfolio analytics and reporting.
- Target user: investors and advisors monitoring actual accounts and linked external accounts.
- Main workflow: open PortfolioAnalyst, analyze consolidated portfolio by asset class/sector/instrument/region/country/date, inspect concentration/risk metrics, run default or custom reports.
- Relevant features:
  - Overview page highlights performance, concentration, risk, drawdown, Sharpe, Sortino, alpha/beta, and portfolio drilldowns.
  - Features page highlights reports, holdings, allocation, performance, attribution vs benchmark, projected income, risk measures, and custom reporting.
  - Trading lesson describes default report types, saved custom reports, benchmark selection, and report rerun/edit/delete.
- UI/workflow patterns:
  - Monitoring/reporting is a separate post-selection experience.
  - Default reports and custom reports are saved artifacts, not strategy build screens.
  - Broker data can power analysis without making every analysis screen an order screen.
- Data/evidence model:
  - PortfolioAnalyst can consolidate broker/external account data and produce saved reports.
- Strong ideas for this project:
  - Operations > Portfolio Monitoring should remain monitoring/reporting, not strategy research.
  - Decision dossiers and reports can be saved/re-run without implying broker order execution.
- Ideas to avoid:
  - Do not import broker-account or order workflows into the current no-live product boundary.
- Evidence label: Documented / Claimed.
- Evidence limits: Official pages are product docs/marketing, not an audited behavior test.
- Sources: IBKR PortfolioAnalyst overview, features, reports lesson.

## Cross-Product Patterns

| Pattern | Seen In | Finance Implication |
| --- | --- | --- |
| Run result is separate from deep research diagnostics | QuantConnect | Backtest Analysis should show latest result and replay context; deeper diagnostics can live in reference/research or Practical Validation. |
| History/reports are separate objects | QuantConnect, IBKR PortfolioAnalyst | Backtest run history and decision dossiers should be inspect/replay/report surfaces, not the primary strategy design screen. |
| First screen is task-specific | Portfolio Visualizer, Koyfin | Backtest Analysis should lead with Single Strategy / Portfolio Mix Builder, not maturity panels. |
| Robustness gates prevent overfit promotion | QuantConnect, Portfolio123 | Quarterly prototype maturation and high-performing strategies need OOS/PIT/robustness gates before readiness labels change. |
| Provider/exposure caveats are explicit | Koyfin | ETF evidence should show current-constituent, holdings coverage, and survivorship caveats rather than hiding them in provider notes. |
| Monitoring/reporting is post-selection | Koyfin, IBKR PortfolioAnalyst | Operations should stay read-only scenario/reporting and not absorb strategy research. |

## Architecture / Platform Implications

- A good Backtest product has at least four objects: `run result`, `replayable setup`, `validation evidence`, and `monitoring/report`. The current project already has these objects; the next work should clarify their handoff rather than add panels.
- Strategy maturity should be a compact read model / report contract. It should not be another default Backtest Analysis workbench.
- Saved replay is a reproducibility feature. Practical Validation is the evidence gate. Final Review is the selected-route gate. Portfolio Monitoring is a post-selection observation surface.
- Prototype labels must survive good performance. Performance can nominate a strategy for maturation, but cannot itself change maturity.

## Benchmark-Informed Gaps

| Gap | Source Pattern | Finance Implication |
| --- | --- | --- |
| Backtest Analysis still hosts too many optional maturity/governance panels | Portfolio Visualizer task-first tools, QuantConnect result vs notebook split | Move broad references toward Reference/report surfaces or keep them hidden by default. |
| Quarterly prototype lacks formal maturity gate | Portfolio123 robustness warnings, QuantConnect OOS holdout | Defer 5C until PIT/filing-lag/replay/OOS criteria are defined. |
| ETF evidence needs caveat discipline | Koyfin ETF contribution caveats | Provider/holdings/exposure evidence must state current-constituent and missing historical constituent risks. |
| Portfolio Monitoring could drift into action screen | IBKR reporting separation | Keep monitoring/reporting read-only and explicitly no broker order / auto rebalance. |
| Saved setup can be mistaken for validation | QuantConnect history/report separation | Saved replay should be framed as setup reproducibility, not readiness. |
