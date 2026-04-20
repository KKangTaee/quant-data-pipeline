# Phase 25 Pre-Live Boundary And Operating Frame First Work Unit

## 이 문서는 무엇인가

이 문서는 Phase 25의 첫 번째 작업 단위다.

Phase 25에서 가장 먼저 해야 할 일은 기능을 새로 붙이는 것이 아니라,
`Real-Money 검증 신호`와 `Pre-Live 운영 점검`의 역할을 분리하고
Pre-Live에서 쓸 운영 상태를 정리하는 것이다.

## 쉽게 말하면

Real-Money는 백테스트 결과에 붙는 "주의사항 표"다.
Pre-Live는 그 표를 보고 "그럼 다음에 무엇을 할까"를 기록하는 운영 노트다.

예를 들어 Real-Money가 "거래비용은 괜찮지만 최근 drawdown이 크다"라고 알려주면,
Pre-Live에서는 이 후보를 바로 승인하지 않고
`paper tracking` 또는 `hold`로 남길 수 있어야 한다.

## 왜 먼저 하는가

Phase 25는 이름만 보면 실전 배포처럼 보일 수 있다.
하지만 현재 목표는 live trading이 아니라 pre-live readiness다.

이 경계를 먼저 고정하지 않으면 다음 문제가 생긴다.

- Real-Money 탭과 Phase 25 기능이 중복처럼 보인다.
- 사용자가 paper tracking과 투자 승인을 혼동할 수 있다.
- 후보를 왜 보류했는지 나중에 추적하기 어렵다.
- Phase가 다시 투자 분석 중심으로 흘러갈 수 있다.

## 운영 상태 정의

### Watchlist

- 의미:
  - 다시 볼 가치가 있지만, 아직 paper tracking까지 올리지는 않은 상태다.
- 쓰는 상황:
  - 성과는 흥미롭지만 데이터 품질, 기간, 최근성, 설정 안정성이 더 필요할 때.
- 다음 행동:
  - 조건이 맞으면 paper tracking으로 올리거나, 일정 기간 후 re-review한다.

### Paper Tracking

- 의미:
  - 실제 돈을 넣지 않고 정해진 기간 동안 관찰하는 상태다.
- 쓰는 상황:
  - Real-Money 검증 신호가 크게 나쁘지 않고,
    운영자가 성과와 위험이 계속 유지되는지 보고 싶을 때.
- 다음 행동:
  - 관찰 기간이 끝나면 promotion, hold, reject, re-review 중 하나로 판단한다.

### Hold

- 의미:
  - 지금은 진행하지 않고 보류하는 상태다.
- 쓰는 상황:
  - 데이터 품질, 결측 가격 행, 과도한 drawdown, 과도한 거래비용,
    benchmark 대비 약점, 구조적 설명 부족이 있을 때.
- 다음 행동:
  - blocker가 해결되면 다시 review한다.

### Reject

- 의미:
  - 현재 기준에서는 더 추적하지 않는 상태다.
- 쓰는 상황:
  - 구조적으로 목적에 맞지 않거나,
    반복 검증에서 위험이 너무 크거나,
    데이터 보강 후에도 의미 있는 후보가 아니라고 판단될 때.
- 다음 행동:
  - 일반적으로 active workflow에서는 제거하고, 필요하면 archive에만 남긴다.

### Re-Review

- 의미:
  - 특정 날짜나 조건이 지나면 다시 보기로 예약한 상태다.
- 쓰는 상황:
  - 지금 판단하기에는 데이터가 부족하거나,
    최근 이벤트가 지나간 뒤 다시 보는 것이 맞을 때.
- 다음 행동:
  - review date와 확인 조건을 남긴다.

## 후보 기록에 필요한 최소 정보

Pre-Live 후보 기록에는 최소한 다음 정보가 필요하다.

- `source`
  - 이 후보가 single strategy, compare, saved portfolio, report 중 어디서 왔는지.
- `strategy_or_bundle`
  - 단일 전략인지, weighted portfolio인지, saved portfolio인지.
- `settings_snapshot`
  - 재실행에 필요한 핵심 설정.
- `result_snapshot`
  - CAGR, Sharpe, MDD, End Balance 같은 요약 수치.
- `real_money_signal`
  - Real-Money 검증 신호의 주요 상태와 blocker.
- `pre_live_status`
  - watchlist, paper_tracking, hold, reject, re_review 중 하나.
- `operator_reason`
  - 왜 이 상태로 두었는지 사람이 읽을 수 있는 설명.
- `next_action`
  - 다음에 무엇을 할지.
- `review_date`
  - 언제 다시 볼지.

## 이번 작업에서 고정한 원칙

- Real-Money는 검증 신호다.
- Pre-Live는 운영 절차다.
- Pre-Live 상태는 투자 승인이 아니다.
- 좋은 수치보다 중요한 것은 `다음 행동이 기록되는가`다.
- 데이터 결측이나 coverage 문제는 숨기지 않고 blocker로 남긴다.

## 다음 작업

다음 작업은 이 운영 상태를 실제 기록 포맷으로 옮기는 것이다.

우선 검토할 선택지는 두 가지다.

1. 문서/report 기반으로 먼저 기록한다.
2. `.jsonl` 또는 lightweight registry로 저장하고 UI에서 읽을 수 있게 한다.

현재는 두 번째 방향이 장기적으로 더 좋지만,
구현 전에 기존 `CURRENT_CANDIDATE_REGISTRY.jsonl`과 역할이 겹치지 않게 설계를 확인해야 한다.

## 한 줄 정리

Phase 25의 첫 작업은 후보를 고르는 것이 아니라,
후보를 실전 전에 어떻게 관찰하고 보류하고 다시 볼지 정하는 운영 언어를 고정하는 것이다.
