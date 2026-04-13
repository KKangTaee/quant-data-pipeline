# Phase 16 Current Chapter TODO

## 목표

- `Value > Strict Annual`과 `Quality + Value > Strict Annual`의
  current practical candidate를 유지하면서
  `MDD`를 더 낮추거나 같은 `MDD`에서 `CAGR`를 더 높이는
  downside-focused practical refinement를 진행한다.
- 우선순위는:
  - `Value`
  - `Quality + Value`
  순서로 둔다.

## Workstream A. Value

### 현재 앵커

- family: `Value`
- variant: `Strict Annual`
- anchor: `Top N = 14 + psr`
- result:
  - `CAGR = 28.13%`
  - `MDD = -24.55%`
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = review_required`

### 완료된 작업

- [x] `Top N` narrow band first pass
  - `12 / 13 / 14 / 15 / 16 / 18` 확인
- [x] bounded addition / replacement first pass
  - `pcr`, `pfcr`, `fcf_yield`
  - `sales_yield -> pcr`
  - `sales_yield -> pfcr`
  - `ocf_yield -> pcr`
  - `ocf_yield -> fcf_yield`

### 이번 단계 결론

- `Top N = 14 + psr`가 여전히 best practical point다
- 더 낮은 `MDD`를 유지하면서 same gate를 통과하는 bounded variant는 찾지 못했다
- notable lower-MDD near-miss:
  - `+ pfcr`
  - `CAGR = 27.22%`
  - `MDD = -21.16%`
  - 하지만 `production_candidate / watchlist`로 내려갔다

## Workstream B. Quality + Value

### 현재 앵커

- family: `Quality + Value`
- variant: `Strict Annual`
- anchor:
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
    - `operating_income_yield`
    - `per`
  - `Top N = 10`
  - `Benchmark Contract = Candidate Universe Equal-Weight`
- anchor result:
  - `CAGR = 31.25%`
  - `MDD = -26.63%`
  - `Promotion = real_money_candidate`
  - `Shortlist = small_capital_trial`
  - `Deployment = review_required`

### 완료된 작업

- [x] `Top N` narrow band first pass
  - `9 / 10 / 11`
- [x] bounded quality-side replacement probe
  - `current_ratio -> cash_ratio`
  - `current_ratio -> debt_to_assets`
  - `current_ratio -> net_debt_to_equity`
- [x] bounded value-side replacement probe
  - `sales_yield -> fcf_yield`
  - `sales_yield -> psr`
  - `per -> pbr`
  - `operating_income_yield -> por`
- [x] benchmark sensitivity recap
  - `Ticker Benchmark = SPY`까지 다시 확인

### 이번 단계 결론

- same gate를 유지하면서 `MDD`를 더 낮춘 bounded variant는 찾지 못했다
- 대신 same gate / same `MDD`를 유지하면서
  `CAGR`를 더 높인 new strongest practical point를 찾았다
  - `operating_income_yield -> por`
  - `CAGR = 31.82%`
  - `MDD = -26.63%`
  - `Promotion = real_money_candidate`
  - `Shortlist = small_capital_trial`
  - `Deployment = review_required`
- lower-MDD but weaker-gate near-miss:
  - `Top N = 9`
  - `CAGR = 31.08%`
  - `MDD = -25.61%`
  - `production_candidate / watchlist`
- another lower-MDD but weaker-gate near-miss:
  - `current_ratio -> cash_ratio`
  - `CAGR = 30.96%`
  - `MDD = -25.79%`
  - `production_candidate / watchlist`

## 현재 추천 포인트

- `Value` current best practical point:
  - `Top N = 14 + psr`
  - `CAGR = 28.13%`
  - `MDD = -24.55%`
  - `real_money_candidate / paper_probation / review_required`
- `Quality + Value` current strongest practical point:
  - `operating_income_yield -> por`
  - `Top N = 10`
  - `Benchmark Contract = Candidate Universe Equal-Weight`
  - `CAGR = 31.82%`
  - `MDD = -26.63%`
  - `real_money_candidate / small_capital_trial / review_required`

## 다음 판단

- `Value`는 current anchor 유지 쪽으로 정리하고
  lower-MDD weaker-gate near-miss만 reference로 남긴다
- `Quality + Value`는 new strongest practical point를
  전략 허브 / one-pager / log에 반영한다
- 다음 active step은:
  - lower-MDD but weaker-gate candidate를 rescue할지
  - 아니면 current strongest practical points 기준으로 closeout 준비로 갈지
  결정하는 것이다
