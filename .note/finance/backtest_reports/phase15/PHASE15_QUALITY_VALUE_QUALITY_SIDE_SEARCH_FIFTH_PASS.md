# Phase 15 Quality + Value Quality-Side Search Fifth Pass

## 목적

`Quality + Value > Strict Annual`의 current strongest practical point가
value-side fourth pass까지는

- `ocf_yield -> pcr`
- `Top N = 10`
- `Candidate Universe Equal-Weight`

조합으로 정리돼 있었다.

이번 pass에서는 이 anchor를 유지한 채,
quality factor 쪽 one-for-one bounded replacement를 한 번 더 붙였을 때
실제로 stronger practical point가 나오는지 확인한다.

## 고정 anchor

- 전략:
  - `Quality + Value > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- quality anchor:
  - `roe`
  - `roa`
  - `net_margin`
  - `asset_turnover`
  - `current_ratio`
- value anchor:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `pcr`
  - `operating_income_yield`
  - `per`
- contract:
  - `Top N = 10`
  - `Rebalance Interval = 1`
  - `Option = month_end`
  - `Benchmark Contract = Candidate Universe Equal-Weight`
  - `Trend Filter = off`
  - `Market Regime = off`
  - practical `Real-Money Contract`
  - underperformance / drawdown guardrail `on`

## 이번 pass에서 본 quality-side bounded move

- replace `net_margin -> operating_margin`
- replace `current_ratio -> operating_margin`
- replace baseline factor one-by-one with:
  - `cash_ratio`
  - `operating_margin`
  - `interest_coverage`
  - `ocf_margin`
  - `fcf_margin`
  - `net_debt_to_equity`

## 대표 결과

| case | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
| --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| current anchor | 30.05% | -27.43% | `real_money_candidate` | `small_capital_trial` | `review_required` | `normal` | `normal` | `normal` |
| replace `net_margin -> operating_margin` | 31.25% | -26.63% | `real_money_candidate` | `small_capital_trial` | `review_required` | `normal` | `normal` | `normal` |
| replace `current_ratio -> operating_margin` | 30.84% | -24.09% | `production_candidate` | `watchlist` | `review_required` | `watch` | `normal` | `normal` |

## 해석

### 1. `net_margin -> operating_margin`이 current anchor를 실제로 넘었다

이 replacement는

- `CAGR`: `30.05% -> 31.25%`
- `MDD`: `-27.43% -> -26.63%`

로 둘 다 좋아졌고,

- `Promotion = real_money_candidate`
- `Shortlist = small_capital_trial`
- `Deployment = review_required`
- `Validation / Rolling / OOS = normal / normal / normal`

도 그대로 유지했다.

즉 practical gate를 희생하지 않고
return / drawdown을 같이 개선한 bounded replacement다.

### 2. `current_ratio -> operating_margin`은 숫자는 더 방어적이지만 gate가 약해진다

이 조합은

- `CAGR = 30.84%`
- `MDD = -24.09%`

로 downside는 더 좋아 보이지만,

- `Promotion = production_candidate`
- `Shortlist = watchlist`
- `Validation = watch`

로 내려가서 current strongest practical point를 완전히 넘는 후보로 보긴 어렵다.

### 3. 이번 pass의 결론

현재 `Quality + Value` strongest practical point는 이제:

- quality replacement:
  - `net_margin -> operating_margin`
- value replacement:
  - `ocf_yield -> pcr`
- `Top N = 10`
- `Candidate Universe Equal-Weight`

조합으로 읽는 편이 맞다.

## 다음 액션

1. 새 strongest practical point를 strategy hub와 backtest log에 반영
2. 필요하면 다음에는 이 new anchor 기준 `Top N`만 다시 좁게 흔들어본다
3. 아니면 current strongest candidates를 정리하며 Phase 15 closeout 준비로 넘어간다

## 관련 문서

- [PHASE15_QUALITY_VALUE_REPLACEMENT_ANCHOR_FOLLOWUP_FOURTH_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_REPLACEMENT_ANCHOR_FOLLOWUP_FOURTH_PASS.md)
- [PHASE15_QUALITY_VALUE_VALUE_SIDE_SEARCH_THIRD_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_VALUE_SIDE_SEARCH_THIRD_PASS.md)
- [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
- [QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
