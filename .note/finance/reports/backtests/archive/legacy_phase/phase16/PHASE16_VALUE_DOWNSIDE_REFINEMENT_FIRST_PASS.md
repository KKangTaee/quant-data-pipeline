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

### one-factor bounded addition / replacement

- addition:
  - `psr`
  - `per`
  - `pbr`
  - `por`
  - `ev_ebit`
  - `fcf_yield`
- replacement probe:
  - `replace_sales_with_psr`
  - `replace_ocf_with_psr`

### overlay minimal sensitivity

- `Trend Filter = on/off`
- `Market Regime = on/off`

## representative rerun summary

### bounded additions / replacements

| Case | Top N | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
| --- | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `psr` addition anchor | 14 | 28.13% | -24.55% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `watch` | `caution` |
| `replace_sales_with_psr` | 14 | 27.31% | -24.55% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `caution` | `caution` |
| `per` addition | 13 | 28.70% | -25.69% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `caution` | `caution` |
| `por` addition | 14 | 26.88% | -25.06% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `watch` | `caution` |
| `ev_ebit` addition | 14 | 22.73% | -27.33% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `normal` | `caution` |
| `fcf_yield` addition | 14 | 23.16% | -28.21% | `production_candidate` | `watchlist` | `review_required` | `watch` | `caution` | `caution` |
| `pbr` addition | 14 | 25.83% | -25.67% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `caution` | `caution` |
| `psr` addition | 15 | 27.23% | -25.35% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `caution` | `caution` |
| `psr` addition | 16 | 26.37% | -24.85% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `caution` | `caution` |
| `psr` addition | 13 | 27.28% | -25.28% | `production_candidate` | `watchlist` | `review_required` | `watch` | `caution` | `caution` |
| `psr` addition | 12 | 27.83% | -25.35% | `production_candidate` | `watchlist` | `review_required` | `watch` | `caution` | `caution` |
| `replace_ocf_with_psr` | 14 | 26.50% | -25.40% | `hold` | `hold` | `blocked` | `caution` | `caution` | `caution` |

### overlay sensitivity on the anchor

| Case | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
| --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `trend off / regime off` | 28.13% | -24.55% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `watch` | `caution` |
| `trend on / regime off` | 25.92% | -29.25% | `hold` | `hold` | `blocked` | `caution` | `normal` | `normal` |
| `trend off / regime on` | 15.88% | -25.34% | `hold` | `hold` | `blocked` | `caution` | `caution` | `normal` |
| `trend on / regime on` | 18.68% | -27.17% | `hold` | `hold` | `blocked` | `caution` | `normal` | `normal` |

## 결론

- `Top N = 14 + psr` anchor가 여전히 가장 좋은 practical point다
- bounded addition / replacement 안에서 `MDD`를 더 낮추면서 gate를 유지하는 후보는 찾지 못했다
- overlay는 이 family에서 practical gate를 유지하는 downside lever가 아니었다
- 따라서 current search 기준으로는 `Value` family의 best practical anchor를 유지하고,
  다음 후보 family로 넘어가는 판단이 자연스럽다

## 읽는 법

이 문서는 `Value > Strict Annual`에 대해

- top_n를 조금 흔들어 보고
- 한 개 factor만 더하거나 바꾸고
- overlay를 아주 좁게 시험했을 때

실전형 승격 상태를 유지하면서 `MDD`를 더 낮출 수 있는지를 보는 first pass 기록이다.
