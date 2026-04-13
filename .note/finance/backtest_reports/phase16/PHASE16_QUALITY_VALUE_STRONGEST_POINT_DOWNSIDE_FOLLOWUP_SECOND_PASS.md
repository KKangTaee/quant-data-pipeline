# Phase 16 Quality Value Strongest Point Downside Follow-Up Second Pass

## 목적

`Quality + Value > Strict Annual` current strongest practical point인

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

조합을 기준으로,

- `real_money_candidate`
- `small_capital_trial`
- `review_required`

를 가능하면 유지하면서 더 낮은 `MDD` candidate가 있는지 다시 확인한다.

이번 pass에서는 lower-MDD exact hit가 없더라도,

- strongest point가 current code에서도 그대로 유지되는지
- lower-MDD but weaker-gate 대안이 어디까지 가능한지
- `SPY` benchmark 같은 human-readable 대안이 어떤 tradeoff를 만드는지

를 같이 본다.

## 실행 기준

- 전략: `Quality + Value > Strict Annual`
- 기간: `2016-01-01 ~ 2026-04-01`
- preset: `US Statement Coverage 100`
- `Universe Contract`: `Historical Dynamic PIT Universe`
- practical contract:
  - `Minimum Price = 5.0`
  - `Minimum History = 12M`
  - `Min Avg Dollar Volume 20D = 5.0M`
  - `Transaction Cost = 10 bps`
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

## 탐색 범위

### strongest point reconfirm

- `Top N = 10`
- `Benchmark Contract = Candidate Universe Equal-Weight`

### lower-MDD near-miss rescue probe

- `Top N = 9`
- `current_ratio -> cash_ratio`
- `Top N = 9 + current_ratio -> cash_ratio`

### sensitivity recap

- `Trend Filter on`
- `Ticker Benchmark = SPY`

## current code rerun summary

| Case | Top N | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
| --- | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `por_anchor_top10` | 10 | 31.82% | -26.63% | `real_money_candidate` | `small_capital_trial` | `review_required` | `normal` | `normal` | `normal` |
| `por_anchor_top9` | 9 | 32.21% | -25.61% | `production_candidate` | `watchlist` | `review_required` | `watch` | `normal` | `normal` |
| `por_anchor_top10_cash` | 10 | 31.83% | -25.79% | `production_candidate` | `watchlist` | `review_required` | `watch` | `watch` | `normal` |
| `por_anchor_top9_cash` | 9 | 33.08% | -25.70% | `hold` | `hold` | `blocked` | `caution` | `watch` | `normal` |
| `por_anchor_top10_trend` | 10 | 30.01% | -29.72% | `hold` | `hold` | `blocked` | `caution` | `normal` | `normal` |
| `por_anchor_top10_spy` | 10 | 31.82% | -26.63% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `normal` | `normal` |

## 결론

- current strongest practical point는 그대로 유지된다.
  - `CAGR = 31.82%`
  - `MDD = -26.63%`
  - `real_money_candidate / small_capital_trial / review_required`
- same gate를 유지하면서 `MDD`를 더 낮춘 exact hit는 이번 second pass에서도 없었다.
- 가장 매력적인 lower-MDD near-miss는 두 갈래였다.
  - `Top N = 9`
    - `CAGR = 32.21%`
    - `MDD = -25.61%`
    - 하지만 `production_candidate / watchlist`
  - `Top N = 10 + current_ratio -> cash_ratio`
    - `CAGR = 31.83%`
    - `MDD = -25.79%`
    - 하지만 `production_candidate / watchlist`
- `SPY` benchmark 대안은
  - same `CAGR / MDD`
  - same `real_money_candidate`
  - 하지만 `small_capital_trial -> paper_probation`
  로 한 단계 내려간다.

## 읽는 법

이 문서는
`Quality + Value > Strict Annual` strongest point를 current runtime에서 한 번 더 좁게 재검증했을 때

- strongest point가 그대로 유지되는지
- lower-MDD 대안이 gate를 얼마나 희생하는지

를 보는 second-pass follow-up report다.

실무 해석은 간단하다.

- strongest point는 지금도 충분히 강하다
- 더 낮은 `MDD` 대안은 보이지만
  이번 범위에서는 gate를 조금 양보해야 한다
- 따라서 다음 phase에서는
  bounded `Top N / one-factor`보다 더 구조적인 downside lever를 보는 편이 자연스럽다
