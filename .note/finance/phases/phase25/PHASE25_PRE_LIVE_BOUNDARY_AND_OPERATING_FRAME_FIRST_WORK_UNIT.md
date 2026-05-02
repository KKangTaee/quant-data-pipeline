# Phase 25 Pre-Live Boundary And Operating Frame First Work Unit

## 이 문서는 무엇인가

이 문서는 Phase 25의 첫 번째 작업 단위다.

Phase 25에서 가장 먼저 해야 할 일은 기능을 새로 붙이는 것이 아니라,
`Real-Money 검증 신호`와 `Pre-Live 운영 점검`의 역할을 분리하고
Pre-Live에서 쓸 운영 상태와 다음 행동 기록을 정리하는 것이다.

## 쉽게 말하면

Real-Money는 백테스트 결과에 붙는 "주의사항 표"다.
Pre-Live는 그 표를 보고 "그럼 다음에 무엇을 할까"를 기록하는 운영 노트다.

예를 들어 Real-Money가 "거래비용은 괜찮지만 최근 drawdown이 크다"라고 알려주면,
Pre-Live에서는 이 후보를 바로 승인하지 않고
`paper tracking` 또는 `hold`로 남길 수 있어야 한다.

중요한 차이는 `상태값` 자체가 아니다.
`watchlist`, `paper_tracking`, `hold` 같은 단어만 보면
Real-Money의 promotion / shortlist 단계와 비슷해 보일 수 있다.

Pre-Live의 핵심은 상태값에 붙는 **다음 행동 기록**이다.
즉 "상태가 무엇인가"보다
"그래서 언제, 무엇을, 어떤 조건으로 다시 확인할 것인가"를 남기는 것이 더 중요하다.

## 왜 먼저 하는가

Phase 25는 이름만 보면 실전 배포처럼 보일 수 있다.
하지만 현재 목표는 live trading이 아니라 pre-live readiness다.

이 경계를 먼저 고정하지 않으면 다음 문제가 생긴다.

- Real-Money 탭과 Phase 25 기능이 중복처럼 보인다.
- 사용자가 paper tracking과 투자 승인을 혼동할 수 있다.
- 후보를 왜 보류했는지 나중에 추적하기 어렵다.
- Phase가 다시 투자 분석 중심으로 흘러갈 수 있다.

## Real-Money와 Pre-Live의 실제 차이

| 구분 | Real-Money | Pre-Live |
|---|---|---|
| 핵심 역할 | 백테스트 결과의 위험 신호를 진단한다. | 진단을 보고 사람이 다음 운영 행동을 기록한다. |
| 대표 값 | promotion, shortlist, deployment, blocker | pre_live_status, operator_reason, next_action, review_date, tracking_plan |
| 질문 | "이 결과에 어떤 위험 신호가 있나?" | "그래서 이 후보를 어떻게 관리할 것인가?" |
| 저장 의미 | 결과 해석 / 검증 신호 | 운영 메모 / 추적 계획 / 재검토 조건 |
| 투자 승인 여부 | 아님 | 아님 |

따라서 Pre-Live record는 단순히
`paper_tracking` 같은 상태 하나만 저장하면 부족하다.
반드시 아래의 action package가 같이 있어야 한다.

## 다음 행동 기록 정의

Pre-Live에서 말하는 "다음 행동"은 아래 정보를 묶은 것이다.

| 항목 | 뜻 | 예시 |
|---|---|---|
| `operator_reason` | 왜 이 상태로 뒀는지 | "최근 MDD는 크지만 Real-Money blocker가 없어 1개월 paper tracking" |
| `next_action` | 다음에 실제로 할 일 | "월 1회 성과, MDD, benchmark gap을 확인" |
| `review_date` | 다시 볼 날짜 | "2026-05-21" |
| `tracking_plan.cadence` | 얼마나 자주 볼지 | monthly, next_strategy_review, scheduled_review |
| `tracking_plan.stop_condition` | 언제 중단할지 | "drawdown이 더 악화되거나 blocker가 생기면 중단" |
| `tracking_plan.success_condition` | 무엇이 확인되면 다음 단계로 갈지 | "관찰 기간 동안 blocker 없이 성격이 유지되면 재검토" |
| `docs` | 판단 근거 문서 | source report, strategy hub, backtest log |

쉽게 말하면:

- Real-Money가 "주의" 또는 "검토 가능"이라고 말한다.
- Pre-Live는 "그러면 1개월 동안 무엇을 볼지", "어떤 경우 중단할지",
  "언제 다시 판단할지"를 남긴다.

이 action package가 없으면 Pre-Live는 Real-Money 상태값과 거의 같은 기능처럼 보인다.
따라서 Phase 25에서는 `pre_live_status`보다
`operator_reason`, `next_action`, `review_date`, `tracking_plan`을 함께 남기는 것을 핵심으로 본다.

## 운영 상태 정의

### Watchlist

- 의미:
  - 다시 볼 가치가 있지만, 아직 paper tracking까지 올리지는 않은 상태다.
- 쓰는 상황:
  - 성과는 흥미롭지만 데이터 품질, 기간, 최근성, 설정 안정성이 더 필요할 때.
- 다음 행동:
  - 다음 후보 비교 또는 데이터 업데이트 때 다시 확인한다.
  - 어떤 조건이 맞으면 paper tracking으로 올릴지 `next_action`에 남긴다.
  - 다시 볼 날짜가 정해져 있으면 `review_date`에 남긴다.

### Paper Tracking

- 의미:
  - 실제 돈을 넣지 않고 정해진 기간 동안 관찰하는 상태다.
- 쓰는 상황:
  - Real-Money 검증 신호가 크게 나쁘지 않고,
    운영자가 성과와 위험이 계속 유지되는지 보고 싶을 때.
- 다음 행동:
  - 관찰 주기, 중단 조건, 성공 조건을 `tracking_plan`에 남긴다.
  - 관찰 기간이 끝나면 hold, reject, re-review 또는 다음 review 단계로 판단한다.
  - 이 상태도 실제 돈을 넣는다는 뜻은 아니다.

### Hold

- 의미:
  - 지금은 진행하지 않고 보류하는 상태다.
- 쓰는 상황:
  - 데이터 품질, 결측 가격 행, 과도한 drawdown, 과도한 거래비용,
    benchmark 대비 약점, 구조적 설명 부족이 있을 때.
- 다음 행동:
  - 어떤 blocker를 풀어야 하는지 `operator_reason`과 `next_action`에 남긴다.
  - blocker가 해결되면 다시 review한다.

### Reject

- 의미:
  - 현재 기준에서는 더 추적하지 않는 상태다.
- 쓰는 상황:
  - 구조적으로 목적에 맞지 않거나,
    반복 검증에서 위험이 너무 크거나,
    데이터 보강 후에도 의미 있는 후보가 아니라고 판단될 때.
- 다음 행동:
  - active workflow에서는 추적을 종료한다.
  - 같은 후보를 다시 보려면 새 근거가 생겼을 때 새 review로 다룬다.

### Re-Review

- 의미:
  - 특정 날짜나 조건이 지나면 다시 보기로 예약한 상태다.
- 쓰는 상황:
  - 지금 판단하기에는 데이터가 부족하거나,
    최근 이벤트가 지나간 뒤 다시 보는 것이 맞을 때.
- 다음 행동:
  - `review_date`와 확인 조건을 남긴다.
  - 재검토 시점에 watchlist / paper tracking / hold / reject 중 하나로 다시 정리한다.

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
  - 다음에 무엇을 할지. 단순 문장이 아니라 확인할 지표, 실행 주기, 판단 조건이 들어가야 한다.
- `review_date`
  - 언제 다시 볼지.
- `tracking_plan`
  - paper tracking 또는 re-review에서 관찰 주기, 중단 조건, 성공 조건을 남긴다.

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

Phase 25 두 번째 작업에서 이 방향을 확정했다.
Pre-Live 운영 기록은 별도 `.note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`에 두고,
기존 `CURRENT_CANDIDATE_REGISTRY.jsonl`과는 `source_candidate_registry_id`로 연결한다.

## 한 줄 정리

Phase 25의 첫 작업은 후보를 고르는 것이 아니라,
후보를 실전 전에 어떻게 관찰하고 보류하고 다시 볼지 정하는 운영 언어를 고정하는 것이다.
