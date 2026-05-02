# Phase 14 Real-Money Gate Calibration And Deployment Workflow Plan

## 목적

- Phase 13에서 만든 `promotion / shortlist / probation / deployment-readiness` surface를
  **실제 운영 판단에 더 쓸 수 있게 교정(calibration)** 하는 것이 이번 phase의 첫 번째 목적이다.
- 동시에, shortlist 후보를 실제 운용 행동으로 이어주는
  **deployment workflow bridge**를 어디까지 구현할지 정리하는 것이 두 번째 목적이다.

## 왜 이 phase가 필요한가

Phase 12와 Phase 13을 거치며,
이 프로젝트는 단순 백테스트 도구를 넘어서
실전형 해석 surface까지 갖추게 됐다.

하지만 사용자 검토와 backtest 탐색을 통해
다음 문제가 분명하게 드러났다.

1. 숫자가 좋은 전략도 `promotion = hold`에 자주 머문다
2. `shortlist`와 `deployment-readiness`가 보수적으로 잘 막히지만,
   이 막힘이 “전략이 나빠서”인지 “gate가 너무 엄격해서”인지 분리 분석이 필요하다
3. 현재 시스템은 후보 해석에는 강하지만,
   shortlist 후보를 실제 운용 행동으로 연결하는 workflow는 아직 얇다

즉 이번 phase의 핵심은
“전략을 더 많이 만드는 것”보다
**현재 gate가 어떻게 막는지 구조적으로 이해하고,
그 결과를 실제 운영 workflow로 연결하는 것**
이다.

## 사용자가 보류했던 논의

이번 phase에는 아래 보류 논의를 명시적으로 다시 올린다.

- `real-money gate calibration`
  - 왜 strong candidate가 반복적으로 `hold`가 되는가
  - 이 현상이 전략 품질 문제인지, policy threshold 문제인지
  - family별로 gate를 달리 읽어야 하는지

이 논의는 Phase 13 checklist QA 이후 다시 보기로 했고,
이번 Phase 14에서 정식 workstream으로 다룬다.

## 핵심 질문

1. 어떤 blocker가 `hold`를 가장 자주 만드는가
2. `watch / caution / unavailable / blocked`의 분포는 전략 family별로 어떻게 다른가
3. strict annual family와 ETF family가 같은 promotion threshold를 공유하는 것이 타당한가
4. `production_candidate`와 `real_money_candidate` 사이를 더 현실적으로 나누려면 무엇이 필요한가
5. shortlist 후보를 실제 portfolio action으로 연결하려면 어떤 operator workflow가 더 필요할까
6. ETF operability는 snapshot overlay를 넘어서 언제 actual block rule로 승격할 수 있을까

## 이번 phase의 우선순위

### 1. Gate Blocker Distribution Audit

- backtest history와 representative search result를 기준으로
  어떤 항목이 가장 자주 `hold`를 만드는지 집계한다
- 최소 집계 대상:
  - `validation_status`
  - `benchmark_policy_status`
  - `liquidity_policy_status`
  - `validation_policy_status`
  - `guardrail_policy_status`
  - `etf_operability_status`
  - `price_freshness`

### 2. Promotion / Shortlist Calibration Review

- repeated near-miss candidate를 family별로 모아
  gate가 과도한지, 아니면 전략 계약이 약한지 분리 분석한다
- calibration 후보 예시:
  - rolling underperformance threshold
  - worst rolling excess threshold
  - benchmark coverage floor
  - liquidity clean coverage floor
  - family-specific interpretation rule

### 3. Deployment Workflow Bridge

- shortlist 후보를 실제 operator action으로 넘기는 흐름을 더 명확히 한다
- 예:
  - shortlist candidate selection
  - paper probation note
  - monthly review handoff
  - small-capital trial readiness

### 4. PIT Operability Later-Pass Planning

- ETF operability를 snapshot overlay에서 actual block rule로 올리기 위해
  어떤 PIT history가 필요한지 정리한다
- 이번 phase에서 full implementation이 아니라도,
  최소한 schema / workflow / dependency를 확정한다

## 이번 phase에서 당장 하지 않는 것

- quarterly strict family promotion
- 대규모 신규 전략 라이브러리 확장
- 백테스트 UI 전면 리팩터링
- full live execution / broker integration

## 기대 산출물

- Phase 14 blocker distribution audit 문서
- promotion / shortlist calibration analysis 문서
- deployment workflow bridge first-pass 문서
- PIT operability later-pass decision 문서
- Phase 14 manual test checklist

## 성공 기준

- `hold`가 왜 반복되는지 설명 가능한 상태가 된다
- gate calibration을 “감”이 아니라 문서와 evidence로 논의할 수 있게 된다
- shortlist 후보를 paper probation / small-capital trial로 넘기는 operator flow가 더 또렷해진다
- 다음 live-deployment phase로 가기 전 필요한 PIT / execution-readiness backlog가 명확해진다
