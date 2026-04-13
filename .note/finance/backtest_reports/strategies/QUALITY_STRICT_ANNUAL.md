# Quality Strict Annual Backtest Hub

## 이 문서는 무엇인가

이 문서는 `Quality > Strict Annual` 전략을 위한
**전략 허브 문서**다.

쉽게 말하면:

- `Quality` 전략이 지금 어떤 상태인지
- 다시 볼 만한 후보가 있는지
- 어떤 결과 문서를 먼저 열어야 하는지

를 한 번에 정리한 안내 페이지다.

## 이 문서는 무엇을 하는가

이 문서를 보면 바로 알 수 있는 것은:

- `Quality` 전략이 왜 중요하게 봐야 하는 family인지
- 현재 strongest practical candidate가 무엇인지
- downside-improved candidate가 무엇인지
- 어떤 문서를 다음으로 보면 되는지

이다.

## 이 문서는 무엇을 하지 않는가

이 문서는:

- 모든 탐색 과정을 시간순으로 자세히 보여주는 문서가 아니다
- 코드 구현 설명 문서가 아니다
- 세부 실험 원문 전체를 대신하는 문서도 아니다

세부 탐색 흐름은 phase report에서 보고,
실제 run 누적은 backtest log에서 보는 구조다.

## 전략

- family: `Quality`
- variant: `Strict Annual`
- 관련 phase: `Phase 13`, `Phase 14`, `Phase 15`

## 이 전략 허브를 어떻게 읽으면 되는가

1. 먼저 `Quality`가 현재 rescue된 상태인지 확인한다
2. strongest practical point와 downside-improved candidate를 구분해 본다
3. 더 자세한 이유가 필요하면 structural rescue / downside / alternate contract report를 연다
4. 실제 run 누적은 backtest log에서 본다

## 한 줄 요약

`Quality` 단독 family는 Phase 13 탐색에서는 `SPY` dominance와 non-hold exact-hit를 동시에 만족시키는 대표 후보를 만들지 못했다.
Phase 14 refresh에서는 한때 `production_candidate / watchlist / review_required` 후보가 보였고,
Phase 15 first pass에서는 bounded addition만으로는 다시 `hold`를 못 벗어났다.
하지만 Phase 15 structural rescue second pass에서는
`LQD + trend on + regime off + capital_discipline` 조합이
`real_money_candidate / paper_probation / review_required`까지 회복됐다.
그리고 rescued anchor downside search first pass에서는
`Top N = 12`가
`CAGR = 26.02% / MDD = -25.57%`
로 current recommended downside-improved candidate가 됐다.
그 다음 alternate contract third pass에서는
`SPY + trend on + regime off + Top N 12`
가
`CAGR = 25.18% / MDD = -25.57% / paper_only`
인 cleaner alternative라는 점까지 정리됐다.

즉:

- 품질 factor 조합 실험의 reference로는 의미가 있고
- strict annual family 중 최강 후보는 아니지만
- current practical contract 기준으로도
  다시 살릴 수 있는 구조 조합이 확인된 family다

쉽게 말하면:

- `Quality`는 처음엔 “좋은 후보가 잘 안 나오는 family”처럼 보였다
- factor를 조금 바꾸는 정도로는 잘 안 풀렸다
- 하지만 benchmark와 overlay 같은 구조를 같이 조정하니
  다시 실전 후보 수준까지 올라오는 조합을 찾을 수 있었다
- 그래서 지금은
  “약한 family”라기보다
  “구조를 잘 잡아야 살아나는 family”
  로 이해하는 편이 맞다

## 전략 log

- [QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md)
  - `Quality > Strict Annual`를 어떤 세팅으로 돌렸고 결과가 어땠는지 누적 관리하는 전략 log

## 대표 결과를 쉽게 읽으면

### 1. 이 family를 다시 살린 기준 조합

- strongest practical point
- `LQD + trend on + regime off + Top N 12`
- factor theme:
  - `capital_discipline`
- `CAGR = 26.02%`
- `MDD = -25.57%`
- `Promotion = real_money_candidate`

해석:

- `Quality`는 factor만 조금 바꾸는 것으로는 잘 안 풀렸고
- benchmark와 overlay 구조를 같이 조정했을 때 usable candidate가 나왔다
- 그래서 이 조합이 지금 `Quality`의 기준점 역할을 한다

### 2. 더 깔끔하게 읽히는 대안

- cleaner alternative
- `SPY + trend on + regime off + Top N 12`
- `CAGR = 25.18%`
- `MDD = -25.57%`
- `Deployment = paper_only`

해석:

- 수익률은 조금 약해진다
- 대신 `Validation / Rolling / OOS`가 더 깔끔하게 읽힌다
- 그래서 “실무 해석이 더 쉬운 대안”으로 같이 참고할 가치가 있다

### 3. 잘 안 됐던 방향

- rejected defensive variant
- `CAGR = 17.30%`
- `MDD = -35.84%`
- `Promotion = hold`

해석:

- 더 방어적으로 가면 좋아질 것 같았지만
- 실제로는 성과도 약해지고 gate도 무너졌다
- 즉 `Quality`는 무조건 더 보수적으로 만든다고 좋아지는 family가 아니다

## 최근 backtest log snapshot

- 최근 기록:
  - `2026-04-13 - rescued anchor alternate contract search third pass`
- 핵심 설정:
  - `capital_discipline`:
    - `roe`
    - `roa`
    - `cash_ratio`
    - `debt_to_assets`
  - `Benchmark = LQD`
  - `Trend Filter = on`
  - `Market Regime = off`
  - `Top N = 12`
  - `Rebalance Interval = 1`
- 결과:
  - strongest practical point:
    - `Benchmark = LQD`
    - `Trend Filter = on`
    - `Market Regime = off`
    - `CAGR = 26.02%`
    - `MDD = -25.57%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
    - `Validation / Rolling / OOS = normal / watch / normal`
  - cleaner alternative:
    - `Benchmark = SPY`
    - `Trend Filter = on`
    - `Market Regime = off`
    - `CAGR = 25.18%`
    - `MDD = -25.57%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = paper_only`
    - `Validation / Rolling / OOS = normal / normal / normal`
  - rejected defensive variant:
    - `Benchmark = LQD`
    - `Trend Filter = off`
    - `Market Regime = off`
    - `CAGR = 17.30%`
    - `MDD = -35.84%`
    - `Promotion = hold`
    - `Shortlist = hold`
    - `Deployment = blocked`
- 다음에 볼 것:
  - rescued baseline과 downside-improved candidate를
    Phase 15 checklist 기준으로 다시 검수
  - next phase에서
    weighting / replacement / operator shortlist 연결 중 어디를 먼저 볼지 결정

## 추천 reference point

- strongest practical point:
  - `LQD + trend on + regime off + Top N 12`
  - `CAGR = 26.02%`
  - `MDD = -25.57%`
  - `real_money_candidate / paper_probation / review_required`
- cleaner alternative:
  - `SPY + trend on + regime off + Top N 12`
  - `CAGR = 25.18%`
  - `MDD = -25.57%`
  - `real_money_candidate / paper_probation / paper_only`

## 관련 결과 문서

- [PHASE13_QUALITY_STRICT_SPY_DOMINANCE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_QUALITY_STRICT_SPY_DOMINANCE_SEARCH.md)
  - `Quality`만으로 `SPY`를 동시에 이길 수 있는지 본 핵심 문서
- [PHASE13_SPY_OUTPERFORMANCE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_SPY_OUTPERFORMANCE_SEARCH.md)
  - strict annual family 전체를 `SPY` 기준으로 비교한 문서
- [PHASE13_SPY_OUTPERFORMANCE_AND_MDD20_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_SPY_OUTPERFORMANCE_AND_MDD20_SEARCH.md)
  - `CAGR 15% / MDD 20%` 조건까지 넣었을 때 family 비교 결과
- [PHASE13_REAL_MONEY_CANDIDATE_SPY_MDD25_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_REAL_MONEY_CANDIDATE_SPY_MDD25_SEARCH.md)
  - `real_money_candidate + SPY 초과 + MDD 25% 이내` 조건 탐색
- [PHASE13_STRICT_ANNUAL_COVERAGE300_500_1000_TARGET_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_STRICT_ANNUAL_COVERAGE300_500_1000_TARGET_SEARCH.md)
  - coverage 확대가 `Quality` family에도 의미가 있었는지 확인하는 공통 문서
- [PHASE13_STRICT_ANNUAL_FAMILY_BACKTEST_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_STRICT_ANNUAL_FAMILY_BACKTEST_SUMMARY.md)
  - family 전체를 한 장으로 요약한 summary 문서
- [PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase14/PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md)
  - Phase 14 current runtime 기준으로 `Quality` current best non-hold candidate를 다시 고정한 refresh 문서
- [PHASE15_QUALITY_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md)
  - strict annual dynamic PIT preset semantics를 literal하게 맞춘 뒤,
    `Quality` bounded addition search가 왜 non-hold를 못 회복했는지 정리한 문서
- [PHASE15_QUALITY_STRUCTURAL_RESCUE_SEARCH_SECOND_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_STRUCTURAL_RESCUE_SEARCH_SECOND_PASS.md)
  - `benchmark / overlay` 구조를 조정해 `Quality` current rescued candidate를 다시 확보한 문서
- [PHASE15_QUALITY_RESCUED_ANCHOR_DOWNSIDE_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_RESCUED_ANCHOR_DOWNSIDE_SEARCH_FIRST_PASS.md)
  - rescued anchor 기준 `Top N / Rebalance Interval` downside search를 다시 본 문서
- [PHASE15_QUALITY_RESCUED_ANCHOR_FACTOR_SEARCH_SECOND_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_RESCUED_ANCHOR_FACTOR_SEARCH_SECOND_PASS.md)
  - rescued anchor 위 bounded factor addition / replacement를 다시 붙였지만 baseline을 못 넘었다는 점을 정리한 문서
- [PHASE15_QUALITY_ALTERNATE_CONTRACT_SEARCH_THIRD_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_ALTERNATE_CONTRACT_SEARCH_THIRD_PASS.md)
  - rescued anchor downside-improved candidate를 유지한 채 `benchmark / overlay` alternate contract를 다시 보고,
    strongest practical point와 cleaner alternative를 함께 정리한 문서
- [QUALITY_STRICT_ANNUAL_RESCUED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_RESCUED_CURRENT_CANDIDATE.md)
  - current rescued candidate를 전략 구성 중심으로 바로 읽는 one-pager
- [QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md)
  - rescued anchor보다 `MDD`를 크게 낮춘 `Quality` downside-improved current candidate one-pager

## 실무 해석

쉽게 정리하면 지금 `Quality Strict Annual`은:

- 세 family 중 가장 강한 winner는 아니다
- 대신 “quality 계열을 어떤 구조로 살릴 수 있는지”를 보여주는 기준 family다
- 즉 단독 절대 강자라기보다,
  구조 조정이 왜 중요한지를 보여주는 reference family에 가깝다

지금 이 family를 보는 이유는:

1. `Quality`도 아예 불가능한 건 아니라는 점
2. factor보다 benchmark / overlay 구조가 더 중요할 수 있다는 점
3. `Value`, `Quality + Value`와 비교할 때
   quality-only family의 성격을 이해하는 기준점이 된다는 점

그래서 현재 `Quality`는
“무조건 1순위 후보”라기보다,
“살아 있는 후보가 있고,
quality-only 전략을 해석할 때 꼭 봐야 하는 기준 family”
라고 이해하면 자연스럽다.
