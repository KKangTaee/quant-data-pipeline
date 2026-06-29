# Sources

Status: Active
Last Updated: 2026-06-12 KST
Access date: 2026-06-12 KST

Evidence labels:

- `Observed`: local code or directly visible official docs show the behavior.
- `Documented`: durable docs or official docs describe the behavior.
- `Claimed`: product page / marketing copy claims the capability.
- `Inferred`: synthesis from multiple supported facts.
- `Unknown`: evidence is missing or unclear.

## Local Sources

| Title / Path | Publisher / Owner | Evidence Label | Supports | Source Type | Confidence | Limitations |
| --- | --- | --- | --- | --- | --- | --- |
| `.aiworkspace/note/finance/docs/INDEX.md` | local project | Documented | Current docs structure and active-state reading order. | Durable doc | High | Last verified date is 2026-06-10. |
| `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | local project | Documented | Evidence-first product promise, DB-backed runtime, no-live boundary. | Durable doc | High | May lag branch-specific reset details. |
| `.aiworkspace/note/finance/docs/ROADMAP.md` | local project | Documented | 4C reset, 5A/5B completed runtime hardening, no active phase, next decisions. | Durable doc | Medium | File was pre-existing dirty before this research; this run did not edit it. |
| `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | local project | Documented | Backtest file ownership, workflow boundary, registry/saved/run-history boundaries. | Durable doc | High | Last verified 2026-06-09. |
| `.aiworkspace/note/finance/docs/architecture/BACKTEST_RUNTIME_FLOW.md` | local project | Documented | Single/Compare/Saved replay/runtime/result bundle flow and 5A/5B metadata contracts. | Durable architecture doc | High | Does not prove UI appearance by itself. |
| `.aiworkspace/note/finance/docs/architecture/STRATEGY_IMPLEMENTATION_FLOW.md` | local project | Documented | Strategy family contracts, strict annual/quarterly/Risk-On notes, product checklist. | Durable architecture doc | High | Some future checklist items are guidance, not implemented facts. |
| `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` | local project | Documented | Backtest Analysis, Practical Validation, Final Review, Operations flow and boundaries. | Durable flow doc | High | Long file; this run read the relevant top/workflow sections. |
| `.aiworkspace/note/finance/tasks/active/backtest-analysis-direction-reset-20260609/STATUS.md` | local project | Documented | 4C reset demoted evidence/governance panels behind `전략 개발 참고`. | Task status | High | Completed task record, not current active task. |
| `.aiworkspace/note/finance/tasks/active/global-relative-strength-5a-20260609/STATUS.md` | local project | Documented | 5A GRS runtime/result bundle hardening and no new panel scope. | Task status | High | Completed task record. |
| `.aiworkspace/note/finance/tasks/active/risk-parity-dual-momentum-5b-20260610/STATUS.md` | local project | Documented | 5B Risk Parity / Dual Momentum runtime/result bundle hardening and no new panel scope. | Task status | High | Completed task record. |
| `app/web/backtest_analysis.py` | local code | Observed | Backtest Analysis renders Single/Compare first and hides references behind checkbox. | Code | High | Does not replace Browser QA. |
| `app/services/backtest_analysis_research_board.py` | local code | Observed | 3A~4B panels classified as hidden-by-default, non-writing references. | Code | High | Describes placement policy, not user behavior. |
| `app/services/backtest_strategy_catalog.py` | local code | Observed | Current strategy catalog and strict annual/quarterly variant keys. | Code | High | Catalog support does not equal candidate readiness. |
| `app/services/backtest_strategy_evidence_inventory.py` | local code | Observed | Current maturity rows and first evidence-mature group. | Code | High | Existing implementation is source material, not necessarily final product direction. |
| `app/runtime/candidate_library.py` | local code | Observed | Candidate Library replay supports ETF + strict annual keys. | Code | High | Does not support quarterly/Risk-On candidate lifecycle by default. |
| `app/web/backtest_history_helpers.py` | local code | Observed | Quarterly prototype and Risk-On have deferred/research-lane interpretation in history/replay helpers. | Code | High | UI copy still needs Browser QA if changed. |
| `.aiworkspace/note/finance/researches/active/2026-06-backtest-strategy-direction/` | local project | Documented / Inferred | Prior internal maturity research and weakness matrix. | Research bundle | Medium | Pre-reset and narrower; used as source material, not copied as final answer. |

## Web Sources

| Title | URL | Publisher / Owner | Access Date | Evidence Label | Supports | Source Type | Confidence | Limitations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QuantConnect Research Environment: Backtest Analysis | https://www.quantconnect.com/docs/v2/research-environment/meta-analysis/backtest-analysis | QuantConnect | 2026-06-12 KST | Documented | Backtest results can be loaded into research environment for trade/raw-data analysis and comparison. | Official docs | High | Does not show authenticated UI state. |
| QuantConnect Backtesting: Getting Started | https://www.quantconnect.com/docs/v2/cloud-platform/backtesting/getting-started | QuantConnect | 2026-06-12 KST | Documented | Project backtest run, backtest result history, filtering, renaming, sharing, OOS holdout. | Official docs | High | Platform-specific to QuantConnect. |
| QuantConnect Backtesting Report | https://www.quantconnect.com/docs/v2/cloud-platform/backtesting/report | QuantConnect | 2026-06-12 KST | Documented | Report statistics, turnover, drawdown, capacity, returns, rolling stats, exposure, crisis events. | Official docs | High | Report scope differs from this local product. |
| Portfolio Visualizer Backtest Portfolio | https://www.portfoliovisualizer.com/backtest-portfolio | Portfolio Visualizer | 2026-06-12 KST | Claimed / Documented | Construct one or more portfolios from selected mutual funds, ETFs, and stocks. | Official product page | Medium | Direct terminal fetch returned 403; used official search result snippet/page reference. |
| Portfolio Visualizer Analysis Tools | https://www.portfoliovisualizer.com/analysis | Portfolio Visualizer | 2026-06-12 KST | Claimed / Documented | Tool catalog including portfolio backtesting and risk/return comparison. | Official product page | Medium | Direct terminal fetch returned 403; no live UI inspection. |
| Portfolio123 Home | https://www.portfolio123.com/ | Portfolio123 | 2026-06-12 KST | Claimed | Ranking systems, buy/sell rules, screen backtesting, simulations, data coverage, manage/live areas. | Official product page | Medium | Marketing page; claims not independently verified. |
| Portfolio123 Tutorials | https://www.portfolio123.com/doc/tutorials.jsp | Portfolio123 | 2026-06-12 KST | Documented | Separate tutorials for simulated strategies, screen backtest, ranking, rolling tests, launch/live. | Official docs index | High | Index-level evidence, not full tutorial content. |
| Portfolio123 Blog: Fundamentals-Based Strategy Backtesting Principles | https://blog.portfolio123.com/how-to-design-a-fundamentals-based-strategy-that-really-works-part-three-principles-of-backtesting/ | Portfolio123 Blog | 2026-06-12 KST | Documented | Common backtesting mistakes, robustness, stress-testing, avoiding CAGR-only optimization. | Official blog | Medium | Blog guidance, not product feature documentation. |
| Koyfin Model Portfolios | https://www.koyfin.com/features/model-portfolios/ | Koyfin | 2026-06-12 KST | Claimed | Model portfolio performance, risk, allocation, drift, sleeves, benchmark comparison, reports. | Official product page | Medium | Marketing page; useful for pattern, not verified feature QA. |
| Koyfin ETF Holdings, Constituents & Contribution Function | https://www.koyfin.com/help/etf-holdings-constituents-and-contribution/ | Koyfin Help | 2026-06-12 KST | Documented | ETF contribution calculation caveats around estimated weights, current constituents, delistings/acquisitions. | Official help doc | High | Koyfin-specific methodology. |
| IBKR PortfolioAnalyst Overview | https://www.interactivebrokers.com/en/portfolioanalyst/overview.php | Interactive Brokers | 2026-06-12 KST | Claimed / Documented | Consolidated portfolio analysis by asset class/sector/instrument/region, concentration and risk metrics. | Official product page | Medium | Product page; no live account inspection. |
| IBKR PortfolioAnalyst Features | https://www.interactivebrokers.com/en/portfolioanalyst/features.php | Interactive Brokers | 2026-06-12 KST | Claimed / Documented | Reports, holdings, allocation, performance, attribution vs benchmark, risk measures, custom reporting. | Official product page | Medium | Product page; no live account inspection. |
| IBKR Traders' Academy: PortfolioAnalyst Reports | https://www.interactivebrokers.com/campus/trading-lessons/portfolioanalyst-reports/ | Interactive Brokers Campus | 2026-06-12 KST | Documented | Report workflow, default/custom reports, saved custom report, benchmark selection, rerun/edit/delete. | Official education docs | High | Tutorial page, not direct application test. |

## Source Notes

- External product, pricing, and UI details are volatile. Treat this benchmark as access-date-specific.
- Product marketing pages are used as feature-pattern evidence, not proof of technical behavior.
- The local branch had pre-existing dirty `docs/ROADMAP.md`, `tasks/active/STATUS_MANIFEST.md`, and untracked run history before this research. This bundle did not edit those files.
- Web benchmark evidence is deliberately small. The goal is workflow pattern extraction, not a comprehensive market survey.
