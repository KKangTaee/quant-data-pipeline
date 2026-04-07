# Phase 13 Test Checklist

## 목적

- Phase 13에서 추가된 deployment-readiness / probation / monitoring surface가
  현재 UI와 meta에 맞게 읽히는지 수동으로 확인한다.
- 이번 checklist는 "전략 숫자가 좋은가"보다,
  **실전 후보를 어떻게 운영 언어로 해석하는지**를 검수하는 데 초점을 둔다.

## 추천 실행 순서

1. 결과 상단 `Latest Backtest Run` 안내 영역 확인
2. strict annual single 1개 확인
3. ETF single 1개 확인
4. compare에서 shortlist / probation / deployment surface 확인
5. history / `Load Into Form` 경로 확인
6. watch / caution / blocked 유도 테스트 확인

## 1. Latest Backtest Run 안내 영역

- single 전략 실행 후 결과 상단
- `Latest Backtest Run` 바로 아래 안내 영역 확인
- 확인:
  - 결과를 어떤 순서로 읽으면 되는지 한국어로 정리되어 있는지
  - 이번 실행에서 포함된 보기들이 요약되어 있는지
  - 주의해서 같이 봐야 할 항목이 한 묶음으로 보이는지
  - 안내 문구가 caption처럼 흩어져 있지 않고 한 번에 스캔 가능한지

## 2. Real-Money UX 구조

- `Backtest > Single Strategy`
- strict annual 또는 ETF 1개 실행
- 결과의 `Real-Money` 탭으로 이동
- 확인:
  - 내부가 `현재 판단 / 검토 근거 / 실행 부담 / 상세 데이터`로 나뉘어 있는지
  - 같은 의미의 정보가 카드/컨테이너처럼 묶여 보이는지
  - 각 섹션에 짧은 설명이 붙어 있어 처음 보는 사용자도 읽을 수 있는지
  - 승격 / shortlist / probation / deployment 정보가 한 화면에서 섞이지 않고 구분되는지

## 3. Candidate Shortlist Surface

- `Backtest > Single Strategy`
- `Quality / Value / Quality + Value > Strict Annual`
- 실행 후 결과 영역 상단 탭 중 `Real-Money` 탭으로 이동
- `Real-Money` 내부의 `현재 판단` 탭에서 먼저 확인
- 같은 내용이 `Execution Context`에도 요약되어 있는지 같이 확인
- 확인:
  - `Promotion Decision`
  - `Candidate Shortlist`
  - `Shortlist Status`
  - `Shortlist Next Step`
  - rationale가 보이는지
  - `Promotion Decision = hold`일 때 `Hold 해결 가이드`가 같이 보이는지
  - guide 안에 `항목 / 현재 상태 / 상태를 보는 위치 / 이 상태의 뜻 / 바로 해볼 일`이 함께 보이는지

## 4. ETF Second-Pass Guardrail Surface

- `GTAA`, `Risk Parity Trend`, `Dual Momentum`
- `Real-Money > 실행 부담`
- 확인:
  - `Underperformance Guardrail`
  - `Drawdown Guardrail`
  - trigger count / trigger share
  - `Real-Money` 탭과 `Execution Context`에 guardrail 상태가 같이 보이는지
  - guardrail이 꺼져 있어도 `OFF` 상태로 계속 보이는지

## 5. Hold 해결 가이드와 실행 부담 연결

- `Promotion Decision = hold`
- `Hold 해결 가이드`에서 `실행 부담 > Liquidity Policy` 같은 위치 안내가 나온 경우
- `Real-Money > 실행 부담`으로 이동
- 확인:
  - `Liquidity Policy`가 별도 섹션으로 보이는지
  - `Policy Status`
  - `Min Avg Dollar Volume 20D`
  - `Min Clean Coverage`
  - `Actual Clean Coverage`
  - `Liquidity Excluded Rows`
  - 왜 `unavailable / watch / caution`인지 설명 문구가 같이 보이는지
  - `무엇을 바꾸면 되는지`가 한국어 안내로 바로 보이는지
  - 특히 `Min Avg Dollar Volume 20D = 0.0M`일 때
    - 유동성 필터가 사실상 꺼져 있다는 설명이 나오는지
    - 그래서 `Liquidity Policy = unavailable`처럼 읽힐 수 있다는 안내가 보이는지

## 5-1. Guides 승격 해석 보강

- `Guides > 실전 승격 흐름 빠른 설명 > 어떻게 다음 단계로 가나`
- 확인:
  - `Promotion이 올라가려면` / `Shortlist가 올라가려면`이 분리된 카드로 보이는지
  - `상태는 어디에서 보나` 섹션이 있는지
  - `Validation`, `Benchmark Policy`, `Liquidity Policy`, `Validation Policy`, `Portfolio Guardrail Policy`, `ETF Operability`, `Price Freshness`의 화면 위치가 보이는지
  - `Watch / Caution / Unavailable / Error`가 각각 무엇을 뜻하는지 한 줄 설명이 보이는지
  - `Hold 해결 가이드`에서 보이는 표와 Guides 설명이 서로 연결되어 읽히는지

## 6. Probation And Monitoring Workflow

- single `Real-Money > 현재 판단`
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

## 7. Rolling / Out-Of-Sample Review

- benchmark가 있는 strict annual 또는 ETF run
- `Real-Money > 검토 근거`
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

## 8. Deployment-Readiness Checklist

- single `Real-Money > 현재 판단`
- 확인:
  - `Deployment Readiness` 섹션이 보이는지
  - `Status`
  - `Next Step`
  - `Pass / Watch / Fail / Unavailable`
  - `Checklist 상세 보기` expander 안의 checklist row table
  - rationale가 보이는지

## 9. Compare & Portfolio Builder Surface

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

## 10. Compare Meta Table

- compare 실행 후 `Meta`
- 확인:
  - `shortlist_status`
  - `probation_status`
  - `monitoring_status`
  - `deployment_readiness_status`
  - `rolling_review_status`
  - `out_of_sample_review_status`
  가 기록되는지

## 11. Execution Context

- single 실행 후 `Execution Context`
- 확인:
  - shortlist / probation / monitoring / deployment / rolling review / out-of-sample review가
    한 곳에서 같이 읽히는지

## 12. History / Load Into Form

- single 또는 compare 실행 후 `History`
- 확인:
  - Phase 13 관련 새 상태들은 history meta에서 읽히는지
  - `Load Into Form` 후 기존 입력 contract가 유지되는지

## 13. Watch / Caution / Blocked 유도 테스트

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

## 14. 용어/가이드 연결 확인

- `Candidate Shortlist Surface`를 보면서
- glossary와 화면 용어가 자연스럽게 이어지는지 확인
- 확인:
  - `Promotion`
  - `Shortlist`
  - `Validation`
  - `Benchmark`
  - `Liquidity`
  - `Guardrail`
  - `Min Avg Dollar Volume 20D`
  같은 용어가 현재 UI 해석과 어긋나지 않는지

## 15. Phase Boundary Interpretation

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
