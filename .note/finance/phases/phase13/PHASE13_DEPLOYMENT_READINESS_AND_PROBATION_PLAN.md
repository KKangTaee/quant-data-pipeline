# Phase 13 Deployment Readiness And Probation Plan

## 목적

- Phase 12에서 `real-money candidate` 수준까지 끌어올린 전략들을,
  실제 운용 후보로 더 좁히기 위한 **배치 전 검증 / probation / monitoring 계약**을 만든다.
- 이제 중요한 것은 새 전략을 더 많이 만드는 것이 아니라,
  **이미 승격된 후보 전략을 어떤 기준으로 최종 채택할지** 정하는 일이다.

쉬운 뜻:

- Phase 12는 "이 전략이 실전형 후보인가"를 정리한 phase였다.
- Phase 13은 그 다음 단계로,
  "이 후보를 실제로 돈 넣기 전에 어떤 검증과 관찰을 더 해야 하는가"를 정하는 phase다.
- 즉 지금부터는 단순 백테스트 숫자보다
  - out-of-sample 검증
  - probation
  - monitoring
  - candidate shortlist 운영
  이 더 중요하다.

## 왜 다음 phase가 이 방향이어야 하는가

Phase 12를 통해 다음 기반은 이미 생겼다.

- ETF 전략군 real-money first pass
- strict annual family promotion review surface
- benchmark / validation / liquidity / drawdown / guardrail policy
- strategy family 중심 backtest surface

즉 지금 부족한 것은 "전략을 돌리는 기능"이 아니라,
**그 결과를 실제 운용 후보로 채택하는 운영 계약**이다.

## 이번 phase의 핵심 질문

1. 어떤 전략이 paper / small-capital probation으로 넘어갈 가치가 있는가
2. 어떤 전략은 여전히 hold가 맞는가
3. probation 동안 무엇을 기록하고 무엇을 경고로 볼 것인가
4. backtest winner가 아니라 **실전형 shortlist**를 어떻게 운영할 것인가
5. monthly / rolling review에서 어떤 기준을 통과해야 실제 운용 비중을 늘릴 수 있는가

## 이번 phase에서 다룰 workstream

### 1. Candidate shortlist contract

- Phase 12 후보 전략을 shortlist surface로 묶는다.
- 후보별로 아래를 같이 남긴다.
  - strategy family
  - current contract
  - benchmark / guardrail / policy 상태
  - 추천 운용 상태
    - `watchlist`
    - `paper_probation`
    - `small_capital_trial`
    - `hold`

쉬운 뜻:
- 이제는 백테스트 결과 리스트가 아니라,
  실제 운용 후보 리스트를 따로 관리해야 한다.

### 2. ETF second-pass hardening

- ETF 전략군에 남아 있는 second-pass backlog를 정리한다.
- 예:
  - rolling underperformance review
  - stronger ETF guardrail
  - current operability warning을 실제 운용 rule로 쓸지 여부 검토
  - point-in-time operability later pass 필요성 판단

쉬운 뜻:
- ETF 전략군은 이미 후보가 되었지만,
  실전 운용 직전까지 가려면 한 단계 더 단단해질 여지가 있다.

### 3. Probation / monitoring workflow

- 후보 전략을 실제 투입 전 어떻게 관찰할지 정한다.
- 예:
  - paper tracking
  - small-capital trial
  - monthly review note
  - drawdown / underperformance / policy breach 경고

쉬운 뜻:
- "좋아 보여서 바로 투자"가 아니라,
  일정 기간 관찰한 뒤 비중을 늘리는 절차를 만든다.

### 4. Out-of-sample / rolling validation workflow

- fixed long-range backtest만 보지 않고,
  rolling window / recent regime review도 같이 본다.
- 목적:
  - 특정 구간 과최적화인지 확인
  - 현재 시장 국면에서도 여전히 일관된지 보기

쉬운 뜻:
- 과거 전체 평균만 좋다고 바로 믿지 않고,
  최근 구간에서도 버티는지 같이 본다.

### 5. Deployment-readiness checklist

- 최종적으로 실제 운용 직전 확인해야 할 기준을 checklist로 만든다.
- 이 checklist는
  - 전략 자체
  - 운용 후보 상태
  - monitoring 준비 상태
  를 같이 본다.

## 이번 phase의 우선순위

1. candidate shortlist contract
2. ETF second-pass hardening
3. probation / monitoring workflow
4. out-of-sample / rolling validation workflow
5. deployment-readiness checklist

## 이번 phase에서 일부러 바로 하지 않는 것

- quarterly strict prototype promotion
- 대규모 새 전략 라이브러리 추가
- 대형 UI 리디자인
- 대규모 백엔드 리팩터링

이유:
- 지금은 전략 수를 늘리는 것보다,
  **이미 후보가 된 전략을 실제 운용 후보로 좁히는 일**이 더 중요하기 때문이다.

## 예상 산출물

- candidate shortlist / probation policy 문서
- ETF second-pass hardening 문서
- monitoring workflow 문서
- deployment-readiness checklist
- phase closeout summary

## 성공 기준

이번 phase는 아래가 되면 practical completion으로 본다.

1. real-money candidate 전략을 shortlist 상태로 관리할 수 있다
2. probation / monitoring 기준이 문서와 UI surface에서 읽힌다
3. ETF 전략군 second-pass backlog 중 핵심이 정리된다
4. "백테스트 winner"와 "실전 투입 후보"를 구분하는 운영 계약이 생긴다
