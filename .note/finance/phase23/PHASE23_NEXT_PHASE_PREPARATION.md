# Phase 23 Next Phase Preparation

## 목적

이 문서는 `Phase 23` 이후 어떤 질문으로 다음 phase를 여는 것이 자연스러운지 미리 정리하는 handoff 문서다.

현재는 Phase 23 representative smoke validation과 history / saved replay roundtrip code check까지 진행된 상태이므로,
최종 handoff가 아니라 남은 UI QA와 다음 phase 방향을 함께 보는 메모로 읽는다.

## 현재 handoff 상태

Phase 23이 끝나면 다음이 고정되어 있어야 한다.

- quarterly strict family가 제품 기능으로 어디까지 믿고 쓸 수 있는지
- annual / quarterly / alternate cadence의 입력 차이가 무엇인지
- compare / history / saved replay에서 cadence 설정이 재현되는지
- representative smoke validation 기준이 무엇인지

현재까지는 quarterly 3개 family가 non-default portfolio handling contract를 받은 상태로
실제 DB-backed runtime에서 실행되고,
result bundle meta에 contract 값이 남는 것까지 확인했다.
또한 history record, history payload, saved portfolio strategy override까지 같은 contract 값이 보존되는 것을 코드 레벨에서 확인했다.
manual QA 중에는 compare 화면의 Annual / Quarterly variant 변경이 즉시 하단 입력 UI를 바꾸지 않는 문제가 발견되어,
variant selector를 form 밖으로 이동하는 방식으로 보강했다.

## 다음 phase에서 더 중요한 질문

1. 새 전략을 추가할 때 어떤 cadence를 기본 지원해야 하는가
2. research note에서 finance strategy implementation으로 넘어갈 때 어떤 템플릿을 따라야 하는가
3. 신규 전략이 compare / history / saved replay까지 자연스럽게 연결되려면 최소 구현 단위가 무엇인가

## 추천 다음 방향

Phase 23이 닫히면 기본 다음 방향은 `Phase 24 New Strategy Expansion`이다.

이유는 단순하다.
cadence별 실행 경로가 안정되어야 새 전략을 붙일 때 annual만 되는 반쪽 기능이 되지 않는다.

## handoff 메모

- Phase 23은 투자 분석 phase가 아니다.
- Phase 24도 먼저 "새 전략을 제품에 붙이는 표준 구현 경로"를 만드는 phase로 열어야 한다.
- 사용자가 별도로 특정 전략 분석을 요청하면 그 분석은 `사용자 요청 분석`으로 분리한다.
