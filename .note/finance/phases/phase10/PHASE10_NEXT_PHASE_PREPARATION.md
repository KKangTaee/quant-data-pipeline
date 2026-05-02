# Phase 10 Next Phase Preparation

## 목적

- Phase 10 종료 이후,
  다음 major phase를 어떤 방향으로 여는 것이 자연스러운지 정리한다.
- dynamic PIT validation contract가 들어온 뒤,
  이제 무엇을 product/workflow 쪽으로 확장해야 하는지 연결해 둔다.

## Phase 10 종료 시점의 출발점

현재 확보된 상태:

- `Static Managed Research Universe` vs `Historical Dynamic PIT Universe` 분리
- annual strict family dynamic PIT single / compare / history 지원
- quarterly strict prototype dynamic PIT single / compare / history 지원
- continuity/profile diagnostics
- dynamic universe history artifact persistence
- result UI의 `Dynamic Universe` 상세 탭

즉 다음 단계는
validation contract를 처음부터 다시 만드는 phase라기보다,
**지금 확보한 전략 / compare / history / dynamic PIT surface를 실제 연구 워크플로우로 묶는 phase**
가 더 자연스럽다.

## 가장 자연스러운 다음 방향

### 후보 1. Portfolio Productization And Research Workflow

가장 추천되는 다음 방향이다.

핵심 이유:

- 이제 single / compare / history / dynamic validation이 모두 있다
- 하지만 반복 연구를 실제 workflow로 쓰기엔
  저장, 재조합, compare-to-portfolio, rerun bridge가 아직 약하다

핵심 작업:

- saved portfolio contract
- compare-to-portfolio bridge
- weighted portfolio UX 정리
- richer portfolio readouts
- saved run / saved portfolio / rerun workflow 정리

이 방향은
Phase 10에서 만든 validation contract를 실제 사용자 workflow로 끌어올리는 단계다.

### 후보 2. Stronger PIT Source Reinforcement

가능은 있지만 다음 active phase의 메인 축으로 두기엔 우선순위가 조금 낮다.

예:

- stronger listing / delisting source
- better symbol continuity source
- closer-to-perfect constituent-history source

이유:

- 실전형 validation contract는 이미 first/second pass로 열렸다
- 지금 즉시 product value를 크게 올리는 쪽은 workflow/productization이다

다만 이 항목들은 장기 backlog로 유지하는 것이 맞다.

## 추천 방향

Phase 11은 아래 방향으로 여는 것이 가장 합리적이다.

- `Portfolio Productization And Research Workflow`

의도:

- 지금까지 구현한 전략 / compare / history / dynamic validation을
  실제 연구/운영용 workflow로 묶는다
- 단발성 백테스트 surface를 넘어서
  저장 / 불러오기 / 재실행 / 비교가 되는 제품형 흐름으로 발전시킨다

## 추천 첫 작업

1. saved portfolio persistence contract 고정
2. compare -> weighted portfolio builder bridge 연결
3. saved portfolio UI first pass
4. portfolio contribution / exposure readout 보강
5. history / rerun / saved portfolio 연결

## 현재 상태

- Phase 10 closeout:
  - `practically_completed`
- next-phase candidate evaluation:
  - `completed`
- recommended Phase 11 direction:
  - `Portfolio Productization And Research Workflow`
- next phase formal opening:
  - `ready`

## 메모

- current dynamic PIT는 여전히 `approximate PIT + diagnostics` contract다.
- 따라서 Phase 11이 productization phase로 열리더라도,
  더 강한 constituent-history / continuity source 보강은 long-term backlog로 계속 유지해야 한다.
- 즉 다음 단계는 validation contract를 부정하는 phase가 아니라,
  **현재 validation contract 위에 실제 workflow를 얹는 phase**다.
