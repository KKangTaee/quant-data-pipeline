# Phase 21 Quality Anchor And Alternative Rerun First Pass

## 목적

- `Quality > Strict Annual` current anchor와 cleaner alternative를
  `Phase 21` 공통 validation frame에서 다시 돌린다.
- 지금 기준에서
  - current anchor를 그대로 유지하는지
  - cleaner alternative가 실제 replacement candidate로 올라오는지
  를 다시 확인한다.

## 이번 rerun에서 사용한 공통 frame

- `2016-01-01 ~ 2026-04-01`
- `US Statement Coverage 100`
- `Historical Dynamic PIT Universe`
- `Option = month_end`
- `Top N = 12`
- `Rebalance Interval = 1`
- `Minimum Price = 5.0`
- `Minimum History = 12M`
- `Min Avg Dollar Volume 20D = 5.0M`
- `Transaction Cost = 10 bps`
- `Benchmark Contract = Ticker Benchmark`
- `Trend Filter = on`
- `Market Regime = off`
- underperformance guardrail:
  - `on`
  - `12M`
  - `-10%`
- drawdown guardrail:
  - `on`
  - `12M`
  - strategy threshold `-35%`
  - gap threshold `8%`

## 다시 본 후보

### 1. current anchor

- label:
  - `capital_discipline + LQD + trend on + regime off + Top N 12`
- factor:
  - `roe`
  - `roa`
  - `cash_ratio`
  - `debt_to_assets`
- benchmark:
  - `LQD`

### 2. cleaner alternative

- label:
  - `capital_discipline + SPY + trend on + regime off + Top N 12`
- factor:
  - `roe`
  - `roa`
  - `cash_ratio`
  - `debt_to_assets`
- benchmark:
  - `SPY`

## 결과 요약

| label | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
|---|---:|---:|---|---|---|---|---|---|
| `LQD + trend on + Top N 12` | `26.02%` | `-25.57%` | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `watch` | `normal` |
| `SPY + trend on + Top N 12` | `25.18%` | `-25.57%` | `real_money_candidate` | `paper_probation` | `paper_only` | `normal` | `normal` | `normal` |

## 세부 해석

### 1. current anchor

- `CAGR = 26.02%`
- `MDD = -25.57%`
- `Promotion = real_money_candidate`
- `Shortlist = paper_probation`
- `Deployment = review_required`
- `Validation / Benchmark / Liquidity / Guardrail Policy = normal / normal / normal / normal`
- `Rolling Review = watch`
- `Out-of-Sample Review = normal`

추가 체크:

- `Benchmark Coverage = 100%`
- `Liquidity Clean Coverage = 99.19%`
- `Worst Rolling Excess Return = -7.76%`
- `Drawdown Gap vs Benchmark = -2.82%p`

해석:

- current anchor는 `Phase 21` validation frame에서도
  그대로 `Quality` current best practical point로 유지된다.
- strongest raw winner는 아니지만,
  quality-only family를 실전형으로 다시 살리는 reference point라는 해석은 흔들리지 않았다.

### 2. cleaner alternative

- `CAGR = 25.18%`
- `MDD = -25.57%`
- `Promotion = real_money_candidate`
- `Shortlist = paper_probation`
- `Deployment = paper_only`
- `Validation / Benchmark / Liquidity / Guardrail Policy = normal / normal / normal / normal`
- `Rolling Review = normal`
- `Out-of-Sample Review = normal`

추가 체크:

- `Benchmark Coverage = 100%`
- `Liquidity Clean Coverage = 99.19%`
- `Worst Rolling Excess Return = -7.38%`
- `Drawdown Gap vs Benchmark = +0.77%p`

해석:

- cleaner alternative는 이번 frame에서도
  validation surface가 더 매끄럽게 읽히는 장점이 유지된다.
- 다만:
  - `CAGR`가 current anchor보다 낮고
  - `Deployment = paper_only`
  로 남기 때문에,
  current anchor를 대체하는 replacement candidate는 아니다.
- 따라서 이 조합은
  `readability / comparison surface` 용도로는 계속 의미가 있지만,
  current practical anchor를 바꿀 정도의 evidence는 아니다.

## 이번 first pass 결론

1. `Quality` current anchor는 current code에서도 그대로 유지된다
2. `SPY` cleaner alternative는 여전히 비교용 대안으로는 의미가 있다
3. 하지만 actual replacement나 rescue candidate까지는 아니다

즉 지금 읽는 것이 맞다:

- current practical anchor:
  - `capital_discipline + LQD + trend on + regime off + Top N 12`
- cleaner comparison alternative:
  - `capital_discipline + SPY + trend on + regime off + Top N 12`

## 다음 액션

- `Quality + Value` rerun pack을 같은 frame에서 실행
- 그 다음 portfolio bridge validation까지 묶어
  `Phase 21` integrated comparison을 이어간다

## 같이 보면 좋은 문서

- [PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phases/phase21/PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md)
- [QUALITY_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL.md)
- [QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md)
- [CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md)
