# Phase 16 Value Downside Refinement First Pass

## 목적

`Value > Strict Annual` current practical anchor인 `Top N = 14 + psr`를 기준으로
bounded하게 다시 탐색해서
`Promotion = real_money_candidate`,
`Shortlist >= paper_probation`,
`Deployment != blocked`
를 유지하면서 `MDD`를 더 낮출 수 있는 후보가 있는지 확인한다.

## 고정한 기준

- 전략: `Value > Strict Annual`
- 기간: `2016-01-01 ~ 2026-04-01`
- preset: `US Statement Coverage 100`
- `Universe Contract`: `Historical Dynamic PIT Universe`
- practical contract:
  - `Minimum Price = 5.0`
  - `Minimum History = 12M`
  - `Min Avg Dollar Volume 20D = 5.0M`
  - `Transaction Cost = 10 bps`
  - `Benchmark Contract = Ticker Benchmark`
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

## 탐색 범위

### Top N narrow band

- `12`
- `13`
- `14`
- `15`
- `16`
- `18`

### one-factor bounded addition / replacement

- addition:
  - `pcr`
  - `pfcr`
  - `fcf_yield`
- replacement probe:
  - `replace_sales_with_pcr`
  - `replace_sales_with_pfcr`
  - `replace_ocf_with_pcr`
  - `replace_ocf_with_fcf`

## representative rerun summary

| Case | Top N | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
| --- | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `anchor` | 14 | 28.13% | -24.55% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `watch` | `caution` |
| `Top N` follow-up | 15 | 27.23% | -25.35% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `caution` | `caution` |
| `Top N` follow-up | 16 | 26.37% | -24.85% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `caution` | `caution` |
| `Top N` follow-up | 13 | 27.28% | -25.28% | `production_candidate` | `watchlist` | `review_required` | `watch` | `caution` | `caution` |
| `Top N` follow-up | 12 | 27.83% | -25.35% | `production_candidate` | `watchlist` | `review_required` | `watch` | `caution` | `caution` |
| `Top N` follow-up | 18 | 25.06% | -29.04% | `production_candidate` | `watchlist` | `review_required` | `watch` | `caution` | `caution` |
| `+ pcr` | 14 | 28.75% | -25.00% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `caution` | `caution` |
| `+ pfcr` | 14 | 27.22% | -21.16% | `production_candidate` | `watchlist` | `review_required` | `watch` | `caution` | `caution` |
| `+ fcf_yield` | 14 | 25.29% | -21.16% | `hold` | `hold` | `blocked` | `caution` | `caution` | `caution` |
| `sales_yield -> pcr` | 14 | 24.59% | -31.86% | `hold` | `hold` | `blocked` | `caution` | `caution` | `caution` |
| `sales_yield -> pfcr` | 14 | 23.80% | -28.21% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `caution` | `caution` |
| `ocf_yield -> pcr` | 14 | 28.01% | -24.55% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `watch` | `caution` |
| `ocf_yield -> fcf_yield` | 14 | 24.42% | -30.16% | `production_candidate` | `watchlist` | `review_required` | `watch` | `caution` | `caution` |

## 결론

- `Top N = 14 + psr` anchor가 여전히 가장 좋은 practical point다
- bounded addition / replacement 안에서 `MDD`를 더 낮추면서 gate를 유지하는 후보는 찾지 못했다
- 가장 눈에 띄는 lower-MDD near-miss는 `+ pfcr`였다
  - `CAGR = 27.22%`
  - `MDD = -21.16%`
  - 하지만 `production_candidate / watchlist`로 내려갔다
- 따라서 current search 기준으로는 `Value` family의 best practical anchor를 유지하고,
  lower-MDD but weaker-gate candidate를 reference로만 남기는 판단이 자연스럽다

## 읽는 법

이 문서는 `Value > Strict Annual`에 대해

- top_n를 조금 흔들어 보고
- 한 개 factor만 더하거나 바꾸고
- same practical contract를 유지한 채

실전형 승격 상태를 유지하면서 `MDD`를 더 낮출 수 있는지를 보는 first pass 기록이다.
