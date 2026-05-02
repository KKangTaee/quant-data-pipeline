# Phase 13 Probation And Monitoring Workflow First Pass

## 목적

- Phase 13 shortlist 결과를 실제 운영 언어로 더 좁혀서,
  각 전략이 지금
  - 아직 대기 상태인지
  - paper tracking으로 먼저 봐야 하는지
  - small-capital trial까지 볼 수 있는지
  를 한 번 더 읽을 수 있게 만든다.
- 이번 pass는 전략 규칙을 더 공격적으로 바꾸는 작업이 아니라,
  **deployment-readiness를 운영 workflow로 읽는 layer**를 추가하는 작업이다.

쉬운 뜻:

- shortlist는 "이 전략이 후보인가 아닌가"를 말한다.
- probation / monitoring은 "그 후보를 지금 어떻게 관찰해야 하는가"를 말한다.

## 이번에 추가된 contract

runtime meta에 아래 항목이 추가되었다.

- `probation_status`
- `probation_stage`
- `probation_review_frequency`
- `probation_next_step`
- `probation_rationale`
- `monitoring_status`
- `monitoring_focus`
- `monitoring_breach_signals`
- `monitoring_review_frequency`
- `monitoring_next_step`

## probation 상태 의미

- `not_ready`
  - shortlist가 `hold`인 경우
  - 계약 gap을 먼저 해결해야 한다
- `watchlist_review`
  - shortlist가 `watchlist`인 경우
  - 아직 probation에 넣기 전에 robustness / policy review가 더 필요하다
- `paper_tracking`
  - shortlist가 `paper_probation`인 경우
  - 실거래 전 paper tracking과 월별 review를 먼저 진행한다
- `small_capital_live_trial`
  - shortlist가 `small_capital_trial`인 경우
  - 소액 실전 trial과 월별 breach review까지 같이 본다

## monitoring 상태 의미

- `blocked`
  - 아직 monitoring을 운영 단계로 읽기 전에 blocker를 먼저 해결해야 한다
- `routine_review`
  - 현재 계약 기준에서는 월별 routine review로 이어갈 수 있다
- `heightened_review`
  - watch / warning 성격의 신호가 있어 routine보다 더 보수적으로 봐야 한다
- `breach_watch`
  - guardrail trigger 또는 caution / unavailable 성격의 정책 breach가 있어
    비중 확대보다 먼저 review가 필요하다

## breach 신호를 어떻게 읽는가

first pass는 이미 runtime에 있는 정책 상태를 재사용한다.

- `validation_status`
- `benchmark_policy_status`
- `etf_operability_status`
- `liquidity_policy_status`
- `validation_policy_status`
- `guardrail_policy_status`
- `price_freshness.status`
- `underperformance_guardrail_trigger_count`
- `drawdown_guardrail_trigger_count`

즉 이번 구현은 새 데이터를 더 요구하지 않고,
기존 정책 상태를 probation / monitoring 언어로 다시 읽는 구조다.

## UI surface

다음 위치에 probation / monitoring 정보가 추가되었다.

- single strategy `Real-Money`
- `Execution Context`
- compare `Strategy Highlights`
- compare meta table

## 현재 경계

- 이번 pass는 **read-only deployment workflow layer**다.
- actual ETF operability block rule이나 PIT operability history까지 추가한 것은 아니다.
- monthly review 노트를 별도 저장하는 product workflow도 아직 later pass다.

## 검증

- `py_compile`
- page/runtime import smoke
- helper-level branch smoke
  - `hold -> not_ready / blocked`
  - `watchlist -> watchlist_review / routine or heightened review`
  - `paper_probation -> paper_tracking`
  - `small_capital_trial -> small_capital_live_trial`
- DB-backed smoke
  - strict annual
  - ETF strategy

## 해석

- 이제 Phase 13은 단순히 shortlist를 보여주는 단계가 아니라,
  **현재 어떤 probation 단계로 운영해야 하는지**까지 읽을 수 있는 상태가 되었다.
- 다만 monthly review 기록 저장, rolling/out-of-sample review, deploy checklist는 계속 다음 단계다.
