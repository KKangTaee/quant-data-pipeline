# Phase 28 Next Phase Preparation

## 목적

이 문서는 Phase 28 이후 어떤 질문으로 Phase 29를 여는 것이 자연스러운지 정리하기 위한 handoff 문서다.

현재 예상되는 Phase 29는 `Candidate Review And Recommendation Workflow`다.

## 현재 handoff 상태

- Phase 28은 complete / manual_qa_completed 상태다.
- 사용자 manual QA가 완료되었으므로 Phase 29로 넘어갈 수 있다.
- Phase 28에서 strategy family별 실행 / 저장 / 재실행 의미와 Real-Money / Guardrail 범위가 안정되었으므로, 다음 질문은 백테스트 결과를 어떻게 후보 검토 workflow로 넘길지다.

## 다음 phase에서 더 중요한 질문

1. 백테스트 결과를 current candidate, near miss, watchlist, pre-live 후보로 어떻게 표준화할 것인가
2. 좋은 결과와 보류 결과를 어떤 registry / report / UI surface에 남길 것인가
3. 사용자에게 투자 추천처럼 보이지 않으면서도 후보 검토 흐름은 어떻게 명확히 만들 것인가

## 다음 phase에서 실제로 할 작업

쉽게 말하면:

- Phase 29는 좋은 백테스트 결과를 임시 메모가 아니라 반복 가능한 후보 검토 절차로 넘기는 phase다.
- Phase 28에서 strategy별 저장 / 재실행 의미를 맞춘 뒤, 그 결과를 candidate review workflow로 연결한다.

주요 작업:

1. 후보 상태와 registry 흐름 정리
   - current candidate, near miss, watchlist, hold, pre-live 후보를 어떻게 나눌지 정한다.
2. backtest result to candidate handoff
   - Latest Backtest Run이나 History에서 후보 기록으로 넘기는 UX를 정리한다.
3. operator review summary 표준화
   - 왜 이 후보를 유지 / 보류 / 재검토하는지 짧게 남기는 형식을 정한다.

## 추천 다음 방향

Phase 29는 `Candidate Review And Recommendation Workflow`가 자연스럽다.

이유:

- Phase 27은 결과의 데이터 조건을 보이게 했다.
- Phase 28은 strategy family별 실행 / 저장 / 재실행 차이를 정리한다.
- 그 다음에는 결과를 후보로 남기고 다시 검토하는 절차가 필요하다.

## handoff 메모

- Phase 29는 자동 투자 추천이나 live approval이 아니다.
- 후보 검토 workflow는 최종 목표인 투자 후보 / 포트폴리오 구성 제안으로 가기 위한 중간 운영 절차다.
- 이 문서는 Phase 28 closeout 이후 Phase 29 opening handoff 기준으로 사용한다.
