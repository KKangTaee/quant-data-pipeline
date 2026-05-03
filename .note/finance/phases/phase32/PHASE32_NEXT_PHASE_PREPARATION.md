# Phase 32 Next Phase Preparation

## 목적

이 문서는 Phase 32 이후 Phase 33 `Paper Portfolio Tracking Ledger`로 넘어갈 때 필요한 handoff 질문을 미리 정리하는 초안이다.

현재 Phase 32는 아직 진행 중이므로,
이 문서는 최종 handoff 문서가 아니라 다음 phase 준비 방향을 잃지 않기 위한 중간 메모다.

## 현재 handoff 상태

- Phase 31은 포트폴리오 구조 / blocker / paper tracking gap / overlap first pass를 읽는 Validation Pack을 완료했다.
- Phase 32 첫 작업은 그 결과를 받아 robustness / stress 검증 입력이 충분한지 preview로 보여준다.
- 아직 실제 stress sweep 결과나 paper portfolio ledger는 만들지 않았다.

## 다음 phase에서 더 중요한 질문

1. robustness 검증을 통과한 후보나 proposal을 실제 돈 없이 어떤 시작일 / 비중 / 추적 조건으로 paper tracking할 것인가?
2. paper tracking 중에는 어떤 성과 악화, 변동성, MDD, benchmark 괴리를 재검토 신호로 볼 것인가?

## 다음 phase에서 실제로 할 작업

쉽게 말하면:

- Phase 33은 "좋아 보이는 후보를 실제 돈 없이 관찰하는 장부"를 만든다.
- snapshot 비교만 보는 것이 아니라, 시작일과 비중, 추적 조건, 재검토 기준을 가진 paper portfolio record를 남긴다.

주요 작업:

1. Paper tracking ledger row 정의
   - 후보 / proposal id, 시작일, target weight, tracking benchmark, observation rule, review cadence를 저장한다.
2. Paper tracking 상태 surface 추가
   - active / watch / paused / re-review 같은 상태와 최신 성과 악화 신호를 읽는다.
3. Phase 34 final selection 입력 정리
   - paper tracking 결과가 충분한지, 최종 선정 / 보류 / 거절 중 어디로 갈지 판단할 요약을 만든다.

## 추천 다음 방향

Phase 32가 robustness / stress 입력과 결과 해석을 충분히 제공하면,
다음은 Phase 33 `Paper Portfolio Tracking Ledger`가 자연스럽다.

왜냐하면 최종 실전 포트폴리오 선정 전에는 백테스트 결과뿐 아니라,
실제 운용을 가정한 관찰 기간과 추적 조건이 필요하기 때문이다.

## handoff 메모

- Phase 32가 끝나기 전까지는 이 문서를 확정하지 않는다.
- Phase 33을 열 때는 Phase 32에서 확정한 robustness route, stress summary schema, paper tracking requirement를 먼저 읽는다.
