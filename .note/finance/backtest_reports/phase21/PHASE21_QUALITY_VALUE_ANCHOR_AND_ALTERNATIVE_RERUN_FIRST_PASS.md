# Phase 21 Quality + Value Anchor And Alternative Rerun First Pass

## 목적

- `Quality + Value > Strict Annual` current strongest point와 lower-MDD alternative를
  `Phase 21` 공통 validation frame에서 다시 돌린다.
- 지금 기준에서
  - current strongest point를 그대로 유지하는지
  - `Top N = 9` alternative가 실제 replacement candidate로 올라오는지
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
- `Benchmark Contract = Candidate Universe Equal-Weight`
- `Benchmark Reference Ticker = SPY`
- `Trend Filter = off`
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

### 1. current strongest point

- label:
  - `operating_margin + pcr + por + per + Top N 10`
- quality factor:
  - `roe`
  - `roa`
  - `operating_margin`
  - `asset_turnover`
  - `current_ratio`
- value factor:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `pcr`
  - `por`
  - `per`
- `Top N = 10`

### 2. lower-MDD alternative

- label:
  - `same factor set + Top N 9`
- quality factor:
  - `roe`
  - `roa`
  - `operating_margin`
  - `asset_turnover`
  - `current_ratio`
- value factor:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `pcr`
  - `por`
  - `per`
- `Top N = 9`

## 결과 요약

| label | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
|---|---:|---:|---|---|---|---|---|---|
| `Top N 10 current strongest` | `31.82%` | `-26.63%` | `real_money_candidate` | `small_capital_trial` | `review_required` | `normal` | `normal` | `normal` |
| `Top N 9 lower-MDD alternative` | `32.21%` | `-25.61%` | `production_candidate` | `watchlist` | `review_required` | `watch` | `normal` | `normal` |

## 세부 해석

### 1. current strongest point

- `CAGR = 31.82%`
- `MDD = -26.63%`
- `Promotion = real_money_candidate`
- `Shortlist = small_capital_trial`
- `Deployment = review_required`
- `Validation / Benchmark / Liquidity / Guardrail Policy = normal / normal / normal / normal`
- `Rolling Review = normal`
- `Out-of-Sample Review = normal`

추가 체크:

- `Benchmark Coverage = 100%`
- `Liquidity Clean Coverage = 100%`
- `Worst Rolling Excess Return = -9.83%`
- `Drawdown Gap vs Benchmark = -6.82%p`

해석:

- current strongest point는 `Phase 21` validation frame에서도
  `real_money_candidate / small_capital_trial / review_required`를 유지한다.
- `Quality + Value` family의 representative anchor로 계속 쓰기에 충분하다.

### 2. lower-MDD alternative

- `CAGR = 32.21%`
- `MDD = -25.61%`
- `Promotion = production_candidate`
- `Shortlist = watchlist`
- `Deployment = review_required`
- `Validation = watch`
- `Validation / Benchmark / Liquidity / Guardrail Policy = normal / normal / normal / normal`
- `Rolling Review = normal`
- `Out-of-Sample Review = normal`

추가 체크:

- `Benchmark Coverage = 100%`
- `Liquidity Clean Coverage = 100%`
- `Worst Rolling Excess Return = -12.78%`
- `Drawdown Gap vs Benchmark = -7.84%p`

해석:

- `Top N = 9` alternative는 이번 frame에서
  current strongest point보다 `CAGR`도 높고 `MDD`도 낮다.
- 하지만 gate는 한 단계 약하다.
  - `Promotion = production_candidate`
  - `Shortlist = watchlist`
  - `Validation = watch`
- 따라서 숫자만 보면 매우 매력적이지만,
  current representative anchor를 바로 대체하는 후보로 읽기에는 아직 gate가 약하다.

## 이번 first pass 결론

1. `Quality + Value` current strongest point는 current code에서도 그대로 유지된다
2. `Top N = 9` alternative는 숫자상 매우 좋은 lower-MDD alternative다
3. 하지만 `small_capital_trial` gate를 유지하지 못해서 actual replacement는 아니다

즉 지금 읽는 것이 맞다:

- current representative anchor:
  - `Top N 10 current strongest`
- lower-MDD but weaker-gate alternative:
  - `Top N 9`

## 다음 액션

- representative portfolio bridge validation으로 이어간다
- `Load Recommended Candidates -> near-equal weighted bundle -> saved portfolio replay`
  흐름이 single-family validation 결과와 같이 읽힐 수 있는지 확인한다

## 같이 보면 좋은 문서

- [PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phases/phase21/PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md)
- [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
- [QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
- [CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md)
