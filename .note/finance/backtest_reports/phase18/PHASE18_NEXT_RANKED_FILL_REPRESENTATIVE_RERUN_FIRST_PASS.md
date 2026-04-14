# Phase 18 Next-Ranked Fill Representative Rerun First Pass

## 목적

- strict annual larger structural redesign first slice인
  `Fill Rejected Slots With Next Ranked Names`
  contract가
  current `Value` / `Quality + Value` structural probe에서
  실제로 의미 있는 rescue로 이어지는지 확인한다.

## 공통 해석

- 이번 rerun은 current practical anchor를 그대로 다시 돌린 것이 아니라,
  **trend rejection이 실제로 발생하는 structural probe**
  를 기준으로 봤다.
- 이유:
  - next-ranked fill은
    `Trend Filter`가 raw top-N 일부를 탈락시키는 상황에서만 작동하기 때문이다.

공통 contract:

- `2016-01-01 ~ 2026-04-01`
- `US Statement Coverage 100`
- `Historical Dynamic PIT Universe`
- `Minimum Price = 5.0`
- `Minimum History = 12M`
- `Min Avg Dollar Volume 20D = 5.0M`
- `Transaction Cost = 10 bps`
- practical benchmark / liquidity / validation / guardrail policy 유지
- `Trend Filter = on`
- `Market Regime = off`
- `partial_cash_retention_enabled = false`
- `risk_off_mode = cash_only`
- `rejected_slot_fill_enabled = off / on`

## 1. Value probe

전략:

- `Value > Strict Annual`
- factors:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `ocf_yield`
  - `operating_income_yield`
  - `psr`
- `Top N = 14`
- `Benchmark Contract = Ticker Benchmark`
- `Benchmark Ticker = SPY`

결과:

- `fill off`
  - `CAGR = 25.92%`
  - `MDD = -29.25%`
  - `Promotion = hold`
  - `Shortlist = hold`
  - `Deployment = blocked`
  - `Validation = caution`
  - `Average Cash Share = 11.38%`
- `fill on`
  - `CAGR = 25.23%`
  - `MDD = -28.37%`
  - `Promotion = hold`
  - `Shortlist = hold`
  - `Deployment = blocked`
  - `Validation = normal`
  - `Filled Rows = 117`
  - `Filled Tickers = 466`
  - `Average Cash Share = 0.00%`

해석:

- `Value`에서는 이 redesign이 selection-structure 개선으로는 의미가 있었다
- cash drag를 없애고 `MDD`를 일부 줄였으며
  `Validation = caution -> normal`까지는 회복시켰다
- 다만 current practical anchor
  (`28.13% / -24.55% / real_money_candidate / paper_probation / review_required`)
  보다 더 좋은 downside point도 아니고,
  gate recovery도 만들지 못했으므로
  current anchor replacement로 보진 않는다

## 2. Quality + Value probe

전략:

- `Quality + Value > Strict Annual`
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

결과:

- `fill off`
  - `CAGR = 30.01%`
  - `MDD = -29.72%`
  - `Promotion = hold`
  - `Shortlist = hold`
  - `Deployment = blocked`
  - `Validation = caution`
  - `Average Cash Share = 11.40%`
- `fill on`
  - `CAGR = 26.64%`
  - `MDD = -28.05%`
  - `Promotion = hold`
  - `Shortlist = hold`
  - `Deployment = blocked`
  - `Validation = caution`
  - `Filled Rows = 111`
  - `Filled Tickers = 328`
  - `Average Cash Share = 8.09%`

해석:

- blended family에서도 redesign은 실제로 작동했다
- cash share와 `MDD`를 줄였지만
  이번 first pass에서는 gate recovery까지 이어지진 못했다
- 즉 `Quality + Value`에서는
  “개선은 있음, 하지만 still hold”로 읽는 것이 맞다

## 결론

이번 first pass는 이렇게 정리할 수 있다.

1. `next-ranked eligible fill`은 의미 있는 new lane이다
2. `Value`에서는 cash drag, `MDD`, validation을 개선했지만 still hold였다
3. `Quality + Value`에서는 개선은 있었지만 still hold였다
4. current practical anchor replacement는 아직 아니다

즉 이 contract는
“실패한 실험”이 아니라
**larger structural redesign이 실제로 의미가 있다는 첫 evidence**
로 보는 것이 더 정확하다.
