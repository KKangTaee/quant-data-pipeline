# Phase 13 Next Phase Preparation

## 목적

- Phase 13 이후 다음 phase를 어떤 방향으로 여는 것이 가장 합리적인지 정리한다.
- 이번 phase에서 생긴 deployment-readiness contract가,
  다음 구현 우선순위와 어떻게 연결되는지 남긴다.

## 현재 handoff 상태

Phase 13을 통해 다음 기반은 확보되었다.

- candidate shortlist language
- probation / monitoring workflow
- rolling / out-of-sample review
- deployment-readiness checklist
- ETF second-pass guardrail actual rule

즉 지금은
"실전 후보를 어떻게 읽을지"에 대한 운영 계약은 이미 생긴 상태다.

## 다음 phase에서 더 중요한 질문

다음에 중요한 것은
"이 계약을 실제 live deployment 쪽으로 더 밀려면 무엇이 더 필요한가"
이다.

즉 초점은 아래 질문에 가까워야 한다.

1. ETF current-operability를 actual block rule로 쓸 수 있으려면 PIT가 얼마나 더 필요할까
2. monthly review note와 run history를 실제 probation log로 승격할 필요가 있을까
3. rolling / out-of-sample review를 반복 실행하는 dedicated workflow가 필요할까
4. shortlist 전략을 실제 portfolio action으로 연결하려면 어떤 capital-sizing / execution layer가 더 필요할까

## 추천 다음 방향

### 추천 1. Live Deployment Workflow Phase

우선순위:
- probation note / monthly review logging
- shortlist portfolio action workflow
- deploy gating
- actual review cadence tooling

이 방향이 좋은 이유:
- Phase 13에서 판단 언어는 생겼다.
- 이제는 그 판단을 실제 운용 workflow로 이어주는 단계가 필요하다.

### 추천 2. PIT Operability And Execution-Readiness Phase

우선순위:
- ETF point-in-time operability later pass
- operability actual block rule 검토
- richer execution-readiness policy

이 방향이 좋은 이유:
- 현재 operability는 snapshot overlay다.
- 실제 live contract로 더 밀려면 PIT 보강이 중요하다.

## 지금 바로 하지 않는 것

- quarterly strict prototype promotion
- 대규모 새 전략 라이브러리 추가
- backtest UI 대형 리팩터링

이유:
- 현재 프로젝트의 더 중요한 우선순위는
  새 전략 수를 늘리는 것이 아니라,
  **이미 후보가 된 전략을 실제 운용 계약으로 더 밀어붙이는 것**
  이기 때문이다.

## handoff 메모

- Phase 13 remaining backlog는 "미완료"가 아니라 "다음 phase 주제"로 보는 편이 맞다.
- 따라서 다음 phase는
  live deployment workflow 또는 PIT execution-readiness 방향으로 여는 것이 가장 자연스럽다.
