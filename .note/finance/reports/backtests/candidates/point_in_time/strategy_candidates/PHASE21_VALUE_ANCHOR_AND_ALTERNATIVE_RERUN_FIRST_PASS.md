# Phase 21 Value Anchor And Alternative Rerun First Pass

## 목적

- `Value > Strict Annual` current anchor와 lower-MDD alternative를
  `Phase 21` 공통 validation frame에서 다시 돌린다.
- 지금 기준에서
  - current anchor를 그대로 유지하는지
  - lower-MDD alternative가 실제 rescue candidate로 올라오는지
  를 다시 확인한다.

## 이번 rerun에서 사용한 공통 frame

- `2016-01-01 ~ 2026-04-01`
- `US Statement Coverage 100`
- `Historical Dynamic PIT Universe`
- `Option = month_end`
- `Rebalance Interval = 1`
- `Minimum Price = 5.0`
- `Minimum History = 12M`
- `Min Avg Dollar Volume 20D = 5.0M`
- `Transaction Cost = 10 bps`
- `Benchmark Contract = Ticker Benchmark`
- `Benchmark Ticker = SPY`
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
  - `Top N = 14 + psr`
- factor:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `ocf_yield`
  - `operating_income_yield`
  - `psr`
- overlay:
  - `Trend Filter = off`
  - `Market Regime = off`

### 2. lower-MDD alternative

- label:
  - `Top N = 14 + psr + pfcr`
- factor:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `ocf_yield`
  - `operating_income_yield`
  - `psr`
  - `pfcr`
- overlay:
  - `Trend Filter = off`
  - `Market Regime = off`

## 결과 요약

| label | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
|---|---:|---:|---|---|---|---|---|---|
| `Top N = 14 + psr` | `28.13%` | `-24.55%` | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `watch` | `caution` |
| `Top N = 14 + psr + pfcr` | `27.22%` | `-21.16%` | `production_candidate` | `watchlist` | `review_required` | `watch` | `caution` | `caution` |

## 세부 해석

### 1. current anchor

- `CAGR = 28.13%`
- `MDD = -24.55%`
- `Promotion = real_money_candidate`
- `Shortlist = paper_probation`
- `Deployment = review_required`
- `Validation / Benchmark / Liquidity / Guardrail Policy = normal / normal / normal / normal`
- `Rolling Review = watch`
- `Out-of-Sample Review = caution`

추가 체크:

- `Benchmark Coverage = 100%`
- `Liquidity Clean Coverage = 100%`
- `Worst Rolling Excess Return = -6.06%`
- `Drawdown Gap vs Benchmark = -0.25%p`

해석:

- current anchor는 `Phase 21` validation frame에서도
  그대로 current best practical point로 유지된다.
- benchmark, liquidity, guardrail contract 쪽에서
  새로 무너지는 부분은 보이지 않았다.

### 2. lower-MDD alternative

- `CAGR = 27.22%`
- `MDD = -21.16%`
- `Promotion = production_candidate`
- `Shortlist = watchlist`
- `Deployment = review_required`
- `Validation = watch`
- `Validation / Benchmark / Liquidity / Guardrail Policy = normal / normal / normal / normal`
- `Rolling Review = caution`
- `Out-of-Sample Review = caution`

추가 체크:

- `Benchmark Coverage = 100%`
- `Liquidity Clean Coverage = 100%`
- `Worst Rolling Excess Return = -10.59%`
- `Drawdown Gap vs Benchmark = -3.64%p`

해석:

- lower-MDD alternative는 이번 frame에서도
  여전히 더 낮은 drawdown을 보여준다.
- 하지만 gate는 여전히 한 단계 약하다.
- 특히:
  - `Promotion = production_candidate`
  - `Shortlist = watchlist`
  - `Validation = watch`
  - `Rolling Review = caution`
  로 남아서,
  current anchor를 실제로 교체하는 rescue candidate까지는 아니다.

## 이번 first pass 결론

1. `Value` current anchor는 current code에서도 그대로 유지된다
2. `+ pfcr` alternative는
   여전히 lower-MDD alternative로는 의미가 있다
3. 하지만 same-gate replacement나 actual rescue까지는 아니다

즉 지금 읽는 것이 맞다:

- current practical anchor:
  - `Top N = 14 + psr`
- lower-MDD but weaker-gate alternative:
  - `Top N = 14 + psr + pfcr`

## 다음 액션

- `Quality` rerun pack을 같은 frame에서 실행
- 그 다음 `Quality + Value` rerun pack을 실행
- 이후 portfolio bridge validation까지 묶어
  `Phase 21` integrated comparison을 이어간다

## 같이 보면 좋은 문서

- [PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phases/phase21/PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md)
- [VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL.md)
- [VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
- [CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md)
