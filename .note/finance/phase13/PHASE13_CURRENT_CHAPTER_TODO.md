# Phase 13 Current Chapter TODO

## 상태 기준

- `pending`
- `in_progress`
- `completed`

## 1. Chapter Setup

- `completed` Phase 13 방향 고정
  - deployment-readiness / probation / monitoring phase로 연다
- `completed` Phase 12 handoff 재해석
  - Phase 12 remaining ETF second-pass backlog는
    Phase 13의 주제로 이관한다
- `completed` current active phase 전환
  - `Phase 13`을 현재 active phase로 둔다

## 2. Candidate Shortlist Contract

- `completed` shortlist status language first pass 고정
  - `watchlist`
  - `paper_probation`
  - `small_capital_trial`
  - `hold`
- `completed` candidate shortlist metadata surface 초안 작성
  - strategy family
  - benchmark/guardrail/policy status
  - current recommendation
- `completed` shortlist document first pass 작성
  - 실전형 후보를 운영용 shortlist로 다시 묶는다

## 3. ETF Second-Pass Hardening

- `completed` ETF underperformance / guardrail later pass 정리
  - `GTAA`, `Risk Parity Trend`, `Dual Momentum`에
    underperformance / drawdown guardrail actual rule을 연결했다
  - single / compare / history / saved-portfolio compare context까지
    같은 contract로 round-trip된다
- `pending` ETF current-operability rule 검토
  - 현재 AUM / spread warning을 actual block rule로 쓸지 판단
- `pending` ETF point-in-time operability later-pass 필요성 검토
  - current snapshot overlay를 어디까지로 볼지 다시 정리

## 4. Probation And Monitoring Workflow

- `completed` probation workflow contract 초안 작성
  - paper tracking
  - small-capital trial
  - monthly review
- `completed` monitoring note / warning contract 초안 작성
  - drawdown
  - underperformance
  - policy breach
- `completed` later UI / history surface 필요 범위 정리
  - single `Real-Money`, `Execution Context`, compare `Strategy Highlights`, compare meta table까지 first pass로 연결

## 5. Out-Of-Sample / Rolling Validation

- `pending` rolling validation contract 초안 작성
  - recent regime review
  - rolling window 비교
- `pending` out-of-sample review checklist 초안 작성
  - fixed long-period 결과와 분리해서 본다

## 6. Documentation And Validation

- `completed` Phase 13 문서 인덱스 반영
- `completed` roadmap / progress / analysis log 동기화
- `pending` phase closeout checklist skeleton 준비

## 현재 메모

- Phase 12 manual test는 아직 user-side에서 완료되지 않았다.
- 따라서 현재 운영 기준은:
  - `Phase 12`: implementation closed / manual_validation_pending
  - `Phase 13`: active planning and implementation
- 이번 phase의 핵심은 새 전략 추가가 아니라
  **실전형 후보를 실제 운용 후보로 더 좁히는 운영 계약**
  이다.
- Phase 13 first pass는 현재 `promotion_decision`을
  shortlist language로 다시 읽는 layer까지 연결한 상태다.
- ETF second pass는 now optional actual guardrail rule까지 연결된 상태다.
  다만 operability actual block rule과 PIT operability history는 아직 backlog다.
- probation / monitoring workflow first pass도 now connected 상태다.
  현재는 strategy rule이 아니라 deployment-readiness / monthly review contract를
  single / compare surface에서 읽는 layer로 구현되어 있다.
