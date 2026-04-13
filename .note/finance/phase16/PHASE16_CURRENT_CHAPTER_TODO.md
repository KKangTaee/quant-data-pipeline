# Phase 16 Current Chapter TODO

## 목표

- `Value > Strict Annual`과 `Quality + Value > Strict Annual`의
  current practical candidate를 유지하면서
  `MDD`를 더 낮추거나, 같은 gate를 유지한 채
  더 좋은 return / drawdown tradeoff를 찾는다.
- blanket gate relaxation보다
  bounded `Top N`, one-factor addition / replacement,
  minimal benchmark / overlay sensitivity를 우선한다.

## 상태

- `practical closeout / manual_validation_pending`

## Workstream A. Value

### 기준점

- family: `Value`
- variant: `Strict Annual`
- current best practical point:
  - `Top N = 14 + psr`
  - `CAGR = 28.13%`
  - `MDD = -24.55%`
  - `real_money_candidate / paper_probation / review_required`

### 완료한 작업

- [x] bounded downside refinement first pass
  - `Top N = 12 / 13 / 14 / 15 / 16 / 18`
  - one-factor addition / replacement
- [x] lower-MDD rescue second pass
  - `+ pfcr`
  - `Top N = 14 / 15`
  - `Candidate Universe Equal-Weight`
  - `Trend Filter`
  - `Market Regime`
  - `sales_yield -> pfcr`

### 최종 결론

- current best practical point는 그대로 유지된다
- strongest lower-MDD near-miss:
  - `Top N = 14 + psr + pfcr`
  - `CAGR = 27.22%`
  - `MDD = -21.16%`
  - `production_candidate / watchlist / review_required`
- same-gate but no rescue:
  - `Top N = 15 + psr + pfcr`
  - `CAGR = 25.95%`
  - `MDD = -27.59%`
  - `real_money_candidate / paper_probation / review_required`

쉬운 뜻:

- `Value`는 여전히 강한 family다
- 하지만 이번 bounded 범위 안에서는
  gate를 유지하면서 더 낮은 `MDD`를 만드는 exact rescue는 없었다

## Workstream B. Quality + Value

### 기준점

- family: `Quality + Value`
- variant: `Strict Annual`
- current strongest practical point:
  - quality:
    - `roe`
    - `roa`
    - `operating_margin`
    - `asset_turnover`
    - `current_ratio`
  - value:
    - `book_to_market`
    - `earnings_yield`
    - `sales_yield`
    - `pcr`
    - `por`
    - `per`
  - `Top N = 10`
  - `Benchmark Contract = Candidate Universe Equal-Weight`
  - `CAGR = 31.82%`
  - `MDD = -26.63%`
  - `real_money_candidate / small_capital_trial / review_required`

### 완료한 작업

- [x] bounded downside refinement first pass
  - `Top N = 9 / 10 / 11`
  - quality-side replacement
  - value-side replacement
  - `Ticker Benchmark = SPY` recap
- [x] strongest-point downside follow-up second pass
  - `Top N = 9`
  - `current_ratio -> cash_ratio`
  - `Trend Filter = on`
  - `Ticker Benchmark = SPY`

### 최종 결론

- current strongest practical point는 current code에서도 그대로 유지된다
- lower-MDD but weaker-gate alternatives:
  - `Top N = 9`
    - `CAGR = 32.21%`
    - `MDD = -25.61%`
    - `production_candidate / watchlist / review_required`
  - `current_ratio -> cash_ratio`
    - `CAGR = 31.83%`
    - `MDD = -25.79%`
    - `production_candidate / watchlist / review_required`
- human-readable benchmark alternative:
  - `Ticker Benchmark = SPY`
  - same `CAGR / MDD`
  - `real_money_candidate / paper_probation / review_required`

쉬운 뜻:

- `Quality + Value`는 지금 strongest practical blended family다
- 하지만 이번 bounded 범위 안에서는
  same gate를 유지하면서 `MDD`만 더 낮추는 exact hit는 없었다

## 현재 추천 포인트

- `Value`:
  - `Top N = 14 + psr`
  - `CAGR = 28.13%`
  - `MDD = -24.55%`
  - `real_money_candidate / paper_probation / review_required`
- `Quality + Value`:
  - `operating_margin + pcr + por + per + Top N 10 + Candidate Universe Equal-Weight`
  - `CAGR = 31.82%`
  - `MDD = -26.63%`
  - `real_money_candidate / small_capital_trial / review_required`

## closeout 판단

- bounded downside refinement:
  - `completed`
- lower-MDD rescue follow-up:
  - `completed`
- strategy hub / one-pager / backtest log 동기화:
  - `completed`
- next structural downside backlog:
  - `deferred`

즉 Phase 16은
**bounded downside refinement를 practical 기준으로 마무리하고,
다음은 구조적인 downside improvement phase로 넘기는 상태**
라고 보면 된다.
