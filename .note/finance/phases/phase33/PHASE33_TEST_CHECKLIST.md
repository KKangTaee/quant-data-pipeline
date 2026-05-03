# Phase 33 Test Checklist

## 목적

이 checklist는 Phase 33 `Paper Portfolio Tracking Ledger` 구현이 끝난 뒤 사용자가 직접 확인할 manual QA 문서다.

현재 Phase 33은 `active / not_ready_for_qa` 상태이므로,
이 checklist는 최종 QA handoff 전 초안이다.

## 사용 방법

- Phase 33 구현이 `implementation_complete`가 되면 아래 항목을 최종 QA용으로 다시 정리한다.
- 사용자는 그때 `[ ]`를 `[x]`로 바꾸며 확인한다.
- 현재는 QA를 시작하지 않는다.

## 1. Paper Ledger Draft / Save 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal`
  - Validation Pack 또는 저장 proposal detail
- 체크 항목:
  - [ ] Phase 32 handoff를 바탕으로 paper ledger draft가 보이는지
  - [ ] tracking start date, target weights, benchmark, review cadence, trigger가 보이는지
  - [ ] `Save Paper Tracking Ledger`를 명시적으로 눌러야 저장되는지
  - [ ] preview만 열어서는 paper ledger가 자동 저장되지 않는지

## 2. 저장된 Paper Ledger 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal`
  - 저장된 paper ledger review section
- 체크 항목:
  - [ ] 저장된 paper ledger 목록이 보이는지
  - [ ] source candidate / proposal과 paper ledger record가 연결되어 보이는지
  - [ ] active / watch / paused / re-review 상태가 읽히는지
  - [ ] current candidate / Pre-Live / Portfolio Proposal registry를 덮어쓰지 않는지

## 3. Phase 34 Handoff 확인

- 확인 위치:
  - 저장된 paper ledger detail
- 체크 항목:
  - [ ] Phase 34 final selection으로 넘길 준비 상태가 보이는지
  - [ ] 아직 live approval이나 주문 지시가 아니라는 경계가 보이는지
  - [ ] paper tracking이 부족하면 추가 관찰 / 보강이 필요하다고 읽히는지

## 4. 문서와 closeout 확인

- 확인 문서:
  - `.note/finance/phases/phase33/PHASE33_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/phases/phase33/PHASE33_COMPLETION_SUMMARY.md`
  - `.note/finance/phases/phase33/PHASE33_NEXT_PHASE_PREPARATION.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
- 체크 항목:
  - [ ] Phase 33 상태가 구현 상태와 맞는지
  - [ ] Phase 34에서 무엇을 만들지 next phase preparation에 쉽게 설명되어 있는지

## 한 줄 판단 기준

이번 Phase33 QA는
**후보나 proposal을 실제 돈 없이 추적할 paper ledger로 저장하고 다시 읽을 수 있으며, 아직 최종 승인 / 주문이 아니라는 경계가 분명하면 통과**다.
