# Phase 16 Value Downside Rescue Search Second Pass

## 목적

`Value > Strict Annual`의 current practical anchor로 알려졌던
`Top N = 14 + psr`를 current runtime 기준으로 다시 돌려보고,
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

### Top N narrow band

- `13`
- `14`
- `15`
- `16`

### one-factor bounded addition / replacement

- addition:
  - `pfcr`
  - `pcr`
  - `por`
  - `per`
  - `pbr`
- replacement probe:
  - `pfcr` / `pcr` on `sales_yield`
  - `pfcr` / `pcr` on `ocf_yield`
  - `por` on `ocf_yield`

### minimal benchmark sensitivity

- `Ticker Benchmark`
- `Candidate Universe Equal-Weight`

## current code rerun summary

### ticker benchmark rerun

| Case | Top N | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
| --- | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `anchor_psr_t14` | 14 | 28.13% | -24.55% | `hold` | `hold` | `blocked` | `normal` | `watch` | `caution` |
| `pfcr_add_t13` | 13 | 24.82% | -22.13% | `hold` | `hold` | `blocked` | `watch` | `caution` | `caution` |
| `pfcr_add_t14` | 14 | 23.73% | -28.21% | `hold` | `hold` | `blocked` | `normal` | `caution` | `caution` |
| `pfcr_add_t15` | 15 | 25.45% | -27.05% | `hold` | `hold` | `blocked` | `normal` | `caution` | `caution` |
| `pfcr_add_t16` | 16 | 25.55% | -26.44% | `hold` | `hold` | `blocked` | `normal` | `caution` | `caution` |
| `pcr_add_t14` | 14 | 24.58% | -31.86% | `hold` | `hold` | `blocked` | `caution` | `caution` | `caution` |
| `por_add_t14` | 14 | 26.88% | -25.06% | `hold` | `hold` | `blocked` | `normal` | `watch` | `caution` |
| `per_add_t14` | 14 | 27.49% | -25.55% | `hold` | `hold` | `blocked` | `normal` | `caution` | `caution` |
| `pbr_add_t14` | 14 | 25.83% | -25.67% | `hold` | `hold` | `blocked` | `normal` | `caution` | `caution` |
| `pfcr_replace_sales_t14` | 14 | 23.15% | -21.73% | `hold` | `hold` | `blocked` | `watch` | `caution` | `caution` |
| `pfcr_replace_ocf_t14` | 14 | 24.38% | -23.76% | `hold` | `hold` | `blocked` | `caution` | `caution` | `caution` |
| `pcr_replace_sales_t14` | 14 | 24.25% | -30.77% | `hold` | `hold` | `blocked` | `watch` | `caution` | `caution` |
| `por_replace_ocf_t14` | 14 | 27.47% | -25.48% | `hold` | `hold` | `blocked` | `normal` | `caution` | `caution` |

### benchmark sensitivity

| Case | Benchmark Contract | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
| --- | --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `anchor_psr_t14` | `Ticker Benchmark` | 28.13% | -24.55% | `hold` | `hold` | `blocked` | `caution` | `caution` | `caution` |
| `anchor_psr_t14` | `Candidate Universe Equal-Weight` | 28.13% | -24.55% | `hold` | `hold` | `blocked` | `caution` | `caution` | `caution` |

## 결론

- current code 기준으로는 `Top N = 14 + psr`를 포함한 bounded rescue 후보가 same gate를 유지하지 못했다.
- `pfcr` 계열과 `por`, `per`, `pbr` 계열은 일부 `MDD`를 낮추거나 비슷한 수준을 만들었지만, `Promotion`과 `Shortlist`가 `hold` 또는 `blocked`에 머물렀다.
- benchmark sensitivity도 rescue를 만들지 못했다.
- 따라서 current code 기준 `Value` rescue는 실패이며, historical practical anchor는 reference로만 남기는 것이 맞다.

## 읽는 법

이 문서는 historical current candidate를 current runtime으로 재검증했을 때
same-gate rescue가 가능한지 확인한 second pass 기록이다.

만약 이 문서를 읽고 있다면, 결론은 간단하다.

- `MDD`만 더 낮춘 near-miss는 있다
- 하지만 실전형 gate를 같이 만족하는 bounded rescue는 아직 없다
