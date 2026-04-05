# Phase 12 - Strict Annual Portfolio Guardrail Policy And Promotion Reinforcement Later Pass

## What changed

- strict annual family 3종에 `Portfolio Guardrail Policy` later pass를 추가했다.
- 새 승격 기준:
  - `Max Strategy Drawdown (%)`
  - `Max Drawdown Gap vs Benchmark (%)`
- 이 기준은 기존에 계산만 하던 drawdown 지표를
  실제 `promotion_decision`에 반영하는 역할을 한다.

## Easy explanation

- `Strategy Max Drawdown`
  - 전략이 백테스트 구간에서 가장 깊게 빠졌던 낙폭이다.
  - 이 값이 너무 깊으면, 수익률이 좋아 보여도 실전 운용에선 버티기 어렵다.
- `Drawdown Gap vs Benchmark`
  - 전략의 최대 낙폭이 benchmark보다 얼마나 더 나빴는지를 보는 값이다.
  - benchmark보다 낙폭이 지나치게 크면,
    "수익은 비슷한데 스트레스만 더 큰 전략"일 수 있다.
- 이번 later pass는
  - "drawdown을 보여주기만 하는 단계"에서
  - "승격 판단에도 실제로 쓰는 단계"로 한 걸음 더 나아간 것이다.

## Runtime contract

- runtime meta에 아래 값이 추가된다.
  - `promotion_max_strategy_drawdown`
  - `promotion_max_drawdown_gap_vs_benchmark`
  - `guardrail_policy_status`
  - `guardrail_policy_watch_signals`
  - `guardrail_policy_strategy_drawdown_pass`
  - `guardrail_policy_drawdown_gap_pass`
  - `drawdown_gap_vs_benchmark`
- `guardrail_policy_status`
  - `normal`
  - `watch`
  - `caution`
  - `unavailable`
  로 해석한다.

## UI surface

- single strict annual `Real-Money Contract`
  - 새 threshold 입력 가능
- single `Real-Money`
  - `Portfolio Guardrail Policy` block 추가
- compare `Strategy Highlights`
  - `Guardrail Policy`
  - `Strategy Max DD`
  - `Drawdown Gap`
  컬럼 추가
- history / `Load Into Form`
  - 새 threshold 값 복원
- `Execution Context`
  - 새 threshold와 policy status 기록

## Promotion semantics

- `promotion_decision = real_money_candidate`
  - benchmark policy / liquidity policy / validation policy / guardrail policy가 모두 `normal`이어야 한다.
- `promotion_decision = hold`
  - `guardrail_policy_status = caution / unavailable`이면
    낙폭 방어 계약이 아직 충분하지 않다고 본다.
- `promotion_decision = production_candidate`
  - guardrail policy가 `watch`이면
    실전 승격 전 drawdown robustness를 더 검토해야 한다고 본다.

## Current boundary

- 이번 변경은 promotion rule 강화다.
- 실제 전략 selection rule을 drawdown 기준으로 바꾼 것은 아니다.
- 즉:
  - strategy output은 그대로 두고
  - 실전 승격 판정만 더 엄격하게 만든 later pass다.
- actual strategy-side drawdown guardrail은 아직 later backlog다.

