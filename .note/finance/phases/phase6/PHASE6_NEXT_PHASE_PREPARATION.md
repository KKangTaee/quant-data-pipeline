# Phase 6 Next Phase Preparation

## 목적

- Phase 6 종료 이후,
  다음 major phase를 어떤 방향으로 여는 것이 가장 자연스러운지 정리한다.
- Phase 7 kickoff 전에
  현재 구현 상태와 남은 실제 blocker를 연결해 둔다.

## Phase 6 종료 시점의 출발점

현재 확보된 상태:
- strict annual family 3종에 `Market Regime Overlay` first pass 연결 완료
- single / compare / history / interpretation / prefill까지 overlay-aware 흐름 정리 완료
- `Quality Snapshot (Strict Quarterly Prototype)` research-only entry path 구현 완료
- Phase 6 manual test checklist 작성 및 주요 UI/UX 보강 완료

즉 다음 phase는
overlay 자체를 다시 다듬는 phase라기보다,
**quarterly strict family가 왜 짧게만 시작되는지 해결하는 data/PIT phase**
로 넘어가는 것이 더 자연스럽다.

## 가장 자연스러운 다음 방향

### 후보 1. Quarterly Coverage And Statement PIT Hardening

가장 추천되는 다음 phase 방향이다.

핵심 문제:
- quarterly prototype이 현재 요청 start date보다 훨씬 뒤에서 active하게 시작될 수 있다
- 이는 전략 아이디어 문제가 아니라
  quarterly statement shadow coverage / timing / PIT ledger depth 문제에 더 가깝다

핵심 작업:
- upstream statement API payload 재검토
- 실제 filing / acceptance / available timing field 확인
- raw statement ledger 구조 보강 또는 재설계
- quarterly shadow fundamentals / factors 재생성
- quarterly strict family longer-history 검증

이 방향은
현재 quarterly prototype이 research-only에 머무는 이유를 직접 해결하는 phase다.

### 후보 2. Overlay Layer Further Expansion

가능은 하지만 우선순위는 낮다.

예:
- third overlay candidate
- intramonth regime trigger
- more complex defensive rotation

이유:
- 현재 quarterly 쪽 data foundation이 약한 상태에서 overlay를 더 얹는 것보다
  strategy-library의 데이터 기반을 먼저 강화하는 편이 더 실용적이다.

### 후보 3. Reporting / Visualization Polish

이 또한 가능하지만 다음 major phase 중심으로 보기엔 약하다.

예:
- interpretation table 추가 확장
- compare history replay 고도화
- visualization polish

이유:
- 지금은 보고서보다 quarterly feasibility를 막는 upstream data quality가 더 큰 blocker다.

## 추천 방향

Phase 7은 아래 방향으로 여는 것이 가장 합리적이다.

- `Quarterly Coverage And Statement PIT Hardening`

의도:
- quarterly strict family를 실제 longer-history 연구가 가능하도록 만들기
- point-in-time correctness를 statement raw layer에서 더 엄격하게 정리하기

## 추천 첫 작업

1. current statement API payload inspection
2. raw statement ledger / timing column review
3. quarterly shadow coverage gap measurement
4. schema / loader / backfill plan 고정

즉 다음 phase의 첫 단계는
전략 튜닝이 아니라
**data model and PIT timing reality check**
에 가깝다.

## 현재 상태

- Phase 6 closeout:
  - `completed`
- next-phase candidate evaluation:
  - `completed`
- recommended Phase 7 direction:
  - `Quarterly Coverage And Statement PIT Hardening`
- next phase formal opening:
  - `ready`
