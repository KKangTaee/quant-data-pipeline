# Phase 16 Quality + Value Downside Refinement First Pass

## 목적

`Quality + Value > Strict Annual` current strongest practical point를 기준으로
bounded하게 다시 탐색해서

- `Promotion = real_money_candidate`
- `Shortlist = small_capital_trial`
- `Deployment != blocked`

를 가능하면 유지하면서 `MDD`를 더 낮출 수 있는 후보가 있는지 확인한다.

이번 pass에서는 lower-drawdown same-gate candidate가 없더라도,
같은 `MDD` / 같은 gate에서 `CAGR`를 더 높일 수 있는지도 같이 본다.

## 고정한 기준

- 전략: `Quality + Value > Strict Annual`
- 기간: `2016-01-01 ~ 2026-04-01`
- preset: `US Statement Coverage 100`
- `Universe Contract`: `Historical Dynamic PIT Universe`
- practical contract:
  - `Minimum Price = 5.0`
  - `Minimum History = 12M`
  - `Min Avg Dollar Volume 20D = 5.0M`
  - `Transaction Cost = 10 bps`
  - `Benchmark Contract = Candidate Universe Equal-Weight`
  - `Benchmark Ticker = SPY`
  - `Min Benchmark Coverage = 95%`
  - `Min Net CAGR Spread = -2%`
  - `Min Liquidity Clean Coverage = 90%`
  - `Max Underperformance Share = 55%`
  - `Min Worst Rolling Excess = -15%`
  - `Max Strategy Drawdown = -35%`
  - `Max Drawdown Gap vs Benchmark = 8%`
- guardrail:
  - underperformance `on / 12M / -10%`
  - drawdown `on / 12M / -35% / 8%`

## anchor

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

anchor result:

- `CAGR = 31.25%`
- `MDD = -26.63%`
- `Promotion = real_money_candidate`
- `Shortlist = small_capital_trial`
- `Deployment = review_required`
- `Validation / Rolling / OOS = normal / normal / normal`

## 탐색 범위

### Top N narrow band

- `9`
- `10`
- `11`

### bounded quality-side replacement probe

- `current_ratio -> cash_ratio`
- `current_ratio -> debt_to_assets`
- `current_ratio -> net_debt_to_equity`

### bounded value-side replacement probe

- `sales_yield -> fcf_yield`
- `sales_yield -> psr`
- `per -> pbr`
- `operating_income_yield -> por`

### benchmark sensitivity recap

- same factor set에서 `Ticker Benchmark = SPY`도 같이 확인

## representative rerun summary

| Case | Top N | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
| --- | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `anchor` | 10 | 31.25% | -26.63% | `real_money_candidate` | `small_capital_trial` | `review_required` | `normal` | `normal` | `normal` |
| `operating_income_yield -> por` | 10 | 31.82% | -26.63% | `real_money_candidate` | `small_capital_trial` | `review_required` | `normal` | `normal` | `normal` |
| `Top N` follow-up | 9 | 31.08% | -25.61% | `production_candidate` | `watchlist` | `review_required` | `watch` | `normal` | `normal` |
| `Top N` follow-up | 11 | 28.45% | -28.83% | `production_candidate` | `watchlist` | `review_required` | `watch` | `normal` | `normal` |
| `current_ratio -> cash_ratio` | 10 | 30.96% | -25.79% | `production_candidate` | `watchlist` | `review_required` | `watch` | `watch` | `normal` |
| `current_ratio -> debt_to_assets` | 10 | 23.03% | -29.47% | `hold` | `hold` | `blocked` | `caution` | `normal` | `normal` |
| `current_ratio -> net_debt_to_equity` | 10 | 22.44% | -30.59% | `hold` | `hold` | `blocked` | `caution` | `normal` | `normal` |
| `sales_yield -> fcf_yield` | 10 | 23.03% | -30.08% | `hold` | `hold` | `blocked` | `caution` | `caution` | `caution` |
| `sales_yield -> psr` | 10 | 31.25% | -26.63% | `real_money_candidate` | `small_capital_trial` | `review_required` | `normal` | `normal` | `normal` |
| `per -> pbr` | 10 | 29.51% | -29.25% | `production_candidate` | `watchlist` | `review_required` | `watch` | `normal` | `normal` |
| `SPY benchmark sensitivity` | 10 | 31.82% | -26.63% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `normal` | `normal` |

## 결론

- 이번 bounded search에서는
  same gate를 유지하면서 `MDD`를 더 낮춘 후보는 찾지 못했다
- 대신 same gate / same `MDD`를 유지하면서
  `CAGR`를 더 높인 새로운 strongest practical point를 찾았다
  - `operating_income_yield -> por`
  - `CAGR = 31.82%`
  - `MDD = -26.63%`
  - `Promotion = real_money_candidate`
  - `Shortlist = small_capital_trial`
  - `Deployment = review_required`
- lower-MDD but weaker-gate candidate는 분명 존재했다
  - `Top N = 9`
  - `current_ratio -> cash_ratio`
  하지만 둘 다 `production_candidate / watchlist`로 내려갔다
- `Ticker Benchmark = SPY`는 human-readable benchmark 대안이긴 하지만,
  same result에서도 `Shortlist = paper_probation`으로 한 단계 내려간다

## 읽는 법

이 문서는 `Quality + Value > Strict Annual`에 대해

- current strongest practical point를 기준으로
- top_n를 조금 흔들어 보고
- quality/value factor를 한 개만 바꿔 보고
- benchmark를 한 번 더 확인했을 때

더 낮은 `MDD`와 same gate를 동시에 만들 수 있는지 보는 first pass 기록이다.

이번 pass의 실무 해석은:

- lower `MDD`를 원하면 gate를 조금 양보해야 할 가능성이 높고
- same gate를 지키려면 현재는
  `operating_income_yield -> por`
  조합이 strongest practical point다
