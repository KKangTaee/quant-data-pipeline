# Benchmarks

Status: Draft
Last Updated: 2026-06-08

Evidence labels:

- `Observed`: official UI/docs directly show the pattern.
- `Documented`: official docs or repository describe the pattern.
- `Claimed`: product page or marketing copy claims the pattern.
- `Inferred`: synthesis from multiple supported facts.
- `Unknown`: evidence is missing or unclear.

## Research Question

현재 finance 프로젝트의 `Backtest -> Practical Validation -> Final Review -> Selected Dashboard` 흐름을 실전 투자 판단 도구로 강화하려면, 상용 / 실서비스가 제공하는 어떤 workflow, data, validation, reporting pattern을 참고해야 하는가?

## Selection Criteria

이번 benchmark는 "라이브 주문 기능을 붙일 것인가"가 아니라 "실전 투자 가능성 판단을 더 엄격하게 만들 것인가"에 초점을 둔다. 그래서 아래 다섯 종류를 섞었다.

- quant research / backtesting platform
- institutional portfolio risk / attribution
- fund / ETF look-through analysis
- personal / broker-adjacent portfolio monitoring
- forward-looking portfolio construction / simulation

## Benchmark Matrix

| Product / Service | Category | Target user | Relevant workflow | Evidence label | Applicability |
| --- | --- | --- | --- | --- | --- |
| QuantConnect / LEAN | Quant research, backtesting, optimization, live deployment platform | Quant developers and systematic investors | Research notebook -> backtest / optimize -> deploy locally or cloud | Documented | Reproducible experiment contract, engine boundary, data library, optimization workflow |
| Bloomberg PORT | Institutional portfolio risk and performance analytics | Asset managers, hedge funds, family offices, banks, wealth teams | Positions + data validation -> risk / attribution -> stress scenarios -> reporting | Claimed / Documented | Data validation service, multi-asset risk, scenario families, batch reporting |
| Morningstar Portfolio X-Ray | Portfolio look-through and fund analysis | Individual investors, advisors | Holdings look-through -> allocation / sector / style / fees / top holdings | Documented | ETF/fund look-through, overlap, cost, diversification interpretation |
| Interactive Brokers PortfolioAnalyst | Broker-adjacent portfolio monitoring and reporting | IBKR clients, sophisticated investors, advisors | Consolidated accounts -> TWR/MWR, risk, benchmark, attribution, allocation goals | Documented | Selected portfolio monitoring, benchmark consistency, drift / allocation goals |
| Portfolio Lab | Portfolio construction, optimization, Monte Carlo and forward assumptions | Self-directed investors, advisors, FIRE planners, students | Optimize -> simulate -> backtest -> market dashboard / report | Claimed | Monte Carlo, forward-looking assumptions, explanation-first tool flow |

## Product Notes

### QuantConnect / LEAN

- Category: algorithmic trading research / backtesting platform.
- Target user: developers and quant researchers.
- Main workflow: research, algorithm writing, backtesting, optimization, live deployment through LEAN / CLI / cloud.
- Relevant features: Python / C# support, local and cloud development, Jupyter research environment, backtesting, optimization, live trading API.
- UI/workflow patterns: research and production are connected but separated by explicit deployment paths.
- Data/evidence model: product docs emphasize a preformatted data repository and LEAN engine abstraction.
- Strong ideas for this project:
  - turn every backtest candidate into a reproducible experiment contract with engine version, data snapshot, strategy params, benchmark, rebalance policy, cost assumptions, warnings, and run provenance.
  - separate exploratory backtests from promotion-grade validation runs.
  - treat optimization as a controlled step with overfit warnings, not as "best result wins".
- Ideas to avoid:
  - live trading deployment is outside current product boundary.
- Evidence label: Documented.
- Evidence limits: official docs show platform capabilities, not an audited comparison of result correctness.
- Sources:
  - https://www.quantconnect.com/docs/v2/

### Bloomberg PORT

- Category: institutional portfolio risk, attribution, construction, and reporting analytics.
- Target user: asset managers, hedge funds, banks, family offices, wealth management teams.
- Main workflow: positions and data -> unified risk / performance analytics -> attribution / scenario analysis -> reports.
- Relevant features: risk and attribution models, cross-asset coverage, data validation service, scenario analysis, portfolio reporting, orchestration.
- UI/workflow patterns: portfolio risk is not a single score; it is attribution, exposure, stress, data quality, and reporting in one workflow.
- Data/evidence model: product page emphasizes data validation, aligned data, Bloomberg + third-party data, and transparent insights across teams.
- Strong ideas for this project:
  - create a `Data Validation Gate` before Practical Validation can be considered complete.
  - make stress tests scenario families, not only static event rows.
  - produce a repeatable final review report that can be regenerated from stored evidence.
- Ideas to avoid:
  - institutional-scale multi-asset modeling and full PORT-like orchestration would be too broad for the current codebase.
- Evidence label: Claimed / Documented.
- Evidence limits: public product page is marketing-oriented; detailed model methodology is not fully inspectable.
- Sources:
  - https://professional.bloomberg.com/products/bloomberg-terminal/portfolio-analytics/

### Morningstar Portfolio X-Ray

- Category: portfolio look-through and fund exposure analysis.
- Target user: self-directed investors and advisors.
- Main workflow: portfolio holdings -> asset allocation, sector, region, style, fees, stock intersection, top holdings.
- Relevant features: underlying holdings analysis, stock overlap, asset class / sector / region / style breakdown, expense view, top holdings.
- UI/workflow patterns: a portfolio is explained by what it truly owns, not just ticker weights.
- Data/evidence model: Morningstar uses fund / ETF holdings data and warns that information may reflect the latest available composition, not necessarily current composition.
- Strong ideas for this project:
  - make ETF look-through coverage a first-class gate.
  - show top holdings overlap, sector / country / asset-class concentration, and expense ratio before Final Review selection.
  - clearly label current snapshot limits.
- Ideas to avoid:
  - copying a proprietary X-Ray UI; use the concept of look-through interpretation instead.
- Evidence label: Documented.
- Evidence limits: public samples show report concepts, not full licensed data coverage.
- Sources:
  - https://portfolio.morningstar.com/rtport/reg/xray_landingpage.aspx
  - https://advisor.morningstar.com/enterprise/reports/xray.pdf

### Interactive Brokers PortfolioAnalyst

- Category: broker-adjacent portfolio monitoring and reporting.
- Target user: investors and advisors who want consolidated performance / risk reporting.
- Main workflow: linked accounts -> performance, allocation, risk, benchmark comparison, attribution, reports.
- Relevant features: TWR / MWR, daily/monthly/quarterly periods, risk measures, custom benchmarks, performance attribution, allocation goals, external accounts, report library.
- UI/workflow patterns: monitoring is continuous and benchmarked; attribution and allocation goals explain performance after selection.
- Data/evidence model: account / external account consolidation, benchmarks, reports; official disclosures warn that data can be delayed or incomplete and that outputs are informational.
- Strong ideas for this project:
  - selected portfolio monitoring should store review snapshots, not only display current recheck.
  - track target vs current allocation, benchmark-relative performance, risk measure changes, and review triggers.
  - support custom benchmark / benchmark policy per selected strategy.
- Ideas to avoid:
  - broker account linking and order execution remain outside current boundary.
- Evidence label: Documented.
- Evidence limits: official public pages describe product features but not all internal calculations.
- Sources:
  - https://www.interactivebrokers.co.uk/en/trading/pa-standalone-splash.php
  - https://www.interactivebrokers.com/en/portfolioanalyst/features.php
  - https://www.interactivebrokers.com/en/software/pa-checkup.php

### Portfolio Lab

- Category: portfolio construction, optimization, Monte Carlo, and forward-looking assumption tool.
- Target user: serious self-directed investors, advisors, FIRE planners, students.
- Main workflow: optimization -> simulation -> retirement / backtest / dashboard / report.
- Relevant features: optimization methods, Monte Carlo paths, historical backtesting, factor exposure, capital market assumptions, PDF reports, saved portfolios.
- UI/workflow patterns: historical backtest is complemented by forward-looking assumptions and Monte Carlo simulation.
- Data/evidence model: product page claims use of 2026 J.P. Morgan long-term capital market assumptions and browser-side calculations.
- Strong ideas for this project:
  - add forward-looking scenario assumptions separate from historical backtests.
  - expose methodology and assumptions near the output, not hidden in code.
  - make PDF / report output a first-class artifact for final decisions.
- Ideas to avoid:
  - using forward assumptions as prediction; they should be scenario inputs with clear limitations.
- Evidence label: Claimed.
- Evidence limits: product page claims were not independently verified in this run.
- Sources:
  - https://www.portfoliolab.app/

## Backtesting And Regulatory Context

| Source | Pattern | Implication |
| --- | --- | --- |
| CFA Institute backtesting / simulation reading | Backtesting should be supplemented by scenario analysis, simulation, sensitivity analysis; analysts must watch survivorship and look-ahead bias. | Practical Validation should require a robustness protocol beyond one historical equity curve. |
| FINRA / SEC automated investment tools alert | Tools should disclose limitations, assumptions, and may not fit an individual situation. | Final Review should require assumption disclosure and operator acknowledgement. |
| FINRA projection guidance | Hypothetical illustrations need reasonable basis and material assumptions / limitations; hypothetical backtested performance is especially sensitive for retail communications. | UI copy and reports must avoid implying expected performance from backtest output. |
| FINRA leveraged / inverse ETF FAQ | leveraged / inverse ETFs have daily reset and can be unsuitable for longer horizons without close monitoring. | Leveraged / inverse ETF suitability diagnostic should be strict, not a soft warning. |
| NBER Novy-Marx multi-signal backtesting paper | combining many signals can create severe overfitting and multiple-testing bias. | Strategy comparison / factor strategy exploration needs experiment count and selection-bias controls. |

## Cross-Product Patterns

1. Reproducibility is a product feature.
   Serious tools make the data, assumptions, benchmark, cost, strategy rules, reporting period, and output artifact explicit enough to revisit.

2. Look-through matters more than ticker names.
   Morningstar and IBKR-style workflows look inside funds / ETFs to explain asset class, sector, region, cost, and concentration.

3. Backtest is one evidence source, not the final answer.
   Backtesting is supplemented with stress, Monte Carlo, sensitivity, attribution, benchmark parity, and explicit assumptions.

4. Monitoring is a lifecycle, not a screen.
   PortfolioAnalyst and PORT patterns imply repeated reports, benchmarks, allocation goals, and review cadence.

5. Missing data should be visible and decision-relevant.
   Data validation and disclosure patterns make stale / incomplete / hypothetical data part of the decision, not a hidden implementation detail.

## Benchmark-Informed Gaps

| Gap | Source pattern | Finance implication |
| --- | --- | --- |
| Missing investment decision packet | Bloomberg PORT reporting, Portfolio Lab reports, IBKR detailed reports | Final Review should produce a durable report-like packet with assumptions, evidence, gaps, and decision. |
| Weak look-through gate | Morningstar X-Ray, IBKR Fund Parser / Checkup | ETF holdings / exposure coverage should become mandatory for selection unless explicitly waived. |
| Insufficient robustness protocol | CFA backtesting / simulation, QuantConnect optimization, Portfolio Lab Monte Carlo | Add walk-forward, sensitivity, parameter stability, Monte Carlo / scenario assumptions as Practical Validation evidence. |
| Monitoring is not persistent enough | IBKR PortfolioAnalyst allocation goals / reports | Selected Dashboard should append monitoring snapshots and trigger states over time. |
| Data validation is scattered | Bloomberg Data Validation Service pattern | Add a visible data validation summary: price, provider, macro, benchmark, PIT, stale, missing. |
| Backtest claims can read too strongly | FINRA / SEC alerts and guidance | Reports and UI labels should emphasize hypothetical / decision-support status and unresolved assumptions. |

## Architecture / Platform Implications

- Keep Streamlit for internal ops surfaces until workflow is settled.
- Product-facing surfaces should converge around evidence packets and read models, not around ad hoc registry tables.
- The strongest next architecture move is not a broker integration; it is a stricter evidence model and report contract.
- A future API / React product surface would be easier after `Final Review Packet`, `Validation Gate`, and `Monitoring Snapshot` contracts exist.

## Open Questions

- Which user profile is primary: self-directed investor, quant researcher, advisor-style operator, or internal research assistant?
- Should `SELECT_FOR_PRACTICAL_PORTFOLIO` require zero critical `NOT_RUN`, or allow an explicit human waiver?
- What minimum paper observation duration is required before a candidate can be "selected"?
- Should current snapshot ETF data be acceptable for all ETF validation, or should validation require snapshot as-of records persisted per decision?

## 2026-06-08 Benchmark Refresh

Access date: 2026-06-08.

This refresh adds current official-source evidence for the `main-dev` product-direction session. It keeps the same benchmark question, but shifts the interpretation because the local product has already implemented much of the May `Investability Evidence Packet` / gate-hardening foundation.

### Updated Benchmark Set

| Product / service | Why included now | Useful pattern | Boundary note |
| --- | --- | --- | --- |
| QuantConnect / LEAN | Strategy research, backtesting, reports, walk-forward optimization | Treat research, backtest, optimization, report, and deployment as distinct lifecycle states | Use the research / robustness / report pattern, not live deployment |
| Portfolio123 | Factor ranking and simulation platform | Ranking-system contract, simulation assumptions, liquidity/slippage disclosure, universe exit handling | Good pattern for factor strategy governance and assumption disclosure |
| Composer | Retail no-code strategy builder with backtest and automated execution | Very explicit backtest-vs-live assumptions, cost/slippage settings, API separation of backtest/deploy/portfolio | Execution features conflict with this product boundary; use disclosure pattern only |
| Bloomberg PORT | Institutional portfolio risk / performance analytics | Unified positions, data validation, risk, attribution, scenario analysis, reporting | Use as direction for data validation and reporting, not as a full risk-model clone |
| Morningstar X-Ray | Portfolio look-through and exposure analysis | Holdings breakdown, benchmark-relative exposure, fees, sector/style/region interpretation | Use look-through pattern with local provider coverage limits |
| Koyfin Model Portfolios | Advisor-style model monitoring and reports | Drift analysis, benchmark comparison, sleeves, exposures, risk metrics, holdings matrix, reports | Strong fit for `Operations > Portfolio Monitoring` without broker execution |
| Interactive Brokers PortfolioAnalyst | Broker-adjacent monitoring / reporting | Consolidated performance, allocation/risk measures, benchmarks, reports | Use monitoring/report pattern; account linking remains out of scope |

### New Source Notes

#### QuantConnect / LEAN

- Official docs describe backtesting as simulating an algorithm on historical data and then measuring historical performance.
- QuantConnect reports include key statistics, returns, asset allocation, drawdown, rolling statistics, exposure, crisis events, and parameters.
- Walk-forward optimization is documented as periodically adjusting strategy parameters over a trailing window; the docs explicitly call out an optimization-frequency tradeoff between responsiveness and overfitting risk.

Applicability:

- This supports a future `Robustness Experiment Registry` and `Strategy Promotion Contract`.
- Every promoted strategy should carry parameters, data snapshot, benchmark, cost/slippage, rebalance policy, report period, crisis-window outcome, and run-set id.

Sources:

- https://www.quantconnect.com/docs/v2/cloud-platform/backtesting
- https://www.quantconnect.com/docs/v2/cloud-platform/backtesting/report
- https://www.quantconnect.com/docs/v2/writing-algorithms/optimization/walk-forward-optimization

#### Portfolio123

- Ranking systems explicitly define factors, formulas, weights, lower-is-better / higher-is-better direction, and rank-within-universe behavior.
- Simulation assumptions disclose that performance is model-based and historical, not predictive; they also define assumed trade timing, liquidity-based slippage, split / dividend handling, universe exits, and cash return assumptions.

Applicability:

- This is a strong pattern for `backtest-dev -> main product` handoff: a strategy is not just a name and CAGR, but a ranking/selection contract with explicit assumptions.
- It also supports making local strategy reports show transaction timing, liquidity/slippage, universe exit, and cash assumptions beside results.

Sources:

- https://portfolio123.customerly.help/en/articles/13611-ranking-system
- https://portfolio123.customerly.help/en/articles/13753-simulation-assumptions

#### Composer

- Composer's help center is unusually clear that backtests are hypothetical, benefit from hindsight, are not recommendations, and may differ from live trading because live decisions use real-time quotes.
- It exposes cost assumptions such as regulatory fees, default slippage, and optional subscription cost modeling.
- Its API separates account/portfolio data, symphonies, backtests, deploy actions, dry runs, and direct trading.

Applicability:

- Strong pattern for local assumption disclosure and "backtest output is not execution authority."
- Weak fit for implementation because Composer's automated deployment, rebalancing, direct trading, and account features conflict with the current no-live-trading boundary.

Sources:

- https://help.composer.trade/article/67-backtest-basics
- https://api.composer.trade/docs/index.html

#### Bloomberg PORT

- Public Bloomberg PORT material emphasizes unifying positions, risk, performance, data validation, attribution, scenario analysis, optimization, and reporting.
- It also mentions factor-based, full-valuation, macroeconomic, and climate scenario-analysis families.

Applicability:

- Supports a product direction where data validation and scenario families sit above individual evidence rows.
- Useful benchmark for a durable `Decision Dossier` / reporting artifact generated from existing evidence.

Source:

- https://professional.bloomberg.com/products/bloomberg-terminal/portfolio-analytics/

#### Morningstar X-Ray

- X-Ray explains a portfolio by underlying holdings and benchmark-relative breakdowns: asset class, world region, sector, fees, stock stats, style boxes, and stock intersection.

Applicability:

- Supports treating provider look-through as a core Practical Validation / Final Review requirement.
- Local limitation remains provider coverage and current-snapshot semantics, so missing / stale / partial holdings must stay decision-relevant.

Source:

- https://www.morningstar.com/help-center/portfolio/xray

#### Koyfin Model Portfolios

- Koyfin model portfolios emphasize key stats, holdings visualization, target-drift monitoring, benchmark comparison, rolling returns, sleeves, long/short and leveraged positions, exposure breakdowns, historical returns, risk metrics, holdings matrix, and custom reports.
- Their help page also describes benchmark settings, rebalancing frequency, custom allocation dates, and handling securities that start trading after the portfolio start date.

Applicability:

- Strongest benchmark for `Operations > Portfolio Monitoring`.
- Supports a future monitoring snapshot and drift/review loop without account linking.

Sources:

- https://www.koyfin.com/features/model-portfolios/
- https://www.koyfin.com/help/model-portfolios/

### 2026-06-08 Cross-Product Patterns

1. `Strategy contract before performance`: QuantConnect, Portfolio123, and Composer all make assumptions / parameters / data source boundaries part of the backtest story.
2. `Robustness is lifecycle evidence`: reports, walk-forward optimization, crisis events, rolling returns, and scenario testing are separate from a single headline CAGR.
3. `Look-through and exposure explain the portfolio`: Morningstar and Koyfin show that ticker weights are insufficient for ETF / fund portfolios.
4. `Monitoring needs drift and report artifacts`: Koyfin, Bloomberg, and IBKR patterns point to repeated snapshot/report workflows rather than session-only dashboards.
5. `Execution must stay separate`: Composer and IBKR show how quickly monitoring can become trading; this project should keep broker/order/account sync out of scope unless explicitly approved later.

### Updated Benchmark-Informed Gaps

| Gap after 2026-06-08 audit | Benchmark pattern | Local implication |
| --- | --- | --- |
| Strategy research handoff is informal | QuantConnect lifecycle, Portfolio123 ranking contract | Create a strategy promotion checklist for backtest-dev outputs before they enter Practical Validation / Final Review governance. |
| Monitoring scenario is session-first | Koyfin drift monitoring, IBKR / Bloomberg reporting | Add explicit monitoring snapshot records with benchmark, drift, provider freshness, review trigger, operator note. |
| Robustness has evidence rows but no run-set registry | QuantConnect walk-forward / report parameters, Portfolio123 assumptions | Introduce robustness run-set ids and assumption metadata before expanding Robustness Lab. |
| Look-through is useful but provider-limited | Morningstar / Koyfin holdings and exposure views | Keep local provider coverage strict: partial / stale / missing remains blocker or review item, not a silent pass. |
| Legacy archive tools still visually compete | Institutional workflows separate production, archive, and report artifacts | Keep Run History / Candidate Library as archive / recovery; do not present them as primary selection stages. |
