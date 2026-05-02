# Phase 14 Deployment Workflow Bridge First Pass

## 목적

- Phase 13에서 생긴 shortlist / probation / monitoring / deployment-readiness surface가
  실제 operator workflow로 어디까지 연결되어 있는지 정리한다.
- 동시에 다음 phase에서 필요한
  **paper probation handoff, monthly review note, small-capital trial action**
  이 어디서부터 비어 있는지도 분명히 남긴다.

## 이번 문서의 한 줄 결론

- 현재 product는
  **전략을 운영 후보 언어로 읽는 surface**까지는 이미 있다.
- 하지만 실제 operator action을 저장하고 추적하는 workflow는 아직 없기 때문에,
  다음 phase는 interpretation layer 위에
  **operator log / action bridge**를 얹는 단계로 읽는 것이 맞다.

## 1. 현재 이미 구현된 bridge

현재 runtime / UI에는 아래 operator-facing surface가 이미 있다.

### 1-1. Shortlist

- `shortlist_status`
- `shortlist_next_step`
- `shortlist_rationale`

해석:

- 이 전략을 watchlist로 둘지,
  paper probation으로 올릴지,
  small-capital trial까지 볼 수 있는지
  product에서 바로 읽을 수 있다.

### 1-2. Probation / Monitoring

- `probation_status`
- `probation_stage`
- `probation_review_frequency`
- `probation_next_step`
- `monitoring_status`
- `monitoring_review_frequency`
- `monitoring_focus`
- `monitoring_breach_signals`
- `monitoring_next_step`

해석:

- 전략이 지금 operator 입장에서
  `not_ready`, `watchlist_review`, `paper_tracking`, `small_capital_live_trial`
  중 어디에 있는지를 product가 설명한다.

### 1-3. Deployment Readiness

- `deployment_readiness_status`
- `deployment_readiness_next_step`
- `deployment_checklist_rows`

해석:

- 전략이 왜 `blocked`, `paper_only`, `review_required`,
  `small_capital_ready`, `small_capital_ready_with_review`
  로 읽히는지 한 장의 checklist로 볼 수 있다.

### 1-4. History gate snapshot

- history `schema v2`는
  `gate_snapshot`을 같이 저장한다.

해석:

- 과거 실행 시점의
  `promotion / shortlist / probation / monitoring / deployment / policy status`
  를 나중에 다시 audit할 수 있다.

## 2. 현재 product에서 아직 없는 것

### 2-1. Paper probation handoff object

지금은 `paper_probation`이나 `paper_tracking`이라는 해석은 있다.
하지만 실제로

- paper portfolio id
- 시작일
- review owner
- review cadence
- comment / note

를 저장하는 별도 workflow object는 없다.

### 2-2. Monthly review note / operator log persistence

현재는

- `probation_next_step`
- `monitoring_next_step`

를 읽을 수는 있지만,
월별 review note를 저장하는 persistent object는 없다.

즉 지금은
**operator action recommendation**은 있고,
**operator action record**는 없다.

### 2-3. Small-capital trial execution handoff

`small_capital_trial`과
`small_capital_live_trial` 해석은 있다.
하지만 실제로

- trial capital
- entry date
- rebalance action
- stop / pause note
- breach response log

를 저장하는 경로는 없다.

### 2-4. Backtest result와 operator action 연결

현재는 backtest result와 gate snapshot이 남는다.
하지만 다음이 아직 없다.

- “이 run을 기준으로 paper probation 시작”
- “이 run을 기준으로 small capital trial 시작”
- “이 run은 reject / hold 유지”

같은 operator action 링크

## 3. 지금까지는 어디까지를 완료로 볼 수 있나

Phase 14 기준으로는 아래까지를 완료로 보는 것이 맞다.

- gate를 operator 언어로 읽는 contract
- 그 contract를 history에서 다시 읽는 snapshot
- 다음 단계 추천(next step) surface

즉 현재는
**operator interpretation bridge**까지는 완료되었다.

반면 아래는 다음 phase 구현 범위다.

- operator note persistence
- actual handoff object
- paper/live trial log
- backtest result -> operator action linkage

## 4. 다음 phase의 구현 우선순위

### 우선순위 1. paper probation handoff object

최소 필드:

- strategy/run identifier
- handoff date
- probation stage
- review frequency
- owner
- note

### 우선순위 2. monthly review note

최소 필드:

- review month
- current gate summary
- breaches observed
- action
- next review date

### 우선순위 3. small-capital trial action record

최소 필드:

- capital amount
- start / pause / stop status
- rationale
- latest gate summary

## 5. closeout 판단

Phase 14는 deployment workflow를
“완전히 구현하는 phase”가 아니라,
**현재 surface가 어디까지 operator workflow를 설명하는지와
어디서부터 persistence가 비는지**
를 분명히 만드는 phase로 읽는 것이 맞다.

따라서 이번 문서는
다음 phase의 operator-log / action-object workstream을 여는
실질적인 bridge 문서로 충분하다.

