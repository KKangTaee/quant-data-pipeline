# Phase 15 Next Phase Preparation

## 목적

- Phase 15 이후 다음 phase를 어떤 방향으로 여는 것이 가장 합리적인지 정리한다.
- 이번 phase에서 확보한 strongest/current candidate들이
  다음 구현 우선순위와 어떻게 연결되는지 남긴다.

## 현재 handoff 상태

Phase 15를 통해 다음 기반은 확보되었다.

- `Value` strongest raw baseline
- `Value` downside-improved / best-addition candidate
- `Quality` rescued / downside-improved candidate
- `Quality + Value` strongest practical blended candidate
- strategy hub + one-pager + strategy backtest log 운영 구조

즉 지금은
“좋은 후보가 있느냐 없느냐”가 아니라
**어떤 후보를 다음 operator workflow와 portfolio decision으로 넘길 것인가**
를 논의할 수 있는 상태다.

## 다음 phase에서 더 중요한 질문

다음에 중요한 것은 아래 세 묶음이다.

### 1. Candidate consolidation

- `Value`, `Quality`, `Quality + Value` strongest/current candidate를
  어떤 기준으로 shortlist 후보군으로 묶을 것인가
- strongest raw winner와 balanced alternative를
  어떻게 같이 관리할 것인가
- family별 후보를 saved portfolio / compare workflow에
  어떤 형태로 연결할 것인가

### 2. Downside / robustness follow-up

- `Value`는 `MDD`를 한 단계 더 낮출 수 있는가
- `Quality + Value`는 strongest gate tier를 유지한 채
  drawdown을 조금 더 줄일 수 있는가
- `Quality`는 weighting / replacement / overlay 확장으로
  consistency surface를 더 깨끗하게 만들 수 있는가

### 3. Operator handoff workflow

- strongest/current candidate를
  operator shortlist 문서나 saved portfolio와 어떻게 연결할 것인가
- strategy log entry에서 실제 운용 후보 관리로
  어떤 최소 필드가 더 필요할 것인가
- backtest report와 operator action note를
  어떤 흐름으로 묶을 것인가

## 추천 다음 방향

### 추천 1. Candidate Consolidation Phase

우선순위:

- family별 strongest/current candidate 카드 정리
- cross-family comparison surface 정리
- saved portfolio / compare / history linkage
- operator shortlist 후보군 문서화

이 방향이 좋은 이유:

- Phase 15에서 후보 품질 개선은 충분히 진행됐다.
- 이제는 후보를 더 많이 찾는 것보다
  **현재 strongest/current candidate를 운용 관점으로 묶는 일**이 더 중요하다.

### 추천 2. Downside Follow-Up Phase

우선순위:

- `Value`:
  - `Top N = 14 + psr` anchor 기준 추가 downside 실험
- `Quality`:
  - weighting / alternate overlay / bounded replacement
- `Quality + Value`:
  - strongest candidate 기준 lower-drawdown 대안 재탐색

이 방향이 좋은 이유:

- strongest/current candidate는 확보됐다.
- 이제는 gate tier를 유지한 채 `MDD`를 더 줄일 수 있는지 보는 bounded 실험이 가능하다.

### 추천 3. Operator Workflow Persistence Phase

우선순위:

- strategy log -> shortlist linkage
- candidate note / operator note persistence
- saved portfolio handoff 규격
- backtest run -> portfolio decision 연결

이 방향이 좋은 이유:

- 전략 후보가 정리된 뒤에는
  결국 operator workflow가 없으면 반복 검토가 흩어진다.

## 지금 바로 하지 않는 것

- blanket gate relaxation
- 새로운 대형 전략 family 확장
- full live deployment automation

이유:

- 현재 더 중요한 우선순위는
  **지금 확보한 후보들을 더 잘 묶고, 더 잘 비교하고, 더 잘 운영 흐름으로 연결하는 것**
  이기 때문이다.

## handoff 메모

- Phase 15 remaining backlog는 “좋은 후보가 아직 없다”가 아니다.
- 오히려
  **후보는 생겼고, 이제 그것을 어떻게 consolidate하고 operate할지 정하는 단계**
  라고 보는 편이 맞다.
- 따라서 다음 phase는
  candidate consolidation,
  downside follow-up,
  operator workflow persistence
  중 하나 또는 둘을 묶는 방향으로 여는 것이 가장 자연스럽다.
