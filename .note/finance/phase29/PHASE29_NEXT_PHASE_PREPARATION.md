# Phase 29 Next Phase Preparation

## 목적

이 문서는 Phase 29 이후 Phase 30으로 넘어갈 때 어떤 질문을 다뤄야 하는지 미리 정리하는 handoff 문서다.

현재는 Phase 29가 아직 active 상태이므로, 이 문서는 임시 준비 문서다.
Phase 29 closeout 시점에 다시 갱신한다.

## 현재 handoff 상태

- Phase 29는 active / manual_qa_pending 상태다.
- 첫 작업 단위로 `Backtest > Candidate Review` panel을 추가했다.
- 현재는 이미 registry에 있는 후보를 읽고 compare / Pre-Live Review로 넘기는 길을 만든 상태다.
- 아직 새 백테스트 결과를 candidate review 초안으로 등록하는 흐름은 남아 있다.

## Phase 30으로 넘어가기 전에 더 중요한 질문

1. 후보 1개를 보는 것이 아니라 후보 묶음을 포트폴리오 제안으로 어떻게 만들 것인가
2. Pre-Live 기록과 portfolio proposal이 서로 어떻게 연결되어야 하는가
3. 포트폴리오 제안이 투자 승인처럼 보이지 않게 하려면 어떤 경계 문구와 상태값이 필요한가

## 다음 phase에서 실제로 할 작업

쉽게 말하면:

- Phase 30은 후보 검토 결과를 포트폴리오 제안과 paper / pre-live monitoring surface로 연결하는 phase다.

주요 작업 후보:

1. Portfolio Proposal 후보 묶음 정의
   - 여러 candidate를 어떤 비중 / 목적 / 위험 역할로 묶을지 기록한다.
2. Proposal review surface
   - 포트폴리오 제안이 어떤 후보들로 구성되었고 어떤 데이터 / Real-Money / Pre-Live 상태를 갖는지 보여준다.
3. Pre-Live monitoring 연결
   - 후보 단위 Pre-Live 기록과 포트폴리오 단위 monitoring이 어떻게 이어질지 정한다.

## 추천 다음 방향

Phase 29가 후보 검토 workflow를 정리하면,
Phase 30은 그 후보들을 묶어 포트폴리오 제안으로 관리하는 흐름이 자연스럽다.

## handoff 메모

- Phase 30은 live approval이 아니다.
- Phase 30은 portfolio proposal과 monitoring surface를 만드는 phase다.
- Live Readiness / Final Approval은 Phase 30 이후 별도 phase 후보로 둔다.
