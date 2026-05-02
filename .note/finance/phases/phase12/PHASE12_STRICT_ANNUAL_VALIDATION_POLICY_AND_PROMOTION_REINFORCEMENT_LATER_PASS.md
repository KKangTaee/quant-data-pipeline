# Phase 12 - Strict Annual Validation Policy And Promotion Reinforcement Later Pass

## What changed

- strict annual family 3종에 `Validation Policy` later pass를 추가했다.
- 새 승격 기준:
  - `Max Underperformance Share (%)`
  - `Min Worst Rolling Excess (%)`
- 이 기준은 기존에 계산만 하던 benchmark-relative validation 지표를
  실제 `promotion_decision`에 반영하는 역할을 한다.

## Easy explanation

- `Underperformance Share`
  - rolling window 기준으로 benchmark보다 약했던 구간의 비율이다.
  - 이 비율이 너무 높으면, 전략이 운 좋게 특정 구간에서만 좋아 보였을 가능성을 더 조심해서 본다.
- `Worst Rolling Excess`
  - benchmark 대비 trailing excess return이 가장 나빴던 구간이다.
  - 이 값이 너무 낮으면, 실전 운용 중 꽤 불편한 underperformance 구간이 나올 수 있다는 뜻이다.
- 이번 later pass는
  - "validation 결과를 보여주기만 하는 단계"에서
  - "승격 판단에도 실제로 쓰는 단계"로 한 걸음 더 나아간 것이다.

## Runtime contract

- runtime meta에 아래 값이 추가된다.
  - `promotion_max_underperformance_share`
  - `promotion_min_worst_rolling_excess_return`
  - `validation_policy_status`
  - `validation_policy_watch_signals`
  - `validation_policy_share_pass`
  - `validation_policy_worst_excess_pass`
- `validation_policy_status`
  - `normal`
  - `watch`
  - `caution`
  - `unavailable`
  로 해석한다.

## UI surface

- single strict annual `Real-Money Contract`
  - 새 threshold 입력 가능
- single `Real-Money`
  - `Validation Policy` block 추가
- compare `Strategy Highlights`
  - `Validation Policy` 컬럼 추가
- history / `Load Into Form`
  - 새 threshold 값 복원
- `Execution Context`
  - 새 threshold와 policy status 기록

## Promotion semantics

- `promotion_decision = real_money_candidate`
  - benchmark policy / liquidity policy / validation policy가 모두 `normal`이어야 한다.
- `promotion_decision = hold`
  - `validation_policy_status = caution / unavailable`이면 더 보수적으로 본다.
- `promotion_decision = production_candidate`
  - validation policy가 `watch`일 때는 아직 추가 robustness 검토가 더 필요하다고 본다.

## Current boundary

- 이번 변경은 promotion rule 강화다.
- 실제 전략 selection rule을 더 바꾼 것은 아니다.
- 즉:
  - strategy output은 그대로 두고
  - 실전 승격 판정만 더 엄격하게 만든 later pass다.

