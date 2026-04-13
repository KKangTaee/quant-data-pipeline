# Quality + Value Strict Annual Backtest Hub

## 전략

- family: `Quality + Value`
- variant: `Strict Annual`
- 관련 phase: `Phase 13`, `Phase 14`, `Phase 15`

## 한 줄 요약

`Quality + Value`는 Phase 13 탐색에서 가장 공격적인 family는 아니었지만, 방어적 조합과 low-drawdown 탐색을 해볼 때 가장 자주 검토된 family였다.

다만:

- `MDD` 방어는 상대적으로 나았지만
- `SPY`를 확실히 이길 만큼의 `CAGR`가 부족한 경우가 많았다
- current runtime refresh에서는 default blend + candidate equal-weight benchmark 조합이
  `production_candidate / watchlist / review_required`까지 올라가는 stronger non-hold candidate로 확인됐다

## 지금 어떻게 읽으면 되는가

1. low-drawdown 탐색 문서를 먼저 본다
2. family summary에서 `Value`와 비교한다
3. 필요하면 `SPY` 비교 문서로 넘어간다

## 전략 log

- [QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
  - `Quality + Value > Strict Annual`를 어떤 세팅으로 돌렸고 결과가 어땠는지 누적 관리하는 전략 log

## 대표 결과

- strongest theme:
  - low-drawdown / defensive factor blend 탐색
- current takeaway:
  - 방어형 실험에는 여전히 의미가 있다
  - baseline default blend 위에 value-side addition을 붙이면
    gate를 실제로 더 올릴 수 있다
  - bounded one-factor addition 중에서는 `per`가 current best practical candidate였다
  - `Top N` downside search까지 보면, 현재도 `Top N = 10 + per`가 strongest practical point로 남는다
  - benchmark / quality-side pruning second pass까지 봐도
    baseline candidate-equal-weight 계약이 strongest practical point로 유지됐다
  - 하지만 value-side third pass에서는
    `ocf_yield -> pcr` replacement가 same gate / same MDD로 `CAGR`를 더 올리며
    current strongest practical point가 됐다
  - replacement-anchor follow-up fourth pass까지 보면
    그 practical point 위에서도 `Top N = 10 + Candidate Universe Equal-Weight`가 그대로 strongest였다
  - 그리고 quality-side fifth pass에서는
    `net_margin -> operating_margin` replacement가
    same gate를 유지하면서 `CAGR`와 `MDD`를 같이 더 개선했다
  - sixth pass에서 new anchor 기준 `Top N`을 다시 봐도
    `Top N = 10`이 strongest practical point로 유지됐다

## 최근 backtest log snapshot

- 최근 기록:
  - `2026-04-13 - strongest-anchor top-n search sixth pass`
- 핵심 설정:
  - quality replacement:
    - `net_margin -> operating_margin`
  - value replacement:
    - `ocf_yield -> pcr`
  - `Top N = 10`
  - `Rebalance Interval = 1`
  - `Trend Filter = off`
  - `Market Regime = off`
- 결과:
  - strongest practical candidate:
    - quality:
      - `net_margin -> operating_margin`
    - value:
      - `ocf_yield -> pcr`
    - `Benchmark Contract = Candidate Universe Equal-Weight`
    - `Top N = 10`
    - `CAGR = 31.25%`
    - `MDD = -26.63%`
    - `Promotion = real_money_candidate`
    - `Shortlist = small_capital_trial`
    - `Deployment = review_required`
  - previous practical anchor:
    - `Top N = 10`
    - `CAGR = 30.05%`
    - `MDD = -27.43%`
    - `Promotion = real_money_candidate`
    - `Shortlist = small_capital_trial`
  - lower-MDD but weaker gate:
    - `current_ratio -> operating_margin`
    - `CAGR = 30.84%`
    - `MDD = -24.09%`
    - `Promotion = production_candidate`
    - `Shortlist = watchlist`
- 다음에 볼 것:
  - strongest practical point와 lower-drawdown weaker-gate 대안을
    Phase 15 checklist 기준으로 다시 검수
  - next phase에서
    candidate consolidation 또는 downside follow-up 중 무엇을 먼저 할지 결정

## 관련 결과 문서

- [PHASE13_QUALITY_VALUE_2016_LOW_DRAWDOWN_FACTOR_OPTION_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_QUALITY_VALUE_2016_LOW_DRAWDOWN_FACTOR_OPTION_SEARCH.md)
  - `Quality + Value` low-drawdown 핵심 탐색 문서
- [PHASE13_SPY_OUTPERFORMANCE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_SPY_OUTPERFORMANCE_SEARCH.md)
  - family 전체 `SPY` 초과 탐색
- [PHASE13_SPY_OUTPERFORMANCE_AND_MDD20_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_SPY_OUTPERFORMANCE_AND_MDD20_SEARCH.md)
  - `CAGR 15% / MDD 20%` 조건 교집합 탐색
- [PHASE13_REAL_MONEY_CANDIDATE_SPY_MDD25_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_REAL_MONEY_CANDIDATE_SPY_MDD25_SEARCH.md)
  - `real_money_candidate + SPY 초과 + MDD 25% 이내` 탐색
- [PHASE13_STRICT_ANNUAL_COVERAGE300_500_1000_TARGET_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_STRICT_ANNUAL_COVERAGE300_500_1000_TARGET_SEARCH.md)
  - wider coverage가 방어형 family에 주는 효과를 같이 확인한 문서
- [PHASE13_STRICT_ANNUAL_FAMILY_BACKTEST_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_STRICT_ANNUAL_FAMILY_BACKTEST_SUMMARY.md)
  - family 전체 summary 문서
- [PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase14/PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md)
  - current runtime 기준으로 `Quality + Value` strongest non-hold candidate를 다시 고정한 refresh 문서
- [PHASE15_QUALITY_VALUE_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md)
  - baseline blend anchor에 controlled factor addition을 붙여 current best addition candidate를 다시 본 문서
- [QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md)
  - `per` addition candidate를 전략 구성 중심으로 바로 읽는 one-pager
- [PHASE15_QUALITY_VALUE_PER_DOWNSIDE_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_PER_DOWNSIDE_SEARCH_FIRST_PASS.md)
  - `per` strongest candidate를 anchor로 `Top N` downside search를 다시 본 문서
- [PHASE15_QUALITY_VALUE_PER_BENCHMARK_AND_PRUNING_SEARCH_SECOND_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_PER_BENCHMARK_AND_PRUNING_SEARCH_SECOND_PASS.md)
  - `per` strongest candidate를 anchor로 benchmark sensitivity와 quality-side pruning을 다시 본 문서
- [PHASE15_QUALITY_VALUE_VALUE_SIDE_SEARCH_THIRD_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_VALUE_SIDE_SEARCH_THIRD_PASS.md)
  - value-side removal / replacement를 다시 보고 `ocf_yield -> pcr` current strongest practical candidate를 고정한 문서
- [PHASE15_QUALITY_VALUE_REPLACEMENT_ANCHOR_FOLLOWUP_FOURTH_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_REPLACEMENT_ANCHOR_FOLLOWUP_FOURTH_PASS.md)
  - `ocf_yield -> pcr` current strongest practical point 위에서 `Top N / benchmark` follow-up을 다시 본 문서
- [PHASE15_QUALITY_VALUE_QUALITY_SIDE_SEARCH_FIFTH_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_QUALITY_SIDE_SEARCH_FIFTH_PASS.md)
  - `ocf_yield -> pcr` anchor 위 quality-side replacement를 다시 보고,
    `net_margin -> operating_margin`가 strongest practical point를 갱신했는지 정리한 문서
- [PHASE15_QUALITY_VALUE_STRONGEST_ANCHOR_TOPN_SEARCH_SIXTH_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_STRONGEST_ANCHOR_TOPN_SEARCH_SIXTH_PASS.md)
  - new strongest practical point 위에서 `Top N` follow-up을 다시 보고,
    `Top N = 10`이 그대로 strongest인지 정리한 문서
- [QUALITY_VALUE_STRICT_ANNUAL_VALUE_REPLACEMENT_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_VALUE_REPLACEMENT_CURRENT_CANDIDATE.md)
  - `ocf_yield -> pcr` replacement candidate를 전략 구성 중심으로 바로 읽는 one-pager
- [QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md)
  - quality/value replacement를 함께 반영한 current strongest practical candidate one-pager

## 실무 해석

지금 시점의 `Quality + Value Strict Annual`은:

- low-drawdown 연구 reference
- 방어형 factor blend 실험용 family
- 그리고 current runtime 기준으로는
  `real_money_candidate / small_capital_trial / review_required`
  까지 올라가는 strongest blended candidate family

로 보는 편이 맞고, raw winner 기준으로는 아직 `Value`보다 뒤에 있다.
Phase 15 bounded addition search 기준으로는
`per`가 `real_money_candidate / small_capital_trial / review_required`까지 올라가며
current strongest practical blended candidate가 되었다.
그리고 value-side third pass까지 보면
현재 strongest practical point는
`Top N = 10 + per`, 단 `ocf_yield -> pcr` replacement를 적용한 조합이었다.
그리고 replacement-anchor follow-up fourth pass까지 보면
그 point 위에서 `Top N`이나 benchmark를 다시 바꿔도 stronger practical point는 나오지 않았다.
다만 quality-side fifth pass에서는
`net_margin -> operating_margin` replacement가
`CAGR = 31.25% / MDD = -26.63% / real_money_candidate / small_capital_trial / review_required`
로 same gate를 유지하면서 더 나은 tradeoff를 만들어,
현재 strongest practical point는
quality-side `net_margin -> operating_margin`,
value-side `ocf_yield -> pcr`,
`Top N = 10 + Candidate Universe Equal-Weight`
조합으로 읽는 편이 맞다.
그리고 sixth pass에서 `Top N`을 8~12까지 다시 흔들어봐도,
`Top N = 10`이 여전히 strongest practical point로 유지됐다.
