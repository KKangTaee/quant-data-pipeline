# Phase 26 Current Chapter TODO

## 진행 상태

- `implementation_complete`

## 검증 상태

- `manual_qa_pending`

## 현재 목표

Phase 26의 목표는 새 전략이나 새 투자 분석을 바로 시작하는 것이 아니다.
Phase 25까지 만들어진 제품 surface를 기준으로,
과거 phase backlog와 현재 foundation gap을 다시 정리해
Phase 27~30 개발 순서를 안정적으로 고정하는 것이다.

## 1. Phase 상태와 backlog 재분류

- `completed` Phase 26 kickoff bundle 작성
  - Phase 26 plan / TODO / checklist / completion summary / next-phase preparation 문서를 실제 내용으로 채운다.
- `completed` 과거 phase pending 상태 inventory
  - Phase 8, 9, 12~15, 18의 pending / practical closeout 항목을 현재 기준으로 다시 분류한다.
- `completed` remaining structural backlog 판단
  - Phase 18 remaining backlog가 immediate blocker인지, Phase 28 후보인지, future option인지 정리한다.

## 2. Foundation Gap Map

- `completed` 데이터 / 백테스트 신뢰성 gap 정리
  - stale price, missing ticker, common-date truncation, excluded ticker, malformed price row 같은 이슈를 Phase 27 입력으로 묶는다.
- `completed` strategy family parity gap 정리
  - annual, quarterly, Global Relative Strength, saved replay / history / compare / Real-Money / Guardrail 차이를 확인한다.
- `completed` candidate review / portfolio proposal gap 정리
  - current candidate, pre-live record, portfolio proposal workflow 사이의 연결 빈틈을 확인한다.

## 3. Phase 27~30 Roadmap Handoff

- `completed` Phase 27 Data Integrity And Backtest Trust Layer 방향 고정
- `completed` Phase 28 Strategy Family Parity And Cadence Completion 방향 고정
- `completed` Phase 29 Candidate Review And Recommendation Workflow 방향 고정
- `completed` Phase 30 Portfolio Proposal And Pre-Live Monitoring Surface 방향 고정
- `completed` Live Readiness / Final Approval은 Phase 30 이후로 명시

## 4. Validation

- `completed` roadmap / index consistency check
- `completed` phase26 checklist handoff
- `completed` hygiene helper

## 5. Documentation Sync

- `completed` phase kickoff bundle 생성
- `completed` roadmap / doc index / work log / question log sync
- `completed` glossary sync
- `completed` completion / next-phase 문서 갱신

## 현재 판단

Phase 26 implementation은 완료되었고, 사용자 checklist QA가 남아 있다.
과거 phase의 오래된 pending 상태는 현재 Phase 27 진입을 막는 blocker가 아니라
이후 phase 입력 또는 future option으로 재분류되었다.
Phase 27 구현은 사용자가 `PHASE26_TEST_CHECKLIST.md`를 확인한 뒤 시작한다.
