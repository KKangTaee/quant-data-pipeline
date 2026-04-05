# Phase 12 Next Phase Preparation

## 목적

- Phase 12 이후 바로 어떤 방향으로 이어가는 것이 가장 합리적인지 정리한다.
- 이번 phase에서 실전형 승격 기준을 만든 결과가,
  다음 구현 우선순위와 어떻게 연결되는지 남긴다.

## 현재 handoff 상태

Phase 12를 통해 다음 기반은 확보되었다.

- ETF 전략군 real-money first pass
- strict annual family promotion review surface
- benchmark / validation / liquidity / drawdown 기반 정책 표면
- strategy family 중심 backtest surface

즉 지금은
"실전형으로 해석할 최소 계약"은 이미 생긴 상태다.

## 다음 phase에서 더 중요한 질문

다음에 중요한 것은
"이 전략들을 실제 운용 후보로 더 좁히려면 어떤 검증과 운영 계약이 더 필요한가"
이다.

즉 초점은 단순 기능 추가보다 아래 질문에 가까워야 한다.

1. ETF 전략군은 second-pass guardrail에서 무엇을 더 붙여야 하는가
2. current-operability를 point-in-time에 더 가깝게 만들 필요가 있는가
3. 실전 후보 전략을 paper/live probation으로 넘기기 전 어떤 검증이 더 필요한가
4. promotion candidate를 실제 운용 리스트로 고르는 workflow는 어떻게 만들 것인가

## 추천 다음 방향

다음 active phase는 아래 중 하나로 여는 것이 자연스럽다.

### 추천 1. 실전형 운용 검증 / deployment-readiness phase

우선순위:
- ETF 전략군 second-pass hardening
- probation / monitoring contract
- out-of-sample / rolling validation workflow
- promotion candidate shortlist 운영

이 방향이 좋은 이유:
- Phase 12에서 "승격 기준"은 만들었다.
- 이제는 "실제로 어떤 전략을 최종 채택할 것인가"가 더 중요해진다.

### 추천 2. strict annual 이후 broader strategy promotion phase

우선순위:
- strict annual candidate 간 최종 비교
- broad research path / baseline 전략과의 재검증
- 실전형 portfolio assembly 기준 정리

이 방향이 좋은 이유:
- Phase 12는 strategy-by-strategy hardening이었다.
- 다음에는 candidate 묶음을 실제 채택 기준으로 좁히는 단계가 필요하다.

## 지금 바로 하지 않는 것

이번 handoff에서는 아직 아래를 새 active phase로 열지 않는다.

- quarterly strict prototype promotion
- 대규모 새 전략 라이브러리 확장
- UI 대형 리팩터링

이유:
- 현재 프로젝트의 더 중요한 우선순위는
  새 전략을 많이 늘리는 것이 아니라,
  **이미 후보가 된 전략을 실전형 판단 기준에서 더 엄격하게 검증하는 것**
  이기 때문이다.

## handoff 메모

- Phase 12 remaining backlog는 "미완료"가 아니라 "다음 phase 주제"로 보는 편이 맞다.
- 따라서 다음 phase는
  실전형 전략의 최종 채택 / probation / monitoring 방향으로 여는 것이 가장 자연스럽다.
