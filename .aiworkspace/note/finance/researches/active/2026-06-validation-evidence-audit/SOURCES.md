# Sources

Last updated: 2026-06-01

## Local Code And Documentation

| Source | Use |
| --- | --- |
| `.aiworkspace/note/finance/docs/INDEX.md` | Durable documentation map and read order. |
| `.aiworkspace/note/finance/docs/ROADMAP.md` | Product direction and workflow context. |
| `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | Ownership boundaries for finance package and Streamlit app. |
| `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` | Backtest UI flow and selected dashboard boundaries. |
| `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md` | Source of truth chain for selection decisions and dashboard handoff. |
| `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md` | Runtime and service module map. |
| `.aiworkspace/note/finance/researches/active/2026-05-investable-workflow-gap-analysis/CURRENT_PROJECT_AUDIT.md` | Prior product audit context. |
| `app/runtime/backtest.py` | Backtest Analysis hardening, policy surfaces, promotion decision, transaction cost postprocess. |
| `app/services/backtest_result_read_model.py` | Stage 1 Data Trust rows. |
| `app/web/backtest_result_display.py` | Stage 1 handoff and readiness rendering. |
| `app/web/backtest_compare.py` | Weighted mix candidate readiness and Practical Validation handoff. |
| `app/services/backtest_practical_validation.py` | Practical Validation orchestration and persistence boundaries. |
| `app/services/backtest_practical_validation_diagnostics.py` | Input checks, diagnostics, provider/curve context, validation builder. |
| `app/services/backtest_practical_validation_replay.py` | Actual runtime replay and period coverage. |
| `app/services/backtest_practical_validation_curve.py` | Benchmark parity and curve provenance. |
| `app/services/backtest_temporal_validation.py` | Walk-forward, OOS holdout, regime split validation. |
| `app/services/backtest_practical_validation_modules.py` | Module gate and selected-route preflight inclusion. |
| `app/services/backtest_selected_route_preflight.py` | Practical Validation selected-route preflight. |
| `app/services/backtest_validation_efficacy.py` | Validation efficacy audit. |
| `app/services/backtest_data_coverage_audit.py` | DB price/provider/PIT/lifecycle/survivorship audit. |
| `app/services/backtest_construction_risk_audit.py` | Construction risk audit. |
| `app/services/backtest_risk_contribution_audit.py` | Risk contribution audit. |
| `app/services/backtest_component_role_weight_audit.py` | Component role/weight audit. |
| `app/services/backtest_realism_audit.py` | Transaction cost, net cost, turnover, liquidity, realism audit. |
| `app/services/backtest_evidence_read_model.py` | Final Review evidence packet, selection gate, deployment policy, open review items. |
| `app/runtime/final_selected_portfolios.py` | Selected Dashboard read models, open issue follow-up, provider evidence, deployment preflight. |

## External Web Sources

Access date: 2026-06-01.

| Source | URL | Use |
| --- | --- | --- |
| Composer Knowledge Center, "Backtest Basics" | https://help.composer.trade/article/67-backtest-basics | Backtest hypothetical nature, adjusted close data, slippage, live-vs-backtest distinction. |
| QuantConnect docs, "Backtesting" | https://www.quantconnect.com/docs/v2/cloud-platform/backtesting | Backtesting purpose, historical simulation, institutional datasets, reports. |
| QuantConnect docs, "Algorithm Engine" | https://www.quantconnect.com/docs/v2/writing-algorithms/key-concepts/algorithm-engine | LEAN streaming backtest model and look-ahead contrast with batch systems. |
| QuantConnect docs, "Research Guide" | https://www.quantconnect.com/docs/v2/writing-algorithms/key-concepts/research-guide | Look-ahead and survivorship-bias guidance. |
| QuantConnect docs, "Walk Forward Optimization" | https://www.quantconnect.com/docs/v2/writing-algorithms/optimization/walk-forward-optimization | WFO and parameter optimization tradeoff/overfitting context. |
| QuantConnect docs, "Trading and Orders" | https://www.quantconnect.com/docs/v1/algorithm-reference/trading-and-orders | Slippage, transaction, brokerage model treatment. |
| AllocateSmartly FAQ | https://allocatesmartly.com/faqs/ | Backtest assumptions, transaction fees/slippage, simulated asset data, daily-vs-monthly checks, overfit/proxy caveats. |
| AllocateSmartly, "Super-Secret Proprietary Black Box Strategies" | https://allocatesmartly.com/super-secret-proprietary-black-box-strategies/ | OOS/live evidence skepticism and minimum OOS track record framing. |
| AllocateSmartly, "New Feature: The Underperformer Watchlist" | https://allocatesmartly.com/new-feature-the-underperformer-watchlist/ | Out-of-sample underperformance and historical backtest relevance warning. |
| Portfolio123, "Back-Testing Data Methodology" | https://www.portfolio123.com/doc/Backtesting_Data_Methods.pdf | Point-in-time database and survivorship-bias handling. |
| Portfolio123 Help Center, "Simulation Assumptions" | https://portfolio123.customerly.help/en/research-section/simulation-assumptions | Simulation trade timing, close price, variable slippage by liquidity. |
| Portfolio123 homepage | https://www.portfolio123.com/ | Current positioning around simulations/ranking systems/backtesting data. |
| Portfolio Visualizer generated report hosted by Vintage Value Investing | https://www.vintagevalueinvesting.com/wp-content/uploads/2021/01/VVI-Portfolio-Statistics-Report.pdf | PV report assumptions: hypothetical/backtested returns, no trading costs/fees/taxes, total return assumptions, monthly-return metrics. Direct Portfolio Visualizer site access was blocked during this audit. |
| World Gold Council Portfolio Simulator FAQ | https://www.gold.org/goldhub/tools/portfolio-simulator/faqs | Public tool disclosure referencing Portfolio Visualizer software for backtesting functionality. |

## Search Notes

Portfolio Visualizer's official site did not return accessible content through the browsing tool during this audit. The report therefore separates Portfolio Visualizer evidence into "public/generated report and secondary public pages" rather than treating it as freshly verified official website copy.

## Local DB Spot Checks

Read-only MySQL checks were run on 2026-06-01 KST. No rows were inserted, updated, deleted, or rewritten.

| Area | Tables checked | Audit use |
| --- | --- | --- |
| Price history | `finance_price.nyse_price_history` | Row count, symbol count, date range, and timeframe coverage for DB-backed price-window evidence. |
| Current asset metadata | `finance_meta.nyse_asset_profile` | Current active/delisted status and collection freshness for operability context. |
| Lifecycle / survivorship | `finance_meta.nyse_symbol_lifecycle` | Historical listing, current listing, delisting-feed, and coverage-status mix for survivorship-bias assessment. |
| ETF provider source mapping | `finance_meta.etf_provider_source_map` | Verified provider/source coverage for supported ETF symbols. |
| ETF operability | `finance_meta.etf_operability_snapshot` | AUM/spread/volume/expense/freshness source mix for current operability evidence. |
| ETF holdings / exposure | `finance_meta.etf_holdings_snapshot`, `finance_meta.etf_exposure_snapshot` | Current official holdings and exposure look-through coverage for construction-risk evidence. |
| Macro / regime | `finance_meta.macro_series_observation` | FRED-backed macro observation coverage for regime context and revision-vintage limitations. |
| Universe / intraday operations | `finance_meta.market_universe_member`, `finance_price.market_intraday_snapshot` | Current universe and provider-status freshness; not treated as historical universe proof. |
| Fundamentals / factor PIT | `finance_fundamental.nyse_fundamentals`, `finance_fundamental.nyse_factors`, `finance_fundamental.nyse_financial_statement_values`, `finance_fundamental.nyse_financial_statement_filings` | Period-end/provider-summary vs statement-backed `available_at` evidence for PIT factor-risk assessment. |
