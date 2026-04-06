# PHASE13_STRICT_ANNUAL_FAMILY_BACKTEST_SUMMARY

## 목적

Phase 13 동안 `Quality`, `Value`, `Quality + Value` strict annual family를 대상으로 진행한 주요 백테스트 탐색 결과를 한 문서로 묶는다.

이 문서는 다음 질문에 빠르게 답하기 위한 요약본이다.

- 어떤 family가 가장 강했는가
- 어떤 family가 drawdown 방어에 더 유리했는가
- 왜 좋은 숫자가 나와도 `hold`가 남았는가
- 지금 UI에서 다시 확인해볼 대표 설정은 무엇인가

## 범위

이번 요약은 주로 다음 조건 아래에서 진행한 탐색을 묶는다.

- variant: `Strict Annual`
- `Universe Contract = Historical Dynamic PIT Universe`
- 비교 구간: 대체로 `2016-01-01 ~ 2026-04-01`
- 실전형 계약:
  - `Minimum Price = 5.0`
  - `Minimum History = 12M`
  - `Min Avg Dollar Volume 20D = 5.0M`
  - `Transaction Cost = 10 bps`

모든 문서가 완전히 같은 계약을 쓰지는 않았지만, Phase 13의 핵심 판단은 위 실전형 조건을 중심으로 읽는 것이 맞다.

## 기준선

가장 자주 사용한 비교 기준은 `SPY`였다.

- 구간: `2016-01-04 ~ 2026-04-01`
- `CAGR = 14.09%`
- `MDD = -33.72%`

즉 이번 탐색에서 자주 쓴 질문은 사실상 이것이었다.

- `SPY`보다 수익률이 높은가
- `SPY`보다 drawdown이 더 얕은가
- 그리고도 `hold`가 아닌가

## Family별 요약

### 1. Quality Strict Annual

관련 문서:

- `PHASE13_QUALITY_STRICT_SPY_DOMINANCE_SEARCH.md`
- `PHASE13_SPY_OUTPERFORMANCE_SEARCH.md`
- `PHASE13_SPY_OUTPERFORMANCE_AND_MDD20_SEARCH.md`

핵심 결과:

- `Quality`는 raw performance 기준으로는 `SPY`를 넘는 후보가 있었다.
- 다만 full hardening 기준으로 다시 읽으면 대부분 `hold`가 남았다.
- 즉 `Quality`는 연구 관점에서는 의미가 있지만, 현재 계약에서는 아직 실전 승격이 빡빡한 family였다.

대표 후보:

1. `capital_discipline`
   - factors: `roe`, `roa`, `cash_ratio`, `debt_to_assets`
   - `month_end / rebalance_interval = 1 / top_n = 10`
   - `trend_filter = on`, `market_regime = on`
   - `benchmark = SPY`
   - `CAGR = 15.80%`
   - `MDD = -27.97%`
   - `promotion = hold`

2. `balance_sheet`
   - factors: `current_ratio`, `cash_ratio`, `debt_to_assets`, `debt_ratio`
   - `month_end / rebalance_interval = 1 / top_n = 5`
   - `CAGR = 15.71%`
   - `MDD = -33.20%`
   - `promotion = hold`

한 줄 해석:

- `Quality`는 `SPY`를 이기는 raw candidate는 만들 수 있었지만,
  현재 promotion / validation 기준에서는 아직 보수적으로 막히는 경우가 많았다.

### 2. Value Strict Annual

관련 문서:

- `PHASE13_SPY_OUTPERFORMANCE_SEARCH.md`
- `PHASE13_SPY_OUTPERFORMANCE_AND_MDD20_SEARCH.md`
- `PHASE13_VALUE_STRICT_SPY_TARGET_SEARCH.md`
- `PHASE13_VALUE_STRICT_CAGR15_MDD20_SEARCH.md`
- `PHASE13_VALUE_STRICT_HOLD_FREE_SEARCH.md`
- `PHASE13_CAGR20_MDD25_HOLD_FREE_SEARCH.md`
- `PHASE13_HOLD_DIAGNOSTIC_AND_NONHOLD_NEAR_MISS_SEARCH.md`

핵심 결과:

- `Value`는 세 family 중 가장 강했다.
- `SPY`를 수익률과 drawdown 양쪽에서 동시에 이기는 후보가 가장 많이 나왔다.
- 다만 수치가 좋아도 `validation` 계층 때문에 `hold`가 남는 경우가 반복되었다.

대표 후보 1: 가장 강한 raw winner

- factors:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `ocf_yield`
  - `operating_income_yield`
- `month_end / rebalance_interval = 1 / top_n = 10`
- `trend_filter = off`
- `market_regime = off`
- `CAGR = 29.89%`
- `MDD = -29.15%`
- `promotion = real_money_candidate`

대표 후보 2: 가장 균형 잡힌 exact-hit

- factors:
  - `earnings_yield`
  - `ocf_yield`
  - `operating_income_yield`
  - `fcf_yield`
- `month_end / rebalance_interval = 1 / top_n = 9`
- `benchmark = SPY`
- `trend_filter = on`
- `market_regime = on`
- `underperformance_guardrail = on`
- `drawdown_guardrail = on`
- `CAGR = 15.84%`
- `MDD = -17.42%`
- `promotion = hold`

대표 후보 3: 더 공격적인 near-miss

- default value factors
- `month_end / rebalance_interval = 1 / top_n = 10`
- `benchmark = SPY`
- `trend_filter = on`
- `market_regime = on`
- `CAGR = 18.81%`
- `MDD = -23.71%`
- `promotion = hold`

한 줄 해석:

- `Value Strict Annual`은 현재 strict annual family 중 가장 유망한 축이다.
- 성과 숫자는 가장 좋았지만, 실전 승격 여부는 여전히 `validation` 계층이 가장 큰 병목이었다.

### 3. Quality + Value Strict Annual

관련 문서:

- `PHASE13_SPY_OUTPERFORMANCE_SEARCH.md`
- `PHASE13_SPY_OUTPERFORMANCE_AND_MDD20_SEARCH.md`
- `PHASE13_QUALITY_VALUE_2016_LOW_DRAWDOWN_FACTOR_OPTION_SEARCH.md`
- `PHASE13_HOLD_DIAGNOSTIC_AND_NONHOLD_NEAR_MISS_SEARCH.md`

핵심 결과:

- `Quality + Value`는 drawdown을 낮추는 쪽에서는 가장 방어적이었다.
- 하지만 CAGR이 빠르게 약해졌다.
- 즉 `Quality + Value`는 공격적인 alpha family라기보다, 방어형 reference 또는 watchlist candidate 성격이 더 강했다.

대표 후보 1: 가장 낮은 drawdown

- quality set:
  - `current_ratio`, `cash_ratio`, `debt_to_assets`, `debt_ratio`
- value set:
  - `ocf_yield`, `fcf_yield`, `pcr`, `pfcr`
- `month_end / rebalance_interval = 6 / top_n = 30`
- `benchmark = Candidate Universe Equal-Weight`
- `CAGR = 2.40%`
- `MDD = -13.57%`
- `promotion = hold`

대표 후보 2: 가장 나은 non-hold defensive case

- 같은 factor 구조
- `month_end / rebalance_interval = 6 / top_n = 30`
- `benchmark = LQD`
- `CAGR = 5.89%`
- `MDD = -19.76%`
- `promotion = production_candidate`
- `shortlist = watchlist`

대표 후보 3: 조정 후 non-hold 방어형

- 같은 factor 구조
- `month_end / rebalance_interval = 6 / top_n = 40` 또는 `50`
- `benchmark = LQD`
- `CAGR ≈ 5.48%`
- `MDD ≈ -18.91%`
- `promotion = production_candidate`

한 줄 해석:

- `Quality + Value`는 `hold`를 피하는 defensive candidate는 만들 수 있었지만,
  강한 CAGR까지 같이 가져오기는 어려웠다.

## 공통으로 반복된 hold 원인

가장 자주 반복된 원인은 `benchmark`나 `liquidity`보다 `validation` 계층이었다.

특히 `Value Strict Annual`의 가장 강한 exact-hit 후보에서 확인된 직접 원인은 다음이었다.

- `validation_status = caution`
- `validation_policy_status = caution`
- `rolling_review_status = caution`

대표 메타:

- `rolling_underperformance_share = 36.6%`
- `rolling_underperformance_worst_excess_return = -39.4%`

쉽게 말하면:

- 전체 수익률과 전체 drawdown은 좋아도
- 특정 rolling 구간에서 benchmark 대비 너무 크게 밀린 적이 있어서
- promotion 단계에서 `hold`가 걸리는 구조였다.

## 지금까지의 practical ranking

### 성과 중심 ranking

1. `Value`
2. `Quality`
3. `Quality + Value`

### 저낙폭 중심 ranking

1. `Quality + Value`
2. `Value`
3. `Quality`

### 실전 승격 가능성 해석

1. `Value`
   - 가장 강한 후보가 많고, 추가 정책 조정 여지가 가장 크다.
2. `Quality + Value`
   - low-drawdown watchlist 용도로는 의미가 있다.
3. `Quality`
   - raw edge는 있으나 현재 hardening 계약에서는 아직 더 보수적이다.

## 다시 확인해볼 대표 설정

### A. Value family의 가장 강한 exact-hit reference

- family: `Value > Strict Annual`
- factors:
  - `earnings_yield`
  - `ocf_yield`
  - `operating_income_yield`
  - `fcf_yield`
- `Historical Dynamic PIT Universe`
- `2016-01-01 ~ 2026-04-01`
- `month_end / rebalance_interval = 1 / top_n = 9`
- `benchmark = SPY`
- `trend_filter = on`
- `market_regime = on`
- `underperformance_guardrail = on`
- `drawdown_guardrail = on`
- 결과:
  - `CAGR = 15.84%`
  - `MDD = -17.42%`
  - `promotion = hold`

### B. Value family의 가장 강한 raw winner

- family: `Value > Strict Annual`
- default value factors
- `Historical Dynamic PIT Universe`
- `month_end / rebalance_interval = 1 / top_n = 10`
- `trend_filter = off`
- `market_regime = off`
- 결과:
  - `CAGR = 29.89%`
  - `MDD = -29.15%`
  - `promotion = real_money_candidate`

### C. Quality + Value family의 가장 강한 방어형 reference

- family: `Quality + Value > Strict Annual`
- quality set:
  - `current_ratio`, `cash_ratio`, `debt_to_assets`, `debt_ratio`
- value set:
  - `ocf_yield`, `fcf_yield`, `pcr`, `pfcr`
- `Historical Dynamic PIT Universe`
- `month_end / rebalance_interval = 6 / top_n = 30`
- `benchmark = LQD`
- 결과:
  - `CAGR = 5.89%`
  - `MDD = -19.76%`
  - `promotion = production_candidate`

## 최종 결론

지금까지 Phase 13에서 진행한 strict annual family 백테스트를 한 줄로 요약하면 다음과 같다.

1. `Value Strict Annual`이 가장 강한 family였다.
2. `Quality Strict Annual`은 raw candidate는 괜찮았지만 hardening 기준에서 아직 막히는 경우가 많았다.
3. `Quality + Value Strict Annual`은 drawdown을 낮추는 데는 유리했지만 CAGR 희생이 컸다.
4. 가장 큰 병목은 현재 `validation / promotion` 계층이며, raw return 자체보다 rolling underperformance가 더 자주 문제를 만들었다.

즉 앞으로 이 family들을 계속 다룰 때의 기본 해석은 이렇게 두면 된다.

- 공격적 후보를 찾을 때: `Value`부터 본다
- 방어적 후보를 찾을 때: `Quality + Value`를 본다
- `hold` 원인을 풀고 싶을 때: `validation`과 `rolling review`부터 본다
