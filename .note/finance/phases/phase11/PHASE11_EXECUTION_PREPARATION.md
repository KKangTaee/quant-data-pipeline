# Phase 11 Execution Preparation

## 목적

- Phase 11을 바로 열 때 어떤 순서로 구현하면 되는지 미리 고정한다.
- productization phase가 되더라도
  실전 투자 기준과 연구 workflow가 섞여 흐려지지 않게 준비한다.

## Phase 11의 위치

Phase 11은
전략/비교/히스토리/weighted builder를
실제 사용자 workflow로 묶는 phase다.

다만 현재 프로젝트에서는
다음 전제가 있다.

- product/workflow 측면에서는 natural next phase
- real-money validation 측면에서는
  `historical dynamic PIT universe` workstream이 먼저 올 수 있음

이 문서는 원래
Phase 11을 언제 열어도 흔들리지 않도록 준비하기 위한 문서였고,
현재는 실제 활성화 이후에도
**chapter 순서를 확인하는 reference 문서**
로 계속 사용한다.

## 권장 구현 순서

### Chapter 1. Saved Portfolio Contract

목표:

- weighted portfolio를 저장 가능한 first-class object로 만든다

핵심 결정:

- portfolio id / name / description
- strategy set
- weight set
- period / benchmark / overlay inputs
- preset vs manual universe metadata
- rerun payload snapshot

산출물:

- saved portfolio contract 문서
- persistence shape 초안

### Chapter 2. Compare-To-Portfolio Bridge

목표:

- compare 결과를 손으로 다시 입력하지 않고
  weighted portfolio builder로 자연스럽게 넘길 수 있게 만든다

핵심 결정:

- compare selected strategies를 builder에 어떻게 전달할지
- strategy-specific advanced inputs를 어떤 범위까지 함께 넘길지
- compare 결과에서 어떤 selection unit을 저장 대상으로 볼지

산출물:

- bridge rule 문서
- first-pass UI handoff 설계

### Chapter 3. Saved Portfolio UI First Pass

목표:

- 사용자가 저장 / 다시 불러오기 / 수정 / rerun을 할 수 있게 한다

핵심 surface:

- create portfolio
- load portfolio
- edit weights
- rerun portfolio
- portfolio detail view

산출물:

- first-pass UI
- history integration 초안

### Chapter 4. Richer Portfolio Readouts

목표:

- 단순 equity curve를 넘어서
  “왜 이런 결과가 나왔는지”를 portfolio 단위로 읽을 수 있게 한다

핵심 readout:

- contribution summary
- strategy-level exposure summary
- rebalance change summary
- drawdown / benchmark comparison 강화

산출물:

- portfolio result readout spec
- first-pass result surface

### Chapter 5. Workflow Integration

목표:

- saved run / saved portfolio / history / rerun이 하나의 흐름으로 읽히게 만든다

핵심 질문:

- saved run과 saved portfolio는 어떻게 다를까
- compare history와 portfolio history는 어떻게 연결할까
- 어떤 정보는 immutable snapshot으로 저장해야 할까

산출물:

- workflow relationship 문서
- UX integration 정리

### Chapter 6. Validation And Handoff

목표:

- Phase 11 결과를 later batch QA에 자연스럽게 얹을 수 있게 만든다

산출물:

- `PHASE11_TEST_CHECKLIST.md`
- roadmap / index / progress sync

## 구현 전 꼭 확인할 것

1. Phase 11이 실제로 active phase가 되는지
2. 그 전에 `historical dynamic PIT universe`(Phase 10)를 먼저 끝냈는지
3. saved portfolio가 current static preset semantics에 기대는 부분을
   UI에서 충분히 설명할지

## recommendation

Phase 11을 열게 되면
가장 먼저 만들 것은 “더 많은 지표”가 아니라
**saved portfolio contract와 compare-to-portfolio bridge**다.

이 둘이 먼저 정리돼야
이후 readout / history / rerun surface가 흔들리지 않는다.
