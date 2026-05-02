# Phase 14 Next Phase Preparation

## 목적

- Phase 14 이후 다음 phase를 어떤 방향으로 여는 것이 가장 합리적인지 정리한다.
- 이번 phase에서 생긴 calibration / workflow / PIT boundary가
  다음 구현 우선순위와 어떻게 연결되는지 남긴다.

## 현재 handoff 상태

Phase 14를 통해 다음 기반은 확보되었다.

- repeated `hold` blocker distribution
- family-specific calibration question
- strict annual next threshold experiment 후보
- ETF next coverage-interpretation experiment 후보
- deployment workflow persistence gap 정의
- PIT operability later-pass dependency 정의

즉 지금은
“무엇이 막히는지 모르는 상태”가 아니라
**어떤 실험과 어떤 persistence 구현을 다음에 해야 하는지 아는 상태**다.

## 다음 phase에서 더 중요한 질문

다음에 중요한 것은 아래 두 묶음이다.

### 1. calibration execution

- strict annual internal validation threshold를 실제로 어느 범위에서 조정할 것인가
- ETF operability coverage interpretation을 어느 수준으로 바꿀 것인가
- 그 변경이
  - `promotion`
  - `shortlist`
  - `deployment`
  - performance profile
  에 어떤 영향을 주는가

### 2. operator workflow persistence

- paper probation handoff object가 필요한가
- monthly review note를 어디에 저장할 것인가
- small-capital trial action record는 어떤 최소 필드가 필요한가
- backtest result와 operator action을 어떻게 연결할 것인가

## 추천 다음 방향

### 추천 1. Threshold Experiment Execution Phase

우선순위:

- strict annual:
  - `worst_excess` severe boundary
  - `single severe -> caution`
  - drawdown-gap secondary review
- ETF:
  - `data_coverage` caution boundary
  - missing-data semantics
  - denominator choice

이 방향이 좋은 이유:

- Phase 14에서 질문이 이미 충분히 좁혀졌다.
- 이제는 실제 code-level experiment와 rerun evidence가 필요하다.

### 추천 2. Operator Workflow Persistence Phase

우선순위:

- paper probation handoff object
- monthly review note / operator log
- small-capital trial action record
- run -> action linkage

이 방향이 좋은 이유:

- Phase 13~14를 통해 interpretation surface는 충분히 생겼다.
- 이제는 operator action을 남길 persistent workflow가 필요하다.

### 추천 3. PIT Operability Implementation Phase

우선순위:

- historical asset-profile snapshot schema
- append-only collector path
- PIT loader
- runtime source split
- ETF actual block rule later pass

이 방향이 좋은 이유:

- current snapshot operability는 useful diagnostic이다.
- 하지만 true live contract로 쓰려면 PIT가 필수다.

## 지금 바로 하지 않는 것

- 새로운 대형 전략 family 추가
- blanket default threshold relaxation
- full live deployment automation

이유:

- 현재 프로젝트의 더 중요한 우선순위는
  후보 전략 수를 늘리는 것보다,
  **현재 gate와 operator workflow를 실제 운용 가능한 수준으로 더 밀어붙이는 것**
  이기 때문이다.

## handoff 메모

- Phase 14 remaining backlog는 “분석 미완료”보다
  **다음 phase 구현 주제**로 보는 편이 맞다.
- 따라서 다음 phase는
  threshold experiment execution,
  operator workflow persistence,
  PIT operability implementation
  중 하나 또는 둘을 묶는 방향으로 여는 것이 가장 자연스럽다.

