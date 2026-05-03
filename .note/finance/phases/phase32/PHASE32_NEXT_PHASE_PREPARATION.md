# Phase 32 Next Phase Preparation

## 목적

이 문서는 Phase 32 이후 Phase 33 `Paper Portfolio Tracking Ledger`로 넘어갈 때 필요한 handoff를 정리한다.

Phase 32는 `implementation_complete / manual_qa_pending` 상태이며,
사용자 QA가 완료되면 Phase 33을 여는 것이 자연스럽다.

## 현재 handoff 상태

- Phase 31은 포트폴리오 구조 / blocker / paper tracking gap / overlap first pass를 읽는 Validation Pack을 완료했다.
- Phase 32는 그 결과를 받아 robustness / stress 검증 입력, stress summary contract, Phase 33 handoff를 보여준다.
- 아직 paper ledger row 저장, paper PnL 시계열 계산, 최종 portfolio selection decision은 만들지 않았다.

## 다음 phase에서 더 중요한 질문

1. robustness / stress 입력이 준비된 후보나 proposal을 실제 돈 없이 어떤 시작일 / 비중 / 추적 조건으로 paper tracking할 것인가?
2. paper tracking 중에는 어떤 성과 악화, 변동성, MDD, benchmark 괴리를 재검토 신호로 볼 것인가?
3. paper ledger가 Phase 34 final selection decision pack으로 넘길 최소 기록은 무엇인가?

## 다음 phase에서 실제로 할 작업

쉽게 말하면:

- Phase 33은 "좋아 보이는 후보를 실제 돈 없이 관찰하는 장부"를 만든다.
- snapshot 비교만 보는 것이 아니라, 시작일과 비중, 추적 조건, 재검토 기준을 가진 paper portfolio record를 남긴다.

주요 작업:

1. Paper tracking ledger row 정의
   - 후보 / proposal id, 시작일, target weight, tracking benchmark, observation rule, review cadence를 저장한다.
2. Paper tracking 저장소와 UI surface 추가
   - active / watch / paused / re-review 같은 상태와 최신 성과 악화 신호를 읽는다.
3. Phase 34 final selection 입력 정리
   - paper tracking 결과가 충분한지, 최종 선정 / 보류 / 거절 중 어디로 갈지 판단할 요약을 만든다.

## 추천 다음 방향

Phase 32 QA가 완료되면 Phase 33 `Paper Portfolio Tracking Ledger`로 넘어간다.

왜냐하면 최종 실전 포트폴리오 선정 전에는 백테스트 결과뿐 아니라,
실제 운용을 가정한 관찰 기간과 추적 조건이 필요하기 때문이다.

## Phase 33 시작 전 확인할 것

- Phase32 checklist가 완료되었는지
- `READY_FOR_PAPER_LEDGER_PREP`와 `NEEDS_STRESS_INPUT_REVIEW`의 차이가 UI에서 이해되는지
- Phase33은 live approval이 아니라 paper tracking ledger 저장 단계라는 경계가 유지되는지

## handoff 메모

- Phase 33은 새 append-only paper ledger 저장소가 필요할 가능성이 높다.
- Portfolio Proposal registry를 덮어쓰지 말고, paper tracking 운영 기록은 별도 저장소로 분리하는 방향이 자연스럽다.
- Phase 32의 `phase33_handoff.requirements`는 Phase 33 row 설계의 최소 입력으로 사용할 수 있다.
