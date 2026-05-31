# Sources

Access date: 2026-05-28 KST

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
