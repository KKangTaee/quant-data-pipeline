# Current Practical Candidates Summary

## 이 문서는 무엇인가

이 문서는 지금 시점에서 다시 봐야 할
`Value`, `Quality`, `Quality + Value`
strict annual family의 **현재 기준 후보를 한 장으로 모아 둔 요약 문서**다.

쉽게 말하면:

- 지금 가장 먼저 다시 돌려볼 후보가 무엇인지
- 더 낮은 `MDD`지만 gate가 약한 near-miss가 무엇인지
- 다음 refinement를 어디서 이어야 하는지

를 빠르게 확인하기 위한 문서다.

## 가장 먼저 볼 후보

| family | 현재 추천 anchor | CAGR | MDD | Promotion | Shortlist | Deployment |
|---|---|---:|---:|---|---|---|
| `Value` | `Top N = 14 + psr` | `28.13%` | `-24.55%` | `real_money_candidate` | `paper_probation` | `review_required` |
| `Quality` | `capital_discipline + LQD + trend on + regime off + Top N 12` | `26.02%` | `-25.57%` | `real_money_candidate` | `paper_probation` | `review_required` |
| `Quality + Value` | `operating_margin + pcr + por + per + Top N 10 + Candidate Universe Equal-Weight` | `31.82%` | `-26.63%` | `real_money_candidate` | `small_capital_trial` | `review_required` |

## family별 해석

### 1. Value

- 지금 current best practical point는
  `Top N = 14 + psr`
  조합이다.
- `Value`가 여전히 세 family 중 가장 높은 raw return 축을 가지고 있고,
  practical candidate로도 강하다.
- 다만 same gate를 유지하면서 `MDD`를 더 낮춘 exact hit는 아직 못 찾았다.

lower-MDD near-miss:

- `+ pfcr`
- `CAGR = 27.22%`
- `MDD = -21.16%`
- `production_candidate / watchlist / review_required`

즉:

- 숫자는 더 방어적으로 좋아졌지만
- gate가 한 단계 내려가서 current anchor를 대체하진 못했다.
- Phase 17 structural note:
  - `Trend Filter = on`에서 `partial cash retention`을 붙이면
    `MDD = -15.85%`까지 크게 내려가지만
    `CAGR = 20.11%`, `hold / blocked`로 남아서
    current anchor를 바꾸진 못했다
  - `defensive sleeve risk-off(BIL, SHY, LQD)`를 붙이면
    gate는 유지되지만
    `MDD = -25.14%`로 소폭 더 나빠져
    역시 current anchor를 바꾸진 못했다

바로 열 문서:

- [VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL.md)
- [VALUE_STRICT_ANNUAL_FACTOR_ADDITION_BEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_FACTOR_ADDITION_BEST_CURRENT_CANDIDATE.md)

### 2. Quality

- `Quality`는 factor만 건드려서는 잘 안 풀렸고,
  구조 조정 이후 살아난 family다.
- current recommended point는
  `capital_discipline + LQD + trend on + regime off + Top N 12`
  이다.
- strongest raw winner family는 아니지만,
  quality-only family를 실전형으로 살리는 기준점으로는 중요하다.

cleaner alternative:

- `SPY + trend on + regime off + Top N 12`
- `CAGR = 25.18%`
- `MDD = -25.57%`
- `real_money_candidate / paper_probation / paper_only`

즉:

- `LQD` 버전은 practical point
- `SPY` 버전은 더 읽기 쉬운 cleaner alternative

바로 열 문서:

- [QUALITY_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL.md)
- [QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md)

### 3. Quality + Value

- 지금 blended family 중 strongest practical point는
  `operating_income_yield -> por`
  replacement까지 반영한 조합이다.
- 결과는:
  - `CAGR = 31.82%`
  - `MDD = -26.63%`
  - `real_money_candidate / small_capital_trial / review_required`
- same gate를 유지하며 `MDD`를 더 낮추진 못했지만,
  같은 `MDD`에서 `CAGR`를 더 올린 strongest point를 찾았다.

lower-MDD but weaker-gate near-miss:

- `Top N = 9`
- `CAGR = 31.08%`
- `MDD = -25.61%`
- `production_candidate / watchlist / review_required`

즉:

- 지금은 strongest practical point가 분명하고
- 그보다 더 방어적인 대안도 있지만 gate가 약하다.
- Phase 17 structural note:
  - strongest point에 `Trend Filter = on + partial cash retention`을 붙이면
    `MDD = -15.07%`까지 크게 낮아지지만
    `CAGR = 20.03%`, `hold / blocked`로 남아서
    current strongest point를 바꾸진 못했다
  - `defensive sleeve risk-off(BIL, SHY, LQD)`를 붙이면
    gate는 유지되지만
    `MDD = -27.19%`로 소폭 더 나빠져
    strongest point를 대체하지 못했다

바로 열 문서:

- [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
- [QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md)
- [QUALITY_VALUE_STRICT_ANNUAL_POR_REPLACEMENT_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_POR_REPLACEMENT_CURRENT_CANDIDATE.md)

## 현재 handoff 해석

1. `Value`
   - current best practical point는 여전히 `Top N = 14 + psr`
   - `+ pfcr` 같은 lower-MDD near-miss는 current code second pass에서도
     `production_candidate / watchlist`를 넘지 못했다
2. `Quality + Value`
   - current strongest practical point는 여전히
     `operating_margin + pcr + por + per + Top N 10 + Candidate Universe Equal-Weight`
   - `Top N = 9`와 `cash_ratio` 대안은 더 낮은 `MDD`를 보였지만
     `production_candidate / watchlist`로 내려갔다
3. 다음 phase 방향
   - bounded `Top N / one-factor / overlay`보다
     더 구조적인 downside improvement가 우선순위가 된다
   - Phase 17 current pass 기준으로는
     `partial cash retention`과 `defensive sleeve risk-off` 모두
     current anchor를 바꾸지 못했기 때문에
     다음 구현 후보는 `concentration-aware weighting`이 더 자연스럽다

## 관련 문서

- [PHASE16_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase16/PHASE16_CURRENT_CHAPTER_TODO.md)
- [BACKTEST_REPORT_INDEX.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/BACKTEST_REPORT_INDEX.md)
