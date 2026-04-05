# Phase 12 - Strict Annual Liquidity Policy And Promotion Reinforcement Later Pass

## 목적

strict annual family의 유동성 보강을 한 단계 더 진행해서,
단순히 `Min Avg Dollar Volume 20D ($M)` 필터가 있다는 사실만 보는 것이 아니라
실제로 백테스트 내 리밸런싱이 유동성 제약에 얼마나 자주 걸렸는지를
승격 판단에 반영한다.

대상 전략:
- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

## 쉽게 말하면

이전까지는:
- 유동성 필터를 켰는가
- 몇 개 종목이 유동성 때문에 제외됐는가
정도만 읽을 수 있었다.

이번 보강 이후에는:
- 리밸런싱 행 중 얼마나 많은 비율이
  **유동성 제외 없이 깔끔하게 지나갔는지**
를 `Liquidity Policy`로 읽을 수 있다.

즉,
- 유동성 필터는 켰지만 실제론 자주 막히는 전략인지
- 아니면 대부분의 리밸런싱이 무리 없이 돌아가는 전략인지
를 promotion 판단에 더 직접적으로 반영한다.

## 추가된 계약

### `Min Liquidity Clean Coverage (%)`

- 기본 설명:
  - 리밸런싱 행 중 최소 몇 %가 유동성 제외 없이 지나가야 하는지 정하는 기준
- 왜 필요한가:
  - 실전형 전략이라면 단순히 "필터가 있다"보다
    "실제로도 대부분의 리밸런싱이 유동성 제약 없이 진행되는가"가 더 중요하기 때문
- 예시 / 필요 상황:
  - 기준이 `90%`라면
    리밸런싱 10번 중 9번 이상은 유동성 제외 없이 지나가길 기대하는 뜻

### `liquidity_clean_coverage`

- 기본 설명:
  - 실제 run에서 유동성 제외가 발생하지 않은 리밸런싱 행 비율
- 왜 필요한가:
  - 설정한 policy 기준과 실제 run 결과를 비교하려면 실제 coverage 값이 필요하기 때문
- 예시 / 필요 상황:
  - `1.00`이면 모든 리밸런싱이 유동성 제외 없이 지나감
  - `0.82`면 일부 구간에서 유동성 제약이 꽤 자주 발생한 것

### `liquidity_policy_status`

- 기본 설명:
  - liquidity policy 기준을 현재 run이 얼마나 잘 만족했는지 요약한 상태값
- 값:
  - `normal`
  - `watch`
  - `caution`
  - `unavailable`
- 왜 필요한가:
  - promotion 판단에서 유동성 상태를 한 줄로 읽기 위해
- 예시 / 필요 상황:
  - `normal`: 기준 충족
  - `watch`: 기준보다 조금 약함
  - `caution`: 기준보다 꽤 약함
  - `unavailable`: 유동성 필터 자체가 꺼져 있거나 coverage 계산 근거가 부족함

## 구현 내용

- shared real-money helper에서 아래 값을 계산한다.
  - `liquidity_rebalance_rows`
  - `liquidity_excluded_active_rows`
  - `liquidity_clean_coverage`
- strict annual contract에 아래 입력값을 추가했다.
  - `Min Liquidity Clean Coverage (%)`
- policy helper가 아래를 계산한다.
  - `liquidity_policy_status`
  - `liquidity_policy_watch_signals`
  - `liquidity_policy_clean_coverage_pass`
- `promotion_decision`가 이제 아래도 함께 본다.
  - `liquidity_policy_status`

## 현재 판정 규칙

- `real_money_candidate`
  - benchmark / validation / liquidity policy가 모두 `normal`
  - static universe contract가 아님
  - price freshness warning/error가 없음
- `hold`
  - liquidity policy가 `caution` 또는 `unavailable`
  - 또는 benchmark/validation/price freshness 쪽에서 hold 조건 충족
- `production_candidate`
  - 위 둘 사이는 중간 상태
  - 예: liquidity policy가 `watch`

## UI / History 반영 범위

- single `Real-Money`
  - `Liquidity Policy`
  - `Policy Status`
  - `Min Clean Coverage`
  - `Actual Clean Coverage`
  - `Liquidity Policy Signals`
- single `Execution Context`
  - `Min Liquidity Clean Coverage`
  - `Liquidity Clean Coverage`
  - `Liquidity Policy Status`
- compare `Strategy Highlights`
  - `Liquidity Policy`
- history / `Load Into Form`
  - `promotion_min_liquidity_clean_coverage` 복원

## 현재 한계

- 이 later pass는 유동성 상태를 더 잘 읽어주는 **promotion policy 강화**다.
- 아직 구현되지 않은 것:
  - spread-aware liquidity
  - AUM 정책
  - volume + spread를 같이 보는 richer investability contract

## 의미

이제 strict annual family는
유동성 필터를 단순히 "켜짐/꺼짐"으로만 보지 않고,
실제로 run이 얼마나 자주 유동성 제약에 걸렸는지를 promotion 판단에 반영한다.

즉 이번 보강은
**유동성 필터의 존재**에서 한 단계 더 나아가
**유동성 제약의 실제 체감 빈도**를 실전 승격 판단에 연결한 단계로 보면 된다.
