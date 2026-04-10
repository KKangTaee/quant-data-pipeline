# PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH

## 목적

Phase 14 calibration / reference 보강 이후,
`Quality`, `Value`, `Quality + Value` strict annual family를 current runtime으로 다시 돌려
아래 관점에서 현재 가장 유망한 candidate를 다시 고정한다.

- `Promotion = real_money_candidate`에 얼마나 가까운가
- `Shortlist >= paper_probation`에 얼마나 가까운가
- `Deployment Readiness != blocked`를 만족하는가

## 공통 실행 계약

이번 refresh는 user-facing practical contract를 기준으로 맞췄다.

- preset: `US Statement Coverage 100`
- `Universe Contract = Historical Dynamic PIT Universe`
- `Start Date = 2016-01-01`
- `End Date = 2026-04-01`
- `Option = month_end`
- `Minimum Price = 5.0`
- `Minimum History = 12M`
- `Min Avg Dollar Volume 20D = 5.0M`
- `Transaction Cost = 10 bps`
- `Underperformance Guardrail = on`
- `Drawdown Guardrail = on`

즉 이번 문서는
runtime 기본값(`history=0`, `liquidity=0`)이 아니라,
실제로 `Real-Money Contract`를 켠 상태에 가까운 practical search refresh다.

## 탐색 범위

이번 refresh는 무작정 큰 격자 탐색 대신,
Phase 13 / Phase 14에서 의미가 있었던 candidate와 그 주변 조합만 bounded하게 다시 확인했다.

- `Value`: 4개 조합
- `Quality`: 5개 조합
- `Quality + Value`: 5개 조합

총 `14`개 current rerun을 기준으로 family별 best case를 다시 고정했다.

## 결과 한눈에 보기

| Family | 대표 후보 | Promotion | Shortlist | Deployment | CAGR | MDD |
| --- | --- | --- | --- | --- | --- | --- |
| `Value` | `v_default_spy` | `real_money_candidate` | `paper_probation` | `review_required` | `29.89%` | `-29.15%` |
| `Quality + Value` | `qv_default_candidate_eq` | `production_candidate` | `watchlist` | `review_required` | `28.51%` | `-28.35%` |
| `Quality` | `q_capital_discipline_lqd` | `production_candidate` | `watchlist` | `review_required` | `14.84%` | `-27.97%` |

한 줄 결론:

- 이번 refresh 기준 exact hit는 `Value` family 하나다.
- `Quality + Value`는 non-hold까지는 안정적으로 올라오지만 아직 `paper_probation`은 아니다.
- `Quality`도 bounded search 안에서 `hold`를 벗어난 candidate가 하나 나왔지만, 아직 `production_candidate / watchlist` 수준이다.

## 1. Value Strict Annual

### best candidate

- name: `v_default_spy`
- factors:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `ocf_yield`
  - `operating_income_yield`
- `Top N = 10`
- `Rebalance Interval = 1`
- `Benchmark Contract = Ticker Benchmark`
- `Benchmark Ticker = SPY`
- `Trend Filter = off`
- `Market Regime = off`

### 결과

- `Promotion = real_money_candidate`
- `Shortlist = paper_probation`
- `Deployment = review_required`
- `Validation = normal`
- `Validation Policy = normal`
- `Benchmark Policy = normal`
- `Liquidity Policy = normal`
- `Guardrail Policy = normal`
- `Rolling Review = watch`
- `Out-of-Sample Review = caution`
- `CAGR = 29.89%`
- `MDD = -29.15%`

### 해석

- 현재 세 family 중
  **사용자 조건에 가장 가까운 exact hit**
  는 여전히 이 후보다.
- `paper_probation`까지는 올라갔고,
  `deployment`도 `blocked`가 아니다.
- 다만 `review_required`인 이유는
  최근/후반부 consistency review가 완전히 깨끗하진 않기 때문이다.

### 참고 near miss

- `v_default_liquidation_spy`
  - `Promotion = production_candidate`
  - `Shortlist = watchlist`
  - `Deployment = review_required`
  - `CAGR = 34.65%`
  - `MDD = -30.18%`

즉 `liquidation_value`를 더한 공격형 value 조합은 숫자는 더 강했지만,
현재 gate 해석에서는 `real_money_candidate`까지는 못 올라갔다.

## 2. Quality Strict Annual

### best current non-hold candidate

- name: `q_capital_discipline_lqd`
- factors:
  - `roe`
  - `roa`
  - `cash_ratio`
  - `debt_to_assets`
- `Top N = 10`
- `Rebalance Interval = 1`
- `Benchmark Contract = Ticker Benchmark`
- `Benchmark Ticker = LQD`
- `Trend Filter = on`
- `Market Regime = on`

### 결과

- `Promotion = production_candidate`
- `Shortlist = watchlist`
- `Deployment = review_required`
- `Validation = watch`
- `Validation Policy = normal`
- `Benchmark Policy = normal`
- `Liquidity Policy = normal`
- `Guardrail Policy = normal`
- `Rolling Review = normal`
- `Out-of-Sample Review = normal`
- `CAGR = 14.84%`
- `MDD = -27.97%`

### 해석

- bounded practical search 안에서는
  `Quality`도 이제 `hold`를 벗어난 current candidate가 하나 있다.
- 다만 아직
  - `real_money_candidate`는 아니고
  - `paper_probation`도 아니다.
- 현재 위치는
  **`production_candidate / watchlist / review_required`**
  로 읽는 것이 맞다.

### why not higher

- 핵심 blocker는 `validation = watch`다.
- 즉 `Quality` family는 current runtime에서도
  benchmark-relative consistency를 더 깨끗하게 만들어야
  다음 단계로 올라갈 수 있다.

## 3. Quality + Value Strict Annual

### best current candidate

- name: `qv_default_candidate_eq`
- quality factors:
  - `roe`
  - `roa`
  - `net_margin`
  - `asset_turnover`
  - `current_ratio`
- value factors:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `ocf_yield`
  - `operating_income_yield`
- `Top N = 10`
- `Rebalance Interval = 1`
- `Benchmark Contract = Candidate Universe Equal-Weight`
- `Trend Filter = off`
- `Market Regime = off`

### 결과

- `Promotion = production_candidate`
- `Shortlist = watchlist`
- `Deployment = review_required`
- `Validation = watch`
- `Validation Policy = normal`
- `Benchmark Policy = normal`
- `Liquidity Policy = normal`
- `Guardrail Policy = normal`
- `Rolling Review = normal`
- `Out-of-Sample Review = normal`
- `CAGR = 28.51%`
- `MDD = -28.35%`

### 해석

- 이번 refresh에서 가장 흥미로운 변화는
  방어형 low-drawdown 케이스보다
  **default blended candidate + candidate equal-weight benchmark**
  가 더 강한 non-hold current candidate로 올라왔다는 점이다.
- 다만 이 family도 아직은
  `paper_probation` 이상으로는 못 갔다.

### defensive reference

- `qv_defensive_lqd_30`
  - `Promotion = production_candidate`
  - `Shortlist = watchlist`
  - `Deployment = review_required`
  - `CAGR = 5.89%`
  - `MDD = -19.76%`

즉 `Quality + Value`는
방어형 해석도 여전히 유효하지만,
current runtime에서 가장 높은 승격 근접도는
default blend 쪽이 더 높았다.

## 4. 운영 결론

현재 current runtime practical refresh 기준으로 보면:

1. `Value`
   - **가장 강한 family**
   - `real_money_candidate / paper_probation / review_required`
   - 현재 바로 다시 볼 1순위
2. `Quality + Value`
   - **가장 강한 non-hold blended family**
   - `production_candidate / watchlist / review_required`
   - 아직 `paper_probation` 전 단계
3. `Quality`
   - bounded search 안에서 non-hold는 만들 수 있었지만
   - 여전히 `production_candidate / watchlist` 수준

## 5. 이번 refresh의 실무적 의미

- Phase 14 이후에도
  `Value`는 여전히 strict annual family의 strongest practical candidate다.
- `Quality`와 `Quality + Value`는
  이제 둘 다 bounded search 안에서 `hold`를 벗어날 수는 있지만,
  아직 `paper_probation` 이상으로는 잘 안 올라간다.
- 즉 next phase calibration/experiment가 필요한 핵심 가족은
  여전히 `Quality`와 `Quality + Value` 쪽이다.

## 최종 요약

- **exact candidate**:
  - `Value > Strict Annual / default value factors / SPY / trend off / regime off`
- **strong blended near-miss**:
  - `Quality + Value > Strict Annual / default blend / candidate equal-weight benchmark`
- **best current quality candidate**:
  - `Quality > Strict Annual / capital_discipline / LQD benchmark`

