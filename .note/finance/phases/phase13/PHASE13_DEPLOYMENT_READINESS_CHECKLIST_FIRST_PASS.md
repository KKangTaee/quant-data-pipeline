# Phase 13 Deployment-Readiness Checklist First Pass

## 목적

- Phase 13에서 지금까지 만든
  - shortlist
  - probation / monitoring
  - rolling / out-of-sample review
  - benchmark / liquidity / validation / guardrail policy
  를 한 장의 checklist로 묶어서,
  실제 운용 직전 현재 상태를 더 빠르게 읽을 수 있게 만든다.

쉬운 뜻:

- 이제는 "이 전략이 좋아 보인다"가 아니라,
  **실전 투입 전에 무엇이 통과됐고 무엇이 아직 걸리는지**를 바로 볼 수 있어야 한다.

## 이번에 추가된 meta

- `deployment_readiness_status`
- `deployment_readiness_next_step`
- `deployment_readiness_rationale`
- `deployment_checklist_rows`
- `deployment_check_pass_count`
- `deployment_check_watch_count`
- `deployment_check_fail_count`
- `deployment_check_unavailable_count`

## checklist에 들어가는 항목

현재 first pass는 아래 상태를 한 장으로 묶는다.

- `Universe Contract`
- `Benchmark Availability`
- `Benchmark Contract`
- `Benchmark Policy`
- `Liquidity Policy`
- `Validation Policy`
- `Guardrail Policy`
- `ETF Operability`
- `Price Freshness`
- `Shortlist`
- `Probation`
- `Monitoring`
- `Rolling Review`
- `Out-Of-Sample Review`

## checklist row 상태 의미

- `pass`
  - 현재 기준에서 큰 blocker가 없다
- `watch`
  - 바로 실패는 아니지만, 더 보수적으로 봐야 한다
- `fail`
  - 지금 상태로는 비중 확대나 live trial 해석이 어렵다
- `unavailable`
  - 필요한 review 정보가 부족하다

## deployment status 의미

- `blocked`
  - failed check가 크거나 아직 probation 전 단계라, 먼저 blocker를 해결해야 한다
- `review_required`
  - 바로 배치는 어렵고, failed check를 수동 review해야 한다
- `watchlist_only`
  - watchlist 단계로만 유지하는 것이 맞다
- `paper_only`
  - 아직은 paper probation으로만 두는 것이 맞다
- `small_capital_ready`
  - 현재 checklist 기준에서는 소액 trial까지 검토 가능하다
- `small_capital_ready_with_review`
  - 소액 trial은 가능하지만 watch / unavailable 항목을 같이 보면서 더 보수적으로 운용해야 한다

## 현재 해석 규칙

- `hold`나 `not_ready`이면 `blocked`
- failed check가 있으면 `review_required` 또는 `blocked`
- `paper_tracking`이면 `paper_only`
- `small_capital_live_trial`이면서 fail이 없으면
  - watch / unavailable 없을 때 `small_capital_ready`
  - 있으면 `small_capital_ready_with_review`

## UI surface

- single strategy `Real-Money`
- `Execution Context`
- compare `Strategy Highlights`
- compare meta table

## 현재 경계

- 이번 pass는 **read-only deployment checklist layer**다.
- checklist가 바로 actual block rule을 더 추가하는 것은 아니다.
- live capital sizing, broker 실행, 월별 review note 저장은 아직 later pass다.

## 검증

- `py_compile`
- page/runtime import smoke
- helper-level checklist mapping smoke
- DB-backed smoke
  - strict annual
  - ETF strategy

## 해석

- Phase 13은 이제 단순한 candidate shortlist가 아니라,
  **실전 투입 직전 점검표**까지 product surface로 읽을 수 있는 상태가 되었다.
- 이 checklist는 아직 "자동 매매 허용기"가 아니라,
  전략을 더 보수적으로 운영하기 위한 deployment-readiness summary로 읽는 것이 맞다.
