# Benchmarks

Evidence labels:

- `Observed`: official UI/docs directly show the pattern.
- `Documented`: official docs or repository describe the pattern.
- `Claimed`: product page or marketing copy claims the pattern.
- `Inferred`: synthesis from multiple supported facts.
- `Unknown`: evidence is missing or unclear.

## Benchmark Matrix

| Product / Service | Category | Evidence | Relevant pattern |
| --- | --- | --- | --- |
| QuantConnect Docs / Research Guide | Quant research platform | Documented | Hypothesis-first research guidance, overfitting warnings, research-to-backtest separation, in-page contents / Ask AI / related docs. |
| TradingView Strategy Report | Charting + strategy testing | Documented | Result report is split into Overview, Performance, Trades analysis, Risk/performance ratios, List of trades; metric definitions are separately indexed. |
| Koyfin Help Center / Model Portfolios / Dashboards | Market analytics + portfolio workspace | Documented | Searchable help center by task/category, reusable dashboards/views, model portfolio snapshots, exposure/performance/risk panels. |
| Interactive Brokers PortfolioAnalyst | Portfolio reporting / monitoring | Claimed + Documented | Dashboard widgets, allocation/performance/risk reports, planning tools, custom benchmarks, default/custom reports. |
| testfolio | Portfolio backtesting and analytics | Claimed | Portfolio backtester explains what users can model, what they can inspect, related tools, shareable links, and educational/no-advice boundary. |
| Composer Knowledge Center | Strategy builder / backtesting | Documented | Short workflow tutorials with related articles and user support handoff. Useful as a lower-complexity reference pattern. |

## Key Findings

### 1. Mature quant tools separate workflow guidance from result interpretation.

- QuantConnect explains research as a process before backtesting, including hypothesis discipline and overfitting risk.
- TradingView puts high-level strategy results in an Overview tab, then moves detailed metrics, trades, and risk ratios to dedicated tabs.
- Finance implication: `Reference > Guides` should not be one long page. It should separate "what task am I doing?" from "what does this metric/status mean?"

### 2. User-facing reference works best when it starts from intent.

- Koyfin's help center starts with categories like Getting Started, Functionality, Release Notes, How do I, FAQ.
- testfolio's landing copy distinguishes what the user can model, inspect, and run next.
- Finance implication: Reference should start with intent cards such as `데이터가 최신인지 확인`, `후보를 만들기`, `검증 결과 해석`, `모니터링 후보 다시 보기`, `문제 해결`.

### 3. Portfolio products repeatedly use reusable views, snapshots, and report boundaries.

- Koyfin emphasizes dashboards, reusable watchlist views, model portfolio snapshots, exposure, performance, risk metrics, drawdowns, and holdings matrix.
- IBKR PortfolioAnalyst emphasizes dashboard widgets, allocation goals, default/custom reports, consolidated reporting, and custom benchmarks.
- Finance implication: Reference should explicitly map durable records and reusable setups:
  `registries/*.jsonl`, `saved/*.jsonl`, DB tables, run history, generated artifacts.

### 4. Good financial UX makes assumptions and limits visible.

- QuantConnect warns against overfitting and recommends out-of-sample discipline.
- TradingView exposes buy-and-hold comparison, drawdown/run-up, long/short metrics, and trade lists.
- testfolio states educational/research purpose and no financial advice in its terms.
- Finance implication: Reference should repeatedly mark no-live-trading, no-order, no-auto-rebalance, context-only evidence, and `NOT_RUN` semantics.

### 5. Help content needs troubleshooting, not only happy-path docs.

- Koyfin includes FAQ and release-note style help; IBKR guide pages show navigation instructions and limitations.
- Composer's backtest tutorial links to basics and trading-cost articles, keeping adjacent explanations close.
- Finance implication: Reference should add compact playbooks for stale futures/Overview data, missing provider snapshots, blocked validation, stale portfolio scenario, and archive recovery.

## Benchmark-Informed Gaps

| Gap | Source pattern | Finance implication |
| --- | --- | --- |
| No top-level Reference Center | Koyfin Help Center categories; testfolio "model / inspect / related tools" split | Add a landing with task cards and search before the portfolio-selection guide. |
| Portfolio guide and glossary are disconnected | TradingView metric report + metric index | Cross-link status/metric terms from Guides to Glossary-like definitions. |
| Troubleshooting is not user-facing enough | Koyfin FAQ / release notes; IBKR limitations sections | Add "문제가 생겼을 때" playbooks with owner screen and stop criteria. |
| Storage boundaries are buried | IBKR reports / Koyfin snapshots distinguish reports, views, goals | Add a records/data source map for DB, registries, saved setups, run history, artifacts. |
| Current guide does not cover Overview/Ingestion/Operations | Koyfin dashboards and IBKR PortfolioAnalyst cover monitoring/reporting surfaces | Add journeys for market context, data refresh, system/data health, and monitoring. |
| Static single-file content is hard to govern | QuantConnect docs have contents/sections/related docs | Split content into structured guide catalog + render layer, then update canonical docs. |
