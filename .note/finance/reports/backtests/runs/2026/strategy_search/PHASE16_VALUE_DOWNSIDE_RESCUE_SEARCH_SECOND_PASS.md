# Phase 16 Value Downside Rescue Search Second Pass

## 목적

`Value > Strict Annual`의 current practical anchor인
`Top N = 14 + psr`를 기준으로 다시 돌려보고,
같은 gate를 유지하면서 `MDD`를 더 낮출 수 있는 bounded rescue 후보가 있는지 확인한다.

이번 pass는 다음을 동시에 확인하는 데 초점을 둔다.

- `Promotion = real_money_candidate`
- `Shortlist >= paper_probation`
- `Deployment != blocked`

## 실행 기준

- 전략: `Value > Strict Annual`
- 기간: `2016-01-01 ~ 2026-04-01`
- preset: `US Statement Coverage 100`
- `Universe Contract`: `Historical Dynamic PIT Universe`
- benchmark:
  - `Ticker Benchmark` / `SPY`
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

### baseline reconfirm

- `Top N = 14 + psr`

### lower-MDD rescue probe

- `Top N = 14 + psr + pfcr`
- `Top N = 15 + psr + pfcr`

### benchmark / overlay sensitivity

- `Candidate Universe Equal-Weight`
- `Trend Filter on`
- `Market Regime on`

### bounded replacement recap

- `sales_yield -> pfcr`

## current code rerun summary

| Case | Top N | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
| --- | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `anchor_psr_t14` | 14 | 28.13% | -24.55% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `watch` | `caution` |
| `pfcr_add_t14` | 14 | 27.22% | -21.16% | `production_candidate` | `watchlist` | `review_required` | `watch` | `caution` | `caution` |
| `pfcr_add_t15` | 15 | 25.95% | -27.59% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `caution` | `caution` |
| `pfcr_add_t14_eqw` | 14 | 27.22% | -21.16% | `hold` | `hold` | `blocked` | `caution` | `caution` | `caution` |
| `pfcr_add_t14_trend` | 14 | 24.49% | -28.72% | `hold` | `hold` | `blocked` | `caution` | `normal` | `caution` |
| `pfcr_add_t14_regime` | 14 | 17.54% | -16.16% | `hold` | `hold` | `blocked` | `caution` | `caution` | `caution` |
| `sales_yield -> pfcr` | 14 | 23.80% | -28.21% | `hold` | `hold` | `blocked` | `caution` | `caution` | `caution` |

## 결론

- current best practical point는 여전히 `Top N = 14 + psr`다.
- 이번 second pass의 핵심 lower-MDD near-miss는
  `Top N = 14 + psr + pfcr`였다.
  - `CAGR = 27.22%`
  - `MDD = -21.16%`
  - 하지만 `production_candidate / watchlist`라서
    same gate rescue는 아니다.
- `Top N = 15 + psr + pfcr`는
  `real_money_candidate / paper_probation`을 회복했지만,
  `MDD = -27.59%`로 baseline보다 더 나빠져 rescue 의미를 잃었다.
- `Candidate Universe Equal-Weight`, `Trend Filter`, `Market Regime` sensitivity도
  same-gate lower-MDD rescue를 만들지 못했다.
- 따라서 current code 기준 결론은:
  - `Value` current best practical point 유지
  - lower-MDD but weaker-gate near-miss는 reference로만 보관
  - deeper downside improvement는 다음 phase의 structural work로 넘기는 것이 맞다

## 읽는 법

이 문서는
`Value > Strict Annual` current practical point 위에서
한 단계 더 bounded하게 rescue를 시도했을 때

- 무엇이 lower-MDD near-miss였고
- 왜 same-gate rescue가 아니었는지

를 정리한 second-pass report다.

실무 해석은 간단하다.

- `Value`는 아직 강한 family다
- 하지만 이번 범위 안에서는
  `MDD`를 더 낮추면서 same gate를 지키는 exact rescue는 못 찾았다
