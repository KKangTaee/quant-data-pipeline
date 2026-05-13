# UI And Report Patterns

## Product Goal

백테스트 리포트 화면의 목표는 "수익률이 좋다/나쁘다"를 빠르게 보여주는 것이 아니라, 사용자가 전략 후보를 다시 판단할 수 있게 만드는 것이다.

좋은 리포트는 다음 질문에 답해야 한다.

| User question | Report answer |
| --- | --- |
| 이 전략은 무엇인가? | name, universe, period, inputs, rebalance rule |
| 성과는 어땠는가? | CAGR, Sharpe, drawdown, volatility, benchmark comparison |
| 위험은 어디서 나왔는가? | drawdown periods, rolling risk, exposure, concentration |
| 믿을 수 있는가? | data trust, validation status, warnings, missing evidence |
| 왜 선택/보류/탈락했는가? | Final Review decision, reason, follow-up |
| 다시 확인하려면 어디를 보면 되는가? | source run, registry row, report path, validation artifact |

## Recommended Report Structure

```text
Backtest Strategy Report
  1. Overview
  2. Performance
  3. Risk & Drawdown
  4. Benchmark
  5. Inputs & Assumptions
  6. Validation Evidence
  7. Source, Warnings, Next Action
```

## Pattern 1. Executive Summary First

첫 화면은 metric wall이 아니라 판단 요약이어야 한다.

Recommended summary cards:

| Card | Content |
| --- | --- |
| Return | CAGR, total return, end balance |
| Risk | max drawdown, volatility, Sharpe |
| Benchmark | excess return, benchmark Sharpe, tracking caveat |
| Evidence status | validation pass/fail/not run, warning count |
| Decision | candidate status or final review decision |

Important:

- `NOT_RUN`은 pass로 보이면 안 된다.
- benchmark가 없으면 comparison card는 "not available"로 표시한다.
- stale data나 period mismatch는 card 아래 warning으로 노출한다.

## Pattern 2. Evidence Before Narrative

리포트는 설명문보다 evidence table과 chart를 먼저 둔다.

Narrative는 다음 원칙을 따른다.

- metric에 없는 결론을 만들지 않는다.
- warning과 limitation을 숨기지 않는다.
- "투자 추천"이 아니라 "backtest evidence summary"로 표현한다.

## Pattern 3. Raw Source Links Are First-Class

각 report에는 source를 되짚을 수 있는 링크가 있어야 한다.

Recommended source fields:

```text
run_id
history_path
report_path
strategy_name
input_hash or input_summary
validation_id
decision_id
registry_refs
generated_at
generator_version
```

## Pattern 4. Tabs Separate Different Questions

One-page scrolling report보다 tab/section separation이 낫다.

Suggested tabs:

| Tab | Purpose |
| --- | --- |
| Overview | 가장 빠른 판단 |
| Performance | return curve, monthly/yearly returns, summary metrics |
| Risk | drawdown, volatility, rolling metrics, tail risk |
| Benchmark | strategy vs benchmark, beta/alpha if available |
| Inputs | universe, weights, fees, rebalance, data source |
| Evidence | Practical Validation / Final Review links |
| Source | logs, warnings, artifact paths, raw links |

## Pattern 5. Report Library Before Fancy Export

PDF export보다 먼저 필요한 것은 report library다.

Minimum report library:

- report id
- title
- strategy / portfolio name
- generated date
- period
- status
- key metrics
- warning count
- path/source links

This can start as Markdown index or Streamlit table. Later it can become a Next.js report library.

## Pattern 6. Contract-First Rendering

Renderer는 contract를 읽어야 한다.

```text
Backtest result bundle
  -> BacktestReportPack
      -> Markdown draft
      -> Streamlit report viewer
      -> Next.js report viewer
      -> HTML/PDF export
```

이 순서가 중요한 이유:

- report 내용을 표현 방식에 묶지 않는다.
- Markdown, Streamlit, Next.js가 같은 값을 보여줄 수 있다.
- report QA를 contract level에서 테스트할 수 있다.

## Pattern 7. Keep Ops Console Separate

내부 조사용 정보와 사용자 판단용 정보를 섞으면 리포트가 무거워진다.

Keep in internal console:

- raw run debug
- registry inspection
- provider/admin status
- generated artifact cleanup
- low-level execution logs

Expose in product report:

- compact source links
- warning summary
- reproducibility metadata
- user-facing limitations

## Pattern 8. No Live Approval Language

Backtest report는 broker order나 live approval이 아니다.

Avoid labels:

- approved for trade
- execute
- rebalance now
- production order

Use labels:

- selected for monitoring
- candidate passed review
- needs re-review
- insufficient evidence
- backtest evidence only
