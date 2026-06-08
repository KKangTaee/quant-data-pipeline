# Sources

Access date: 2026-06-08 KST
Previous access date: 2026-05-28 KST

Evidence labels:

- `Observed`: official UI/docs directly show the pattern.
- `Documented`: official docs or repository describe the pattern.
- `Claimed`: product page or marketing copy claims the pattern.
- `Inferred`: synthesis from multiple supported facts.
- `Unknown`: evidence is missing or unclear.

## Local Sources

| Source | Evidence | Notes |
| --- | --- | --- |
| `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | Documented | Current product promise, no-live-trading boundary, Evidence First and DB-backed runtime principles. |
| `.aiworkspace/note/finance/docs/ROADMAP.md` | Documented | Current active focus: Practical Validation V2 P2 closeout / P3 QA and product research model. |
| `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | Documented | Code ownership map for backtest, Practical Validation, Final Review, Selected Dashboard, data pipeline, registries. |
| `.aiworkspace/note/finance/docs/architecture/BACKTEST_RUNTIME_FLOW.md` | Documented | Backtest runtime, result bundle, Data Trust metadata, strategy/result contract. |
| `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md` | Documented | Ingestion -> DB -> loader -> runtime / Practical Validation flow and data integrity checkpoints. |
| `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md` | Documented | Selection V2 source -> validation -> final decision -> selected dashboard contract. |
| `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` | Documented | Backtest UI surfaces, legacy compatibility, Practical Validation provider flow, dashboard boundaries. |
| `.aiworkspace/note/finance/docs/data/DATA_QUALITY_AND_PIT_NOTES.md` | Documented | PIT, look-ahead, survivorship, current snapshot, FRED vintage, stale data risks. |
| `.aiworkspace/note/finance/docs/data/TABLE_SEMANTICS.md` | Documented | ETF provider source map, operability, holdings, exposure, macro table semantics and snapshot caveats. |
| `.aiworkspace/note/finance/registries/README.md` | Documented | V2 and legacy registry source-of-truth boundary, append-only policy, no-live approval. |
| `.aiworkspace/note/finance/tasks/active/practical-validation-v2/PLAN.md` | Documented | Practical Validation V2 P2 target diagnostics and completion criteria. |
| `.aiworkspace/note/finance/tasks/active/practical-validation-v2/RISKS.md` | Documented | Known provider coverage, stress REVIEW, source origin confusion risks. |
| `app/services/backtest_practical_validation_diagnostics.py` | Observed | `NOT_RUN` scoring, route logic, provider coverage, diagnostic result shape, critical NOT_RUN list. |
| `app/web/backtest_final_review_helpers.py` | Observed | Final Review decision evidence, selected route save evaluation, paper observation snapshot. |
| `app/services/backtest_evidence_read_model.py` | Observed | Final decision display labels and evidence row read model. |

## Web Sources

| Source | Evidence | Notes |
| --- | --- | --- |
| QuantConnect Docs, https://www.quantconnect.com/docs/v2/ | Documented | Official docs describe LEAN, Python/C#, cloud/local platforms, research, notebooks, backtesting, optimization, live trading. Used for reproducible research/backtest/deployment pattern, not as a recommendation to add live trading. |
| Bloomberg PORT, https://professional.bloomberg.com/products/bloomberg-terminal/portfolio-analytics/ | Claimed / Documented | Official product page describes unified positions, risk, performance, attribution, stress scenarios, data validation service, reporting, orchestration. Marketing-oriented source; detailed models not inspected. |
| Morningstar Portfolio X-Ray landing, https://portfolio.morningstar.com/rtport/reg/xray_landingpage.aspx | Documented | Official page describes asset allocation, sector, fees, style, regions, top holdings, stock intersection. Used for look-through pattern. |
| Morningstar Portfolio X-Ray sample/report PDF, https://advisor.morningstar.com/enterprise/reports/xray.pdf | Documented | Sample/disclosure describes portfolio composition, underlying fund holdings, data limitations, asset allocation, style, expenses, risk/return statistics. |
| Interactive Brokers PortfolioAnalyst standalone page, https://www.interactivebrokers.co.uk/en/trading/pa-standalone-splash.php | Documented | Official page describes TWR/MWR, risk measures, benchmark comparison, attribution, external accounts. |
| Interactive Brokers PortfolioAnalyst features, https://www.interactivebrokers.com/en/portfolioanalyst/features.php | Documented | Official page describes custom benchmarks, external accounts, data security, informational-use disclosure. |
| Interactive Brokers Portfolio Checkup, https://www.interactivebrokers.com/en/software/pa-checkup.php | Documented | Official page describes exposure by asset class / sector / geography, fund parser, risk metrics, benchmark comparison. |
| Portfolio Lab, https://www.portfoliolab.app/ | Claimed | Product page claims optimization, Monte Carlo, historical backtesting, factor exposure, capital market assumptions, saved portfolios, PDF reports, browser-side calculations. Used as feature-pattern evidence, not independent verification. |
| CFA Institute, Backtesting & Simulation, https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/backtesting-and-simulation | Documented | Professional education source describes backtesting, scenario analysis, simulation, sensitivity analysis, rolling-window backtesting, survivorship and look-ahead bias. |
| FINRA / SEC Investor Alert: Automated Investment Tools, https://www.finra.org/investors/insights/automated-investment-tools | Documented | Official investor alert emphasizes assumptions, limitations, user-specific suitability, personal data, and output limitations. |
| FINRA Regulatory Notice 17-06, https://www.finra.org/rules-guidance/notices/17-06 | Documented | Regulatory source on hypothetical illustrations, reasonable basis, assumptions, limitations, and concerns around hypothetical back-tested performance. |
| FINRA Non-Traditional ETFs FAQ, https://www.finra.org/rules-guidance/key-topics/etf/non-traditional-etf-faq | Documented | Official source on leveraged / inverse ETF daily reset, suitability, holding period, product understanding. |
| NBER Working Paper 21329, Backtesting Strategies Based on Multiple Signals, https://www.nber.org/papers/w21329 | Documented | Academic source on multi-signal overfitting and multiple testing bias. |

## Source Notes

- External product pages can change. Claims are treated as benchmark patterns as of 2026-05-28 KST.
- Product marketing pages are not treated as proof of calculation correctness.
- Regulatory / professional sources are used to justify caution around hypothetical performance, assumptions, and backtest interpretation.
- No investment recommendation is made by this research.

## 2026-06-08 Refresh Sources

### Local Sources

| Source | Evidence | Notes |
| --- | --- | --- |
| `.aiworkspace/note/finance/docs/INDEX.md` | Documented | Current active phase/task state, doc structure, and product map pointers. |
| `.aiworkspace/note/finance/docs/ROADMAP.md` | Documented | Current merged flow, completed foundations, next decisions, and no active phase state as of 2026-06-08. |
| `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | Documented | Current file ownership map for Backtest, Practical Validation, Final Review, Operations, Portfolio Monitoring, and runtime/service boundaries. |
| `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | Documented | Current product promise, target experience, no-live boundary, and product surface list. |
| `.aiworkspace/note/finance/docs/architecture/SYSTEM_BOUNDARIES.md` | Documented | Layer and product-surface boundaries for ingestion, overview, backtest analysis, validation, final review, operations, and monitoring. |
| `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` | Documented | Current Backtest UI flow, Operations-owned archives, Reference Center flow, and Portfolio Monitoring behavior. |
| `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md` | Documented | Current source -> validation -> final decision -> monitoring chain and user-facing rules. |
| `app/web/backtest_workflow_routes.py` | Observed | 3 visible Backtest stages and legacy panel mapping. |
| `app/web/operations_overview.py` | Observed | Operations Console model, action queue, surface audit, no-live boundary, and archive / recovery semantics. |
| `app/runtime/portfolio_selection_v2.py` | Observed | Current JSONL source / validation / final decision / monitoring log helper boundaries. |
| `app/services/backtest_evidence_read_model.py` | Observed | Final Review decision labels, gate policy group labels, and evidence read model contract. |
| `wc -l` on core files | Observed | Large-surface signal: `backtest_compare.py`, `final_selected_portfolio_dashboard.py`, `final_selected_portfolios.py`, and `backtest_evidence_read_model.py` remain high-risk edit surfaces. |

### Web Sources

| Source | Evidence | Notes |
| --- | --- | --- |
| QuantConnect Backtesting, https://www.quantconnect.com/docs/v2/cloud-platform/backtesting | Documented | Official docs describe backtesting as historical simulation and link to results, reports, deployment, and optimization. |
| QuantConnect Backtesting Report, https://www.quantconnect.com/docs/v2/cloud-platform/backtesting/report | Documented | Official docs show report sections: key statistics, returns, asset allocation, drawdown, rolling statistics, exposure, crisis events, and parameters. |
| QuantConnect Walk Forward Optimization, https://www.quantconnect.com/docs/v2/writing-algorithms/optimization/walk-forward-optimization | Documented | Official docs describe trailing-window parameter optimization and overfitting tradeoffs. |
| Portfolio123 Ranking System, https://portfolio123.customerly.help/en/articles/13611-ranking-system | Documented | Official help describes factor/formula ranking, weights, direction, subset ranking, and percentile-rank output. |
| Portfolio123 Simulation Assumptions, https://portfolio123.customerly.help/en/articles/13753-simulation-assumptions | Documented | Official help documents model-based performance, trade timing, slippage, splits/dividends, universe exits, and cash assumptions. |
| Composer Backtest Basics, https://help.composer.trade/article/67-backtest-basics | Documented | Official help states backtests are hypothetical, use assumptions, differ from live trading, use daily adjusted close prices, and include fee/slippage assumptions. |
| Composer API, https://api.composer.trade/docs/index.html | Documented | Official API separates portfolio, backtest, deploy, dry run, and direct trading endpoints; used as boundary evidence, not implementation target. |
| Bloomberg PORT, https://professional.bloomberg.com/products/bloomberg-terminal/portfolio-analytics/ | Claimed / Documented | Official product page describes data validation, risk / attribution, scenario families, and reporting workflows. |
| Morningstar X-Ray Help, https://www.morningstar.com/help-center/portfolio/xray | Documented | Official help describes holdings breakdown, benchmark selection, asset class, regions, sectors, fees, stock stats, and style views. |
| Koyfin Model Portfolios Feature, https://www.koyfin.com/features/model-portfolios/ | Claimed / Documented | Official page describes drift analysis, benchmark comparison, sleeves, exposures, historical returns, risk metrics, holdings matrix, reports, and alerts. |
| Koyfin Model Portfolios Help, https://www.koyfin.com/help/model-portfolios/ | Documented | Official help describes start date, benchmark, rebalancing frequency, custom allocation dates, risk metrics, drawdowns, stress tests, and holdings matrix. |
| Interactive Brokers PortfolioAnalyst, https://portal.interactivebrokers.com/es/portfolioanalyst/overview.php | Documented | Official page describes consolidated accounts, performance/risk/concentration analysis, benchmarks, allocation, sectors, and reporting. |

### Refresh Source Notes

- 2026-06-08 web sources are current public pages only. They support product-pattern benchmarking, not vendor calculation correctness.
- Bloomberg and Koyfin product pages contain marketing language; claims are treated as pattern evidence unless supported by help docs.
- Composer execution / deployment endpoints are used as contrast evidence. They are not a recommendation to add live trading.
- Local code inspection was static. No Streamlit UI run or browser walkthrough was performed in this refresh.
