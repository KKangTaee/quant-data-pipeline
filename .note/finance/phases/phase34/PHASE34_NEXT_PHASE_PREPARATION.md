# Phase 34 Next Phase Preparation

## 목적

이 문서는 Phase 34 이후 Phase 35 `Post-Selection Operating Guide`로 넘어갈 때 필요한 질문을 미리 정리하는 초안이다.

현재 Phase 34 구현은 완료됐고 manual QA 대기 상태다.
이 문서는 Phase34 QA 통과 후 Phase35로 넘어갈 때의 handoff 기준을 정리한다.

## 현재 handoff 상태

- Phase 33은 paper tracking ledger 저장 / review / Phase34 handoff를 완료했다.
- Phase 34는 `Backtest > Final Review`를 별도 탭으로 분리해 Phase 35가 읽을 최종 후보 판단 기록을 만들 수 있게 했다.
- Phase 34의 현재 main flow에서는 별도 Paper Ledger 저장을 Phase35 입력 필수 조건으로 요구하지 않는다. paper observation 기준은 final review record 안에 포함된다.
- 아직 Phase 35 post-selection operating guide는 만들지 않았다.

## 다음 phase에서 더 중요한 질문

1. 최종 선정된 포트폴리오를 어떤 리밸런싱 / 중단 / 축소 / 재검토 규칙으로 운영할 것인가?
2. 선정 이후에도 live approval / 주문 지시와 어떻게 분리할 것인가?
3. 선정 후 성과 악화나 data trust gap이 생기면 어떤 route로 되돌릴 것인가?

## 다음 phase에서 실제로 할 작업

쉽게 말하면:

- Phase 35는 최종 후보로 선정된 포트폴리오를 어떻게 운영하고, 언제 멈추거나 줄이거나 다시 볼지 정리한다.

주요 작업:

1. Post-selection operating policy 정의
   - 리밸런싱 cadence, 중단 조건, 축소 조건, 재검토 조건을 정리한다.
2. Selected portfolio operating surface 또는 guide 추가
   - 최종 선정 이후 사용자가 따라야 할 운영 기준을 보여준다.
3. Live approval 경계 유지
   - Phase35도 broker order / 자동매매와 분리한다.

## 추천 다음 방향

Phase 34가 끝나면 Phase 35 `Post-Selection Operating Guide`로 넘어가는 것이 자연스럽다.

왜냐하면 최종 후보를 선정한 뒤에는 "선정했다"에서 끝나는 것이 아니라,
언제 리밸런싱하고 언제 중단할지 운영 기준이 필요하기 때문이다.

## handoff 메모

- Phase 35는 Phase 34 final review record의 selected route, operator constraints, selected components, paper observation snapshot, Phase35 handoff를 최소 입력으로 읽어야 한다.
- Phase35의 기본 입력 source는 `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`에서 `decision_route = SELECT_FOR_PRACTICAL_PORTFOLIO`이고 `phase35_handoff.handoff_route = READY_FOR_POST_SELECTION_OPERATING_GUIDE`인 row다.
- 보류 / 거절 / 재검토 row는 Phase35 운영 가이드 대상이 아니라 review backlog 또는 제외 기록으로 읽는다.
- Phase 35에서도 broker order, 자동 매매, live approval은 별도 범위로 유지한다.
