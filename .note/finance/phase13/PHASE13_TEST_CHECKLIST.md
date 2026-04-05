# Phase 13 Test Checklist

## 목적

- Phase 13에서 추가된 deployment-readiness / probation / monitoring surface가
  현재 UI와 meta에 맞게 읽히는지 수동으로 확인한다.
- 이번 checklist는 "전략 숫자가 좋은가"보다,
  **실전 후보를 어떻게 운영 언어로 해석하는지**를 검수하는 데 초점을 둔다.

## 추천 실행 순서

1. strict annual single 1개 확인
2. ETF single 1개 확인
3. compare에서 shortlist / probation / deployment surface 확인
4. history / `Load Into Form` 경로 확인
5. watch / caution / blocked 유도 테스트 확인

## 1. Candidate Shortlist Surface

- `Backtest > Single Strategy`
- `Quality / Value / Quality + Value > Strict Annual`
- 확인:
  - `Promotion Decision`
  - `Candidate Shortlist`
  - `Shortlist Status`
  - `Shortlist Next Step`
  - rationale가 보이는지

## 2. ETF Second-Pass Guardrail Surface

- `GTAA`, `Risk Parity Trend`, `Dual Momentum`
- 확인:
  - `Underperformance Guardrail`
  - `Drawdown Guardrail`
  - trigger count / trigger share
  - `Real-Money` 탭과 `Execution Context`에 guardrail 상태가 같이 보이는지

## 3. Probation And Monitoring Workflow

- single `Real-Money`
- 확인:
  - `Probation`
  - `Stage`
  - `Probation Review`
  - `Monitoring`
  - `Monitoring Review`
  - `Monitoring Focus`
  - `Monitoring Breach Signals`
- 기대:
  - `hold`면 보통 `not_ready / blocked`
  - `paper_probation`이면 `paper_tracking`
  - `small_capital_trial`이면 `small_capital_live_trial`

## 4. Rolling / Out-Of-Sample Review

- benchmark가 있는 strict annual 또는 ETF run
- 확인:
  - `Rolling Review`
  - `Rolling Window`
  - `Recent Excess`
  - `Recent DD Gap`
  - `OOS Review`
  - `In-Sample Excess`
  - `Out-Sample Excess`
  - `Excess Change`
- 기대:
  - `normal / watch / caution / unavailable` 상태가 label과 함께 읽히는지

## 5. Deployment-Readiness Checklist

- single `Real-Money`
- 확인:
  - `Deployment Readiness Checklist` 섹션이 보이는지
  - `Status`
  - `Next Step`
  - `Pass / Watch / Fail / Unavailable`
  - checklist row table
  - rationale가 보이는지

## 6. Compare & Portfolio Builder Surface

- strict annual 1개 + ETF 1개 이상 선택
- 확인:
  - `Strategy Highlights`에
    - `Shortlist`
    - `Probation`
    - `Monitoring`
    - `Deployment`
    - `Rolling Review`
    - `OOS Review`
    가 보이는지
  - focused strategy의 `Real-Money Contract`에도 같은 정보가 보이는지

## 7. Compare Meta Table

- compare 실행 후 `Meta`
- 확인:
  - `shortlist_status`
  - `probation_status`
  - `monitoring_status`
  - `deployment_readiness_status`
  - `rolling_review_status`
  - `out_of_sample_review_status`
  가 기록되는지

## 8. Execution Context

- single 실행 후 `Execution Context`
- 확인:
  - shortlist / probation / monitoring / deployment / rolling review / out-of-sample review가
    한 곳에서 같이 읽히는지

## 9. History / Load Into Form

- single 또는 compare 실행 후 `History`
- 확인:
  - Phase 13 관련 새 상태들은 history meta에서 읽히는지
  - `Load Into Form` 후 기존 입력 contract가 유지되는지

## 10. Watch / Caution / Blocked 유도 테스트

- strict annual:
  - manual small ticker set
  - `Historical Dynamic PIT Universe`
  - benchmark contract 사용
- ETF:
  - guardrail enabled
  - benchmark 지정
- 확인:
  - 어떤 케이스는 `blocked`
  - 어떤 케이스는 `paper_only`
  - 어떤 케이스는 `review_required`
  로 읽히는지

## 11. Phase Boundary Interpretation

- 확인:
  - Phase 12는 아직 `manual_validation_pending`으로 기억되는지
  - Phase 13은 deployment-readiness / probation / monitoring phase로 읽히는지
  - ETF operability actual block rule은 아직 later-pass backlog라는 설명과 충돌이 없는지

## 한 줄 판단 기준

- 이번 checklist는
  "전략이 좋다 / 나쁘다"
  를 보는 것이 아니라,
  **그 전략을 지금 어떤 운영 상태로 읽어야 하는지 product surface가 제대로 말해주는지**
  를 보는 체크리스트다.
