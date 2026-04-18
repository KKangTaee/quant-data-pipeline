# Current Practical Candidates Summary

## 이 문서는 무엇인가

이 문서는 지금 시점에서 다시 봐야 할
`Value`, `Quality`, `Quality + Value`
strict annual family와 별도로 다시 볼 ETF 전략 후보를 한 장으로 모아 둔 요약 문서다.

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
| `GTAA` | `SPY / QQQ / GLD / IEF, Top 2, Interval 4, 1M / 3M` | `17.46%` | `-8.39%` | `real_money_candidate` | `paper_probation` | `paper_only` |

## family별 해석

### 0. GTAA

- 사용자 요청으로 preset 밖 ETF universe를 다시 탐색했고,
  current DB/runtime 기준 `real_money_candidate`까지 올라간 compact ETF 후보를 확보했다.
- 추천 기본 후보는:
  - `SPY, QQQ, GLD, IEF`
  - `Top = 2`
  - `Interval = 4`
  - `Score Horizons = 1M / 3M`
  - `Risk-Off Mode = defensive_bond_preference`
- 결과:
  - `CAGR = 17.46%`
  - `MDD = -8.39%`
  - `Sharpe = 3.07`
  - `real_money_candidate / paper_probation / paper_only`
- 해석:
  - 기존 Phase 13 GTAA reference는 `production_candidate / watchlist_only`였지만,
    이번 후보는 `Validation = normal`과 `ETF Operability = normal`을 함께 만족했다.
  - 다만 ETF 전략의 current deployment는 `paper_only`이므로,
    실전 투입 전 paper tracking 후보로 본다.

바로 열 문서:

- [GTAA.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/GTAA.md)
- [GTAA_REAL_MONEY_CANDIDATE_SEARCH_20260418.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/GTAA_REAL_MONEY_CANDIDATE_SEARCH_20260418.md)

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
- Phase 21 integrated validation first pass에서도
  이 해석은 그대로 유지되었다.
  - current anchor:
    - `28.13% / -24.55% / real_money_candidate / paper_probation / review_required`
  - lower-MDD alternative:
    - `27.22% / -21.16% / production_candidate / watchlist / review_required`
- Phase 17 structural note:
  - `Trend Filter = on`에서 `partial cash retention`을 붙이면
    `MDD = -15.85%`까지 크게 내려가지만
    `CAGR = 20.11%`, `hold / blocked`로 남아서
    current anchor를 바꾸진 못했다
  - `defensive sleeve risk-off(BIL, SHY, LQD)`를 붙이면
    gate는 유지되지만
    `MDD = -25.14%`로 소폭 더 나빠져
    역시 current anchor를 바꾸진 못했다
  - `concentration-aware weighting(rank_tapered)`을 붙이면
    gate는 유지되지만
    `MDD = -25.87%`로 더 나빠지고
    `Rolling Review = caution`으로 약해져
    역시 current anchor를 바꾸진 못했다
  - Phase 18 larger-redesign note:
    - `Trend Filter = on + next-ranked eligible fill`을 붙이면
      `25.23% / -28.37% / hold / blocked`
      로 cash drag와 validation은 개선되지만,
      gate recovery까지는 못 갔다
    - anchor-near second pass에서도
      `base + psr + pfcr`, `Top N = 13`
      의 `24.47% / -24.89% / hold / blocked`
      가 best lower-MDD near-miss였고,
      current anchor replacement는 없었다

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
- Phase 21 integrated validation first pass에서도
  이 해석이 그대로 유지되었다.
  - current anchor:
    - `26.02% / -25.57% / real_money_candidate / paper_probation / review_required`
  - cleaner alternative:
    - `25.18% / -25.57% / real_money_candidate / paper_probation / paper_only`
- 즉 `SPY` 버전은
  validation/rolling surface는 더 깔끔하지만,
  여전히 comparison-only alternative로 읽는 것이 맞다.

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
- `CAGR = 32.21%`
- `MDD = -25.61%`
- `production_candidate / watchlist / review_required`

즉:

- 지금은 strongest practical point가 분명하고
- 그보다 더 방어적인 대안도 있지만 gate가 약하다.
- Phase 21 integrated validation first pass에서도
  이 해석은 그대로 유지되었다.
  - current strongest point:
    - `31.82% / -26.63% / real_money_candidate / small_capital_trial / review_required`
  - lower-MDD alternative:
    - `32.21% / -25.61% / production_candidate / watchlist / review_required`
- 즉 `Top N = 9`는 숫자만 보면 매우 강하지만,
  current anchor를 교체하려면 아직 gate 해석이 부족하다.
- Phase 17 structural note:
  - strongest point에 `Trend Filter = on + partial cash retention`을 붙이면
    `MDD = -15.07%`까지 크게 낮아지지만
    `CAGR = 20.03%`, `hold / blocked`로 남아서
    current strongest point를 바꾸진 못했다
  - `defensive sleeve risk-off(BIL, SHY, LQD)`를 붙이면
    gate는 유지되지만
    `MDD = -27.19%`로 소폭 더 나빠져
    strongest point를 대체하지 못했다
  - `concentration-aware weighting(rank_tapered)`을 붙이면
    `CAGR = 32.92%`로 더 올라가지만
    `MDD = -27.60%`로 더 나빠져
    current strongest point를 대체하지 못했다
  - Phase 18 larger-redesign note:
    - `Trend Filter = on + next-ranked eligible fill`을 붙이면
      `26.64% / -28.05%`까지 개선되지만
      여전히 `hold / blocked`라서
      strongest practical point를 바꾸진 못했다

바로 열 문서:

- [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
- [QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md)
- [QUALITY_VALUE_STRICT_ANNUAL_POR_REPLACEMENT_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_POR_REPLACEMENT_CURRENT_CANDIDATE.md)

## 현재 handoff 해석

2026-04-17 log readability review:

- annual strict backtest log 3종은 최신 날짜순과 `최근 판단 요약표` 기준으로 정리했다.
- 이번 정리는 기록 가독성 개선이며, 아래 current anchor / lower-MDD alternative / portfolio bridge 판단은 변경하지 않는다.

1. `Value`
   - current best practical point는 여전히 `Top N = 14 + psr`
   - `+ pfcr` 같은 lower-MDD near-miss는 current code second pass에서도
     `production_candidate / watchlist`를 넘지 못했다
2. `Quality`
   - current practical point는 여전히
     `capital_discipline + LQD + trend on + regime off + Top N 12`
   - `SPY` cleaner alternative는 이번 frame에서도
     `paper_only`라서 replacement가 아니라 comparison surface로 남았다
3. `Quality + Value`
   - current strongest practical point는 여전히
     `operating_margin + pcr + por + per + Top N 10 + Candidate Universe Equal-Weight`
   - `Top N = 9` 대안은 `CAGR`와 `MDD`가 모두 매력적이지만
     `production_candidate / watchlist`로 내려가서 representative anchor는 아니다
4. 다음 phase 방향
   - Phase 21 integrated validation에서 annual strict family current anchor 3개는 모두 유지됐다
   - lower-MDD alternative들은 의미 있지만,
     representative anchor replacement까지는 아니었다
   - representative portfolio bridge는
     `33 / 33 / 34` weighted bundle에서
     `28.66% / -25.42% / Sharpe 1.51`을 기록했고,
     saved replay도 exact match로 재현됐다
   - 따라서 지금 다음 단계는
     구조 실험을 하나 더 여는 것보다
     **portfolio-level candidate construction을 여는 `Phase 22`**
     쪽이 더 자연스럽다
   - Phase 22 first baseline note:
     - `33 / 33 / 34` shorthand는 saved definition 기준
       `[33.33, 33.33, 33.33]` equal-third baseline으로 정리했다
     - `phase22_annual_strict_equal_third_baseline_v1`은
       `baseline_candidate / portfolio_watchlist / not_deployment_ready`
       상태로 유지한다
     - 즉 최종 portfolio winner가 아니라,
       이후 weight alternative와 diversified component를 비교할 기준점이다

## 관련 문서

- [PHASE16_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase16/PHASE16_CURRENT_CHAPTER_TODO.md)
- [BACKTEST_REPORT_INDEX.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/BACKTEST_REPORT_INDEX.md)
- [PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase21/PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md)
- [PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase22/PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md)
