# Phase 27 Next Phase Preparation

## 목적

이 문서는 Phase 27 이후 어떤 질문으로 Phase 28을 여는 것이 자연스러운지 정리하기 위한 handoff 문서다.

현재 예상되는 Phase 28은 `Strategy Family Parity And Cadence Completion`이다.

## 현재 handoff 상태

- Phase 27은 complete / manual_qa_completed 상태다.
- Phase 27에서 데이터 신뢰성 표시가 사용자 QA까지 통과했으므로, 다음 질문은 annual / quarterly / 신규 전략이 같은 수준의 UX와 metadata를 갖는지로 이동한다.

## 다음 phase에서 더 중요한 질문

1. annual strict, quarterly strict, 신규 ETF 전략이 같은 방식으로 preflight / warning / history / replay 정보를 보존하는가
2. annual에는 있는 Real-Money / Guardrail / contract surface가 quarterly와 신규 전략에서는 어디까지 필요한가
3. 전략 family별 차이가 의도된 차이인지, 아직 덜 만든 차이인지 구분되는가

## 다음 phase에서 실제로 할 작업

쉽게 말하면:

- Phase 28은 전략마다 옵션과 저장 / 재실행 흐름이 너무 다르게 느껴지지 않도록 맞추는 phase다.
- Phase 27에서 만든 데이터 신뢰성 표시도 각 전략 family에 맞게 어디까지 공통화할지 결정한다.

주요 작업:

1. 전략 family별 옵션 차이 표준화
   - annual, quarterly, Global Relative Strength의 UI / payload / meta 차이를 비교한다.
2. history / load-into-form / saved replay parity 확인
   - 실행 설정을 다시 불러올 때 전략별 중요한 값이 빠지지 않는지 확인한다.
3. Real-Money / Guardrail parity 범위 결정
   - 모든 전략에 같은 옵션을 강제로 붙일지, 전략 성격에 따라 다르게 둘지 결정한다.

## 추천 다음 방향

Phase 28은 `Strategy Family Parity And Cadence Completion`이 자연스럽다.

이유:

- Phase 23에서 quarterly를 제품 흐름으로 올렸고, Phase 24에서 신규 ETF 전략을 추가했다.
- Phase 27에서 데이터 신뢰성 표면을 만들면, 그 다음에는 전략 family별 UX와 metadata가 균형 있게 이어져야 한다.
- 후보 검토 workflow인 Phase 29로 가기 전에 전략별 실행 / 저장 / 재실행 의미가 흔들리지 않아야 한다.

## handoff 메모

- Phase 28은 새 전략을 많이 추가하는 phase가 아니라, 이미 있는 전략 family들의 사용성과 저장 계약을 맞추는 phase다.
- Phase 27에서 만든 `Data Trust Summary`와 `price_freshness` 개념은 Phase 28에서 각 전략 family에 맞게 공통화 / 차별화 범위를 정한다.
