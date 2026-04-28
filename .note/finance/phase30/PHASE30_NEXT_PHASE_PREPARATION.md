# Phase 30 Next Phase Preparation

## 목적

이 문서는 Phase 30 이후 어떤 질문으로 다음 phase를 여는 것이 자연스러운지 정리하는 handoff 초안이다.

현재 Phase 30은 막 열렸고, 첫 작업 단위는 사용 흐름 재정렬과 리팩토링 경계 검토다.
따라서 이 문서는 아직 closeout handoff가 아니다.

## 현재 handoff 상태

- Phase 29는 complete / manual_qa_completed 상태로 닫혔다.
- Phase 30은 active / not_ready_for_qa 상태로 열렸다.
- 첫 작업은 `테스트에서 상용화 후보 검토까지 사용하는 흐름` 재정렬과 `backtest.py` 리팩토링 경계 검토였다.
- 두 번째 작업으로 Portfolio Proposal row 계약을 정의했다.
- 세 번째 작업으로 registry JSONL I/O helper를 runtime module로 분리했다.
- 네 번째 작업으로 `Backtest > Portfolio Proposal` draft 작성 / 저장 / registry inspect 흐름을 추가했다.
- 다섯 번째 작업으로 `Backtest > Portfolio Proposal > Monitoring Review` surface를 추가했다.

## 다음 phase에서 더 중요한 질문

1. Phase 30에서 Portfolio Proposal / Pre-Live Monitoring까지 구현한 뒤, 실제 Live Readiness / Final Approval을 어떤 기준으로 열 것인가
2. 실제 돈 투입 전 승인 / 보류 / 거절 기록은 어떤 저장소와 UI에서 관리할 것인가
3. paper tracking 기간과 결과를 어떤 기준으로 portfolio proposal에 다시 반영할 것인가

## 다음 phase에서 실제로 할 작업

쉽게 말하면:

- Phase 30 이후 phase는 실제 돈을 넣어도 되는지 판단하기 위한 최종 운영 검토 절차를 다룰 가능성이 높다.

주요 작업 후보:

1. Live Readiness decision record
   - 포트폴리오 제안 또는 후보가 live readiness 검토를 통과 / 보류 / 거절했는지 기록한다.
2. Final approval checklist
   - paper tracking, data trust, real-money blockers, portfolio risk, operator reason을 한 번에 확인한다.
3. Post-approval monitoring boundary
   - 승인 이후에도 어떤 기준으로 중단 / 축소 / 재검토할지 정한다.

## 추천 다음 방향

아직은 Phase 30 첫 작업 단계이므로 다음 phase를 확정하지 않는다.
Phase 30에서 portfolio proposal과 monitoring surface가 실제로 구현된 뒤,
Live Readiness / Final Approval phase를 별도로 열지 판단한다.

## handoff 메모

- Phase 30은 live approval이 아니다.
- Phase 30의 첫 작업은 product-flow와 refactor boundary 정리였다.
- Phase 30의 두 번째 작업은 Portfolio Proposal 계약 정의였다.
- Phase 30의 세 번째 작업은 current candidate / review note / pre-live registry helper 분리였다.
- Phase 30의 네 번째 작업은 Portfolio Proposal Draft UI / persistence 구현이었다.
- Phase 30의 다섯 번째 작업은 Portfolio Proposal Monitoring Review 구현이었다.
- 다음 구현 전에 `PHASE30_CURRENT_CHAPTER_TODO.md`, Portfolio Proposal 계약 문서, fourth/fifth work-unit 문서, Portfolio Proposal registry guide를 먼저 확인한다.
