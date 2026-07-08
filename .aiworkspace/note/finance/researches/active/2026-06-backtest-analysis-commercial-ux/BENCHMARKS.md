# Benchmarks

Status: Active
Last Updated: 2026-06-29 KST

## Research Question

상용 백테스트 / 포트폴리오 분석 제품은 결과, 검증, 다음 행동, 상세 진단을 어떻게 배치하는가?
이 프로젝트의 Backtest Analysis는 어떤 pattern만 가져오고, 어떤 pattern은 현재 boundary 때문에 피해야 하는가?

## Selection Criteria

- 백테스트 결과 화면이 있거나, 포트폴리오 성과 / 리스크 분석을 다룬다.
- 공식 product page 또는 docs로 현재 기능을 확인할 수 있다.
- UI/workflow pattern이 Backtest Analysis 개선에 직접 참고된다.
- broker/live trading 연결이 있더라도 현재 프로젝트에 그대로 가져오지는 않는다.

## Benchmark Matrix

| Product | Category | Target User | Relevant Workflow | Evidence Label | Applicability |
|---|---|---|---|---|---|
| QuantConnect Backtest Results | Algo backtesting platform | Quant developer | result page with runtime stats, charts, key stats, orders/trades/logs/report/download | Documented | Result detail architecture and advanced tabs |
| TradingView Strategy Tester | Chart-based strategy testing | Trader / Pine user | Overview, Performance Summary, List of Trades, Properties tabs | Documented | Simple result hierarchy and trade/detail separation |
| Koyfin Model Portfolios | Portfolio analytics | Advisor / investment researcher | build model portfolio, compare benchmark, risk/exposure/returns snapshots | Documented | Summary-first portfolio analysis and drilldown |
| Interactive Brokers PortfolioAnalyst | Portfolio reporting | Investor / advisor | performance, concentration, risk, attribution, drilldown by asset/sector/region/time | Documented / Claimed | Monitoring/reporting pattern, not Backtest Analysis build flow |
| Portfolio123 | Quant strategy research | Stock strategy researcher | idea -> ranking system -> backtest / robustness -> launch / monitor | Claimed / Documented from public page | Strategy development sequence and robustness framing |
| Composer | Strategy/backtest product | Retail systematic investor | settings, fees/slippage, chart, benchmark, metrics, allocations, overfitting education | Documented | Compact assumptions / benchmark / overfitting checklist |
| testfol.io | Portfolio backtester | DIY portfolio researcher | compare portfolios, rebalancing, cashflows, drawdowns, rolling returns | Claimed from public page | Portfolio mix comparison pattern |

## Product Notes

### QuantConnect Backtest Results

- Category: algorithmic backtesting platform.
- Main workflow: deploy backtest, inspect result page, review runtime statistics, charts, key stats, reports, orders, trades, logs, project files, downloads.
- UI/workflow pattern:
  - result page opens around performance and investigation.
  - runtime stats live in a top banner.
  - orders/trades/logs are separate sections, not mixed into the summary.
  - report/download/share are secondary actions.
- Fit:
  - Backtest Analysis should show compact run stats first and move meta/log/detail into tabs/disclosures.
  - It supports removing top guide copy in favor of result-oriented navigation.
- Avoid:
  - QuantConnect also has live deployment concepts; current project should not copy live trading semantics.
- Sources: QuantConnect Backtesting Results docs.

### TradingView Strategy Tester

- Category: chart-based strategy testing.
- Main workflow: add strategy to chart, open Strategy Tester, inspect four result tabs.
- UI/workflow pattern:
  - Overview is the quick look.
  - Performance Summary is deeper metrics.
  - List of Trades is chronological detail.
  - Properties contains configuration / dataset details.
- Fit:
  - `Latest Backtest Run` can be simplified into `Overview / Performance / Selection or Trades / Properties` style tabs.
  - Backtest Data Trust belongs closer to Properties / assumptions than as a large repeated warning area, unless it is blocking.
- Avoid:
  - TradingView's chart/trade execution framing can imply trading action; keep Backtest Analysis as candidate source only.
- Sources: TradingView Pine Script strategies documentation and Strategy Tester help.

### Koyfin Model Portfolios

- Category: portfolio analytics / model portfolio workspace.
- Main workflow: create model portfolio, adjust target allocations / rebalancing / fees / currency, compare against benchmark, inspect snapshots.
- UI/workflow pattern:
  - summary snapshot first.
  - performance chart / rolling returns / historical returns / risk metrics / drawdown / holdings matrix are separate snapshots.
  - benchmark comparison and target allocation drift are first-class, but not mixed with raw setup instructions.
- Fit:
  - Portfolio Mix Builder should become a compact model-portfolio workbench: component list, weights, benchmark, risk/return summary, then drilldown.
  - Backtest result should show what changed and what needs review, not a manual.
- Avoid:
  - Advisor reporting / client-ready proposal features are later roadmap, not first Backtest Analysis cleanup.
- Sources: Koyfin Model Portfolios product page and help page.

### Interactive Brokers PortfolioAnalyst

- Category: portfolio reporting and monitoring.
- Main workflow: analyze consolidated portfolio performance, concentration, risk, asset/sector/region/time breakdowns, reports.
- UI/workflow pattern:
  - monitoring/reporting starts from portfolio performance and risk summary.
  - drilldown is available by dimension.
- Fit:
  - Useful for Operations / Portfolio Monitoring and Final Review reports.
  - For Backtest Analysis, only borrow the summary-first / drilldown-later pattern.
- Avoid:
  - Do not import account sync, broker order, or live portfolio semantics.
- Sources: IBKR PortfolioAnalyst overview and features pages.

### Portfolio123

- Category: stock strategy research and management.
- Main workflow from public page: start with investment idea, create/test ranking system, fine tune strategy, launch and monitor.
- UI/workflow pattern:
  - strategy creation has an explicit sequence.
  - ranking / rules / robustness are part of the strategy lifecycle.
- Fit:
  - Strict annual / factor strategies should show idea, ranking factors, validation readiness, and known weakness.
  - It supports separating strategy design from run result.
- Avoid:
  - Launch / broker order step is out of current product boundary.
- Sources: Portfolio123 public product page.

### Composer

- Category: retail systematic strategy / backtesting product.
- Main workflow: backtest settings, fees/slippage, chart, benchmarks, performance metrics, simulated returns, historical allocations, overfitting discussion.
- UI/workflow pattern:
  - assumptions and caution are integrated into the backtest concept, not giant generic help panels.
  - fees/slippage, benchmarks, allocations, and overfitting are important result context.
- Fit:
  - Backtest Analysis top should not teach everything, but result summary should expose assumptions and benchmark/data caveats compactly.
- Avoid:
  - Current project should not copy brokerage/autotrading framing.
- Sources: Composer backtest article.

### testfol.io

- Category: portfolio backtester.
- Main workflow: compare multiple portfolios, model rebalancing and cashflows, inspect drawdowns and rolling returns.
- UI/workflow pattern:
  - portfolio comparison is core, not an afterthought.
  - rebalancing and cashflow assumptions sit near setup.
- Fit:
  - Portfolio Mix Builder can use a compact multi-portfolio compare mental model.
- Evidence limits:
  - Public page content is thin in terminal extraction; use only broad pattern.

## Cross-Product Patterns

1. Results are not manuals.
   Product pages put instructions in docs/help, while result surfaces put metrics, charts, status, and next actions first.

2. Overview first, details second.
   QuantConnect, TradingView, Koyfin, and IBKR all separate summary from deep tables/logs/trades/properties.

3. Assumptions belong near the artifact they qualify.
   TradingView has Properties, Composer calls out settings/fees/slippage/overfitting, Koyfin shows benchmark/rebalancing/fees at portfolio level.

4. Drilldown is tabbed or snapshot-based.
   Detail is available, but not all visible at once.

5. Warnings should change the next action.
   If a warning does not change action, it should be a compact caveat or disclosure.

## Architecture / Platform Implications

- Keep Streamlit for current implementation if scope is cleanup; do not start platform migration inside this task.
- Create Streamlit-free read-model helpers for handoff eligibility and result summary so UI can be compact without hiding logic.
- Do not solve UX by adding more markdown guidance.
- Keep generated artifacts, registry writes, provider collection, and live trading outside this Backtest Analysis redesign.
