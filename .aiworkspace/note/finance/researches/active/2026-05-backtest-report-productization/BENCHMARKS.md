# Benchmarks

Evidence labels:

- `Observed`: 공식 화면/문서에서 직접 확인한 기능 또는 UI 구조
- `Documented`: 공식 문서/repository에 설명된 기능
- `Claimed`: 제품 마케팅 페이지의 주장
- `Inferred`: 여러 근거를 종합한 해석

## Benchmark Matrix

| Product / Library | Type | Evidence | Relevant pattern |
| --- | --- | --- | --- |
| QuantConnect Backtesting Results | Cloud quant platform | Observed / Documented | 결과 페이지에서 equity curve, trades, logs, statistics, reports, orders, downloads, shareable results를 분리한다. |
| QuantConnect Backtest Report | Cloud quant platform report | Documented | return, monthly heatmap, asset allocation, drawdown periods, rolling beta/Sharpe, exposure, crisis-period comparison을 report로 묶는다. |
| QuantRocket Moonshot | Python quant platform | Documented | backtest 결과를 CSV, PDF tear sheet, pyfolio tear sheet로 받을 수 있어 raw data와 report artifact를 분리한다. |
| TradingView Strategy Report | Retail/pro chart platform | Observed / Documented | Overview, Performance, Trades analysis, Risk/performance ratios처럼 report surface를 tab으로 나눈다. |
| QuantStats | Python analytics library | Documented | returns series에서 metrics, plots, basic/full report, HTML tear sheet를 생성한다. |
| pyfolio | Python analytics library | Documented | returns, positions, transactions 기반 tear sheet로 portfolio/risk analysis를 제공한다. |
| NautilusTrader Reports | Trading/backtesting framework | Documented | orders, fills, positions, account states를 structured DataFrame report로 변환한다. |
| Portfolio Backtest | Portfolio backtesting product | Claimed | 자연어 portfolio input, portfolio comparison, returns/volatility/Sharpe/drawdown analysis, shareable client/team insight를 강조한다. |

## Key Findings

### 1. Report는 결과 화면과 원자료의 중간 계층이다

QuantConnect와 QuantRocket 모두 결과 화면 또는 raw CSV만 제공하는 것이 아니라, 사람이 판단하기 쉬운 report/tear sheet를 별도 산출물로 둔다.

Implication for finance:

- `run_history`는 raw operational record로 남긴다.
- `reports/backtests`는 사람이 읽는 durable report로 남긴다.
- 그 사이에 `BacktestReportPack` 같은 structured read model이 필요하다.

### 2. 좋은 backtest report는 metric table만으로 끝나지 않는다

반복적으로 보이는 report 구성:

| Section | Common contents |
| --- | --- |
| Summary | return, risk, drawdown, benchmark spread, key status |
| Equity / returns | cumulative return, daily/monthly/yearly return |
| Risk | volatility, Sharpe, Sortino, drawdown, VaR/CVaR or tail risk |
| Benchmark | beta, alpha, information ratio, tracking error, buy-and-hold comparison |
| Exposure / allocation | holdings, sector/asset class exposure, leverage, turnover |
| Trades / orders | trade list, order/fill details, trade outcome analysis |
| Settings / properties | initial capital, period, commission, slippage, rebalance rule, universe |
| Logs / warnings | runtime logs, missing data, errors, limitations |
| Export/share | JSON/CSV/PDF/HTML/share URL |

Implication for finance:

- 현재 metric set은 충분한 시작점이지만 report product로는 더 넓은 metric/plot contract가 필요하다.
- 단, 1차 구현에서는 available field만 노출하고 missing metric은 limitation으로 표시하는 편이 안전하다.

### 3. UI는 "요약 먼저, 자세한 근거는 탭/섹션" 패턴이 강하다

TradingView와 QuantConnect 모두 결과를 한 화면에 무작정 나열하지 않고 overview와 detail을 분리한다.

Recommended finance report tabs:

```text
Overview
Performance
Risk & Drawdown
Benchmark
Inputs & Assumptions
Validation Evidence
Source & Warnings
```

### 4. Export와 share는 contract 안정화 이후가 맞다

QuantConnect의 download/share, QuantRocket의 CSV/PDF, QuantStats의 HTML report는 매력적이지만, 모두 report source object가 안정적이라는 전제가 있다.

Implication for finance:

- 첫 구현에서 PDF/HTML을 목표로 잡으면 scope가 커진다.
- 먼저 Markdown draft와 JSON-compatible report pack을 만들고, 그 다음 HTML/PDF를 검토한다.

### 5. AI/natural-language report는 매력적이지만 위험하다

Portfolio Backtest류 제품은 자연어 input과 shareable insight를 강조한다. 다만 finance 프로젝트는 evidence-first를 핵심 가치로 잡고 있으므로, AI narrative는 구조화된 evidence를 요약하는 수준으로 제한해야 한다.

Implication for finance:

- AI가 새로운 투자 결론을 생성하면 안 된다.
- AI가 report pack의 metric, warnings, validation state를 요약하는 것은 나중에 검토 가능하다.

## Benchmark-Informed Gaps

| Gap | Source pattern | Finance implication |
| --- | --- | --- |
| Report artifact contract | QuantRocket CSV/PDF/pyfolio, QuantStats HTML | `BacktestReportPack`를 먼저 만든다. |
| Share/reopen flow | QuantConnect share/download | stable report id와 source links가 필요하다. |
| Metric breadth | QuantConnect report, QuantStats stats | Sortino, Calmar, rolling, drawdown period, alpha/beta 등 확장 후보를 분리한다. |
| Report tab structure | TradingView strategy report | Overview/detail tab model로 viewer를 설계한다. |
| Raw vs summary separation | NautilusTrader report provider | raw orders/fills/positions와 summary report를 섞지 않는다. |
| Limitations visibility | QuantConnect logs/errors, finance validation rules | NOT_RUN, stale data, missing benchmark를 report에 고정 노출한다. |
