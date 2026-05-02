# Quality + Value Strict Annual Backtest Hub

## 이 문서는 무엇인가

이 문서는 `Quality + Value > Strict Annual` 전략을 위한
**전략 허브 문서**다.

쉽게 말하면:

- blended 전략인 `Quality + Value`가
  지금 어떤 후보까지 올라왔는지
- 어떤 조합이 현재 가장 강한 practical candidate인지
- 어떤 세부 문서를 먼저 열어야 하는지

를 정리한 안내 페이지다.

## 이 문서는 무엇을 하는가

이 문서를 보면 바로 알 수 있는 것은:

- 현재 strongest practical candidate가 무엇인지
- 왜 그 후보가 strongest로 읽히는지
- 더 낮은 `MDD`지만 gate가 약한 대안이 있는지
- 관련 one-pager / log / phase report를 어디서 봐야 하는지

이다.

## 이 문서는 무엇을 하지 않는가

이 문서는:

- 모든 factor replacement 실험 과정을 하나하나 설명하는 문서가 아니다
- 세부 수치 검증 원문 전체를 대신하는 문서도 아니다
- 구현 코드 설명 문서도 아니다

세부 pass별 변화는 phase report에서,
실제 run 누적은 backtest log에서 보는 구조다.

## 전략

- family: `Quality + Value`
- variant: `Strict Annual`
- 관련 phase: `Phase 13`, `Phase 14`, `Phase 15`, `Phase 16`, `Phase 17`, `Phase 18`

## 이 전략 허브를 어떻게 읽으면 되는가

1. strongest practical candidate가 무엇인지 먼저 본다
2. 그 다음 previous anchor와 lower-drawdown alternative를 비교한다
3. 더 자세한 변경 과정을 보고 싶으면 fifth/sixth pass와 Phase 16 follow-up report를 연다
4. 실제 run 누적은 backtest log에서 본다

## 한 줄 요약

`Quality + Value`는 Phase 13 탐색에서 가장 공격적인 family는 아니었지만, 방어적 조합과 low-drawdown 탐색을 해볼 때 가장 자주 검토된 family였다.

다만:

- `MDD` 방어는 상대적으로 나았지만
- `SPY`를 확실히 이길 만큼의 `CAGR`가 부족한 경우가 많았다
- current runtime refresh에서는 default blend + candidate equal-weight benchmark 조합이
  `production_candidate / watchlist / review_required`까지 올라가는 stronger non-hold candidate로 확인됐다

쉽게 말하면:

- 처음엔 “방어적이지만 조금 심심한 전략”처럼 보였던 family다
- 그런데 Phase 15에서 factor replacement를 차근차근 붙여보니
  결국 세 family 중 가장 좋은 practical blended candidate까지 올라왔다
- 그리고 Phase 16 follow-up에서는
  더 낮은 `MDD` same-gate candidate는 못 찾았지만,
  같은 `MDD`에서 `CAGR`를 더 높이는 strongest point까지 갱신됐다
- Phase 21 integrated validation first pass에서도
  current strongest point는 유지됐고,
  `Top N = 9` alternative는 숫자는 더 좋아 보이지만 gate가 한 단계 약하다는 점이 다시 확인됐다
- 그래서 지금은
  “생각보다 강한 blended family”
  로 읽는 편이 더 맞다

## 전략 log

- [QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
  - `Quality + Value > Strict Annual`를 어떤 세팅으로 돌렸고 결과가 어땠는지 누적 관리하는 전략 log

## 대표 결과를 쉽게 읽으면

### 1. 지금 가장 강한 practical candidate

- strongest practical point
- quality:
  - `net_margin -> operating_margin`
- value:
  - `ocf_yield -> pcr`
  - `operating_income_yield -> por`
- `Top N = 10`
- `Benchmark Contract = Candidate Universe Equal-Weight`
- `CAGR = 31.82%`
- `MDD = -26.63%`
- `Promotion = real_money_candidate`
- `Shortlist = small_capital_trial`

해석:

- 지금 `Quality + Value`에서 가장 먼저 보면 되는 후보다
- blended family인데도 수익률이 강하고
- gate 상태도 좋아서
- current strongest candidate로 보기 가장 자연스럽다

### 2. 그 직전 기준점

- previous practical anchor
- `CAGR = 31.25%`
- `MDD = -26.63%`

해석:

- 이미 좋은 후보였지만
- value-side replacement를 한 번 더 하면서
  strongest practical point가 더 좋아졌다

### 3. 낙폭은 더 좋지만 gate가 약한 대안

- lower-MDD but weaker gate
- `Top N = 9`
- `CAGR = 32.21%`
- `MDD = -25.61%`
- `Promotion = production_candidate`
- `Shortlist = watchlist`

해석:

- 숫자만 보면 꽤 매력적이다
- Phase 21 frame에서는 current strongest보다 `CAGR`도 높고 `MDD`도 낮게 나왔다
- 하지만 strongest candidate보다 gate tier가 내려간다
- 그래서 “대안 후보”로는 좋지만 대표 후보를 대체하진 못한다

## 최근 backtest log snapshot

- 최근 기록:
  - `2026-04-17 - phase21 integrated validation first pass`
- 핵심 설정:
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
  - `Benchmark Contract = Candidate Universe Equal-Weight`
  - `Trend Filter = off`
  - `Market Regime = off`
  - underperformance / drawdown guardrail `on`
- 결과:
  - current strongest point:
    - `Top N = 10`
    - `CAGR = 31.82%`
    - `MDD = -26.63%`
    - `Promotion = real_money_candidate`
    - `Shortlist = small_capital_trial`
    - `Deployment = review_required`
    - `Validation / Rolling / OOS = normal / normal / normal`
  - lower-MDD alternative:
    - `Top N = 9`
    - `CAGR = 32.21%`
    - `MDD = -25.61%`
    - `Promotion = production_candidate`
    - `Shortlist = watchlist`
    - `Deployment = review_required`
    - `Validation / Rolling / OOS = watch / normal / normal`
- 실무 해석:
  - `Top N = 9`는 숫자만 보면 매우 강하다
  - 하지만 `small_capital_trial` gate를 유지하지 못하므로
    current representative anchor는 여전히 `Top N = 10`이다
- 다음에 볼 것:
  - representative portfolio bridge validation으로 이동한다

## 관련 결과 문서

- [PHASE13_QUALITY_VALUE_2016_LOW_DRAWDOWN_FACTOR_OPTION_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_QUALITY_VALUE_2016_LOW_DRAWDOWN_FACTOR_OPTION_SEARCH.md)
  - `Quality + Value` low-drawdown 핵심 탐색 문서
- [PHASE13_SPY_OUTPERFORMANCE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_SPY_OUTPERFORMANCE_SEARCH.md)
  - family 전체 `SPY` 초과 탐색
- [PHASE13_SPY_OUTPERFORMANCE_AND_MDD20_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_SPY_OUTPERFORMANCE_AND_MDD20_SEARCH.md)
  - `CAGR 15% / MDD 20%` 조건 교집합 탐색
- [PHASE13_REAL_MONEY_CANDIDATE_SPY_MDD25_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_REAL_MONEY_CANDIDATE_SPY_MDD25_SEARCH.md)
  - `real_money_candidate + SPY 초과 + MDD 25% 이내` 탐색
- [PHASE13_STRICT_ANNUAL_FAMILY_BACKTEST_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_STRICT_ANNUAL_FAMILY_BACKTEST_SUMMARY.md)
  - family 전체 summary 문서
- [PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase14/PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md)
  - current runtime 기준으로 `Quality + Value` strongest non-hold candidate를 다시 고정한 refresh 문서
- [PHASE15_QUALITY_VALUE_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md)
  - baseline blend anchor에 controlled factor addition을 붙여 current best addition candidate를 다시 본 문서
- [PHASE15_QUALITY_VALUE_VALUE_SIDE_SEARCH_THIRD_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_VALUE_SIDE_SEARCH_THIRD_PASS.md)
  - value-side removal / replacement를 다시 보고 `ocf_yield -> pcr` current strongest practical candidate를 고정한 문서
- [PHASE15_QUALITY_VALUE_QUALITY_SIDE_SEARCH_FIFTH_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_QUALITY_SIDE_SEARCH_FIFTH_PASS.md)
  - `ocf_yield -> pcr` anchor 위 quality-side replacement를 다시 보고,
    `net_margin -> operating_margin`가 strongest practical point를 갱신했는지 정리한 문서
- [PHASE15_QUALITY_VALUE_STRONGEST_ANCHOR_TOPN_SEARCH_SIXTH_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_STRONGEST_ANCHOR_TOPN_SEARCH_SIXTH_PASS.md)
  - new strongest practical point 위에서 `Top N` follow-up을 다시 보고,
    `Top N = 10`이 그대로 strongest인지 정리한 문서
- [PHASE16_QUALITY_VALUE_DOWNSIDE_REFINEMENT_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phases/phase16/PHASE16_QUALITY_VALUE_DOWNSIDE_REFINEMENT_FIRST_PASS.md)
  - same gate를 유지하면서 더 낮은 `MDD`를 만들 수 있는지,
    그리고 same `MDD`에서 `CAGR`를 더 높일 수 있는지를 본 follow-up 문서
- [QUALITY_VALUE_STRICT_ANNUAL_VALUE_REPLACEMENT_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_VALUE_REPLACEMENT_CURRENT_CANDIDATE.md)
  - `ocf_yield -> pcr` replacement candidate를 전략 구성 중심으로 바로 읽는 one-pager
- [QUALITY_VALUE_STRICT_ANNUAL_POR_REPLACEMENT_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_POR_REPLACEMENT_CURRENT_CANDIDATE.md)
  - `operating_income_yield -> por` replacement를 반영한 current strongest practical candidate one-pager
- [QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md)
  - quality/value replacement를 함께 반영한 current strongest practical candidate one-pager
- [PHASE17_DEFENSIVE_SLEEVE_RISK_OFF_REPRESENTATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase17/PHASE17_DEFENSIVE_SLEEVE_RISK_OFF_REPRESENTATIVE_RERUN_FIRST_PASS.md)
  - `defensive sleeve risk-off`를 strongest blended point에 적용해
    same-gate lower-MDD rescue가 가능한지 본 문서
- [PHASE17_CONCENTRATION_AWARE_WEIGHTING_REPRESENTATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase17/PHASE17_CONCENTRATION_AWARE_WEIGHTING_REPRESENTATIVE_RERUN_FIRST_PASS.md)
  - `concentration-aware weighting`을 strongest blended point에 적용해
    same-gate lower-MDD rescue가 가능한지 본 문서
- [PHASE18_NEXT_RANKED_FILL_REPRESENTATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase18/PHASE18_NEXT_RANKED_FILL_REPRESENTATIVE_RERUN_FIRST_PASS.md)
  - `Fill Rejected Slots With Next Ranked Names` redesign을
    strongest blended point에 적용해
    meaningful rescue 또는 gate recovery가 가능한지 본 문서

## 실무 해석

쉽게 정리하면 지금 `Quality + Value Strict Annual`은:

- blended family 중에서는 가장 잘 정리된 후보군을 가진 상태다
- strongest candidate가 이미 `small_capital_trial`까지 올라와 있어서
  실전 후보군 해석에서도 꽤 강하다
- raw winner만 놓고 보면 아직 `Value`가 더 공격적일 수 있지만,
  “성과와 gate를 같이 본 practical tradeoff”로는
  지금 `Quality + Value`가 매우 강한 위치에 있다
- Phase 16 second pass까지 반영하면
  strongest practical point는 current code에서도 그대로 유지되고,
  lower-MDD but weaker-gate 대안과 `SPY` benchmark 대안의 tradeoff까지 정리된 상태다
- Phase 21 integrated validation까지 반영하면
  `Top N = 9`는 `CAGR`와 `MDD`가 모두 매력적이지만
  gate가 `production_candidate / watchlist`로 내려가므로
  current anchor replacement는 아니다
- Phase 17 structural rerun까지 반영하면
  `partial cash retention`, `defensive sleeve`, `concentration-aware weighting`
  어느 쪽도 current strongest practical point를 대체하는 lower-MDD exact rescue는 아니었다
- Phase 18 first redesign slice까지 반영하면
  `next-ranked eligible fill`도 blended strongest point를
  non-hold까지 회복시키지는 못했다
- 즉 지금 `Quality + Value`는
  strongest practical point가 분명하고,
  larger redesign은 계속 시도할 가치가 있지만
  current first slice만으로는 anchor replacement까지는 아직 아니다

지금 다시 볼 우선순위를 한 줄로 정리하면:

1. 대표 후보 하나를 보고 싶으면
   - current strongest practical point
2. 직전 비교 기준을 보고 싶으면
   - previous practical anchor
3. 낙폭을 더 줄인 대안을 보고 싶으면
   - lower-MDD but weaker-gate candidate

즉 현재 `Quality + Value`는
“방어형 실험용 family”를 넘어,
실제로 가장 잘 다듬어진 blended candidate family
라고 이해하는 편이 맞다.
