# Phase 33 Next Phase Preparation

## 목적

이 문서는 Phase 33 이후 Phase 34 `Final Portfolio Selection Decision Pack`으로 넘어갈 때 필요한 질문을 미리 정리하는 초안이다.

현재 Phase 33은 방금 시작된 상태이므로,
이 문서는 최종 handoff가 아니라 방향을 잃지 않기 위한 준비 문서다.

## 현재 handoff 상태

- Phase 32는 robustness / stress validation pack과 Phase33 handoff를 완료했다.
- Phase 33은 paper tracking ledger를 만들어 Phase 34가 읽을 관찰 기록을 쌓을 예정이다.
- 아직 Phase 34 final selection decision pack은 만들지 않았다.

## 다음 phase에서 더 중요한 질문

1. paper tracking record가 충분히 쌓인 후보나 proposal을 최종 선정 / 보류 / 거절 중 어디로 보낼 것인가?
2. 최종 선정 decision pack은 백테스트, robustness, stress, paper tracking, operator note를 어떤 기준으로 결합할 것인가?
3. 최종 실전 후보로 읽히더라도 live approval / 주문 지시와 어떻게 분리할 것인가?

## 다음 phase에서 실제로 할 작업

쉽게 말하면:

- Phase 34는 paper tracking까지 마친 후보나 proposal을 최종 실전 후보로 선정할지, 더 볼지, 거절할지 결정하는 decision pack을 만든다.

주요 작업:

1. Final selection decision schema 정의
   - 후보 / proposal / paper ledger record / robustness evidence / operator decision을 하나로 묶는다.
2. Final decision UI 추가
   - 선정, 보류, 거절, 재검토 route와 이유를 보여준다.
3. 실전 투자 가이드 경계 정리
   - 최종 후보와 live trading approval / 주문 지시의 차이를 명확히 남긴다.

## 추천 다음 방향

Phase 33이 끝나면 Phase 34 `Final Portfolio Selection Decision Pack`으로 넘어가는 것이 자연스럽다.

왜냐하면 최종 실전 포트폴리오 선정은 paper tracking 기록 없이 바로 가기 어렵고,
Phase 33의 ledger가 그 판단의 마지막 근거가 되기 때문이다.

## handoff 메모

- Phase 34는 Phase 33 paper ledger의 상태, tracking result, review trigger를 최소 입력으로 읽어야 한다.
- Phase 34에서도 broker order, 자동 매매, live approval은 별도 범위로 유지한다.
