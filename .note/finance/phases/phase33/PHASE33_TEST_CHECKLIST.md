# Phase 33 Test Checklist

## 목적

이 checklist는 Phase 33 `Paper Portfolio Tracking Ledger` 구현이 끝난 뒤 사용자가 직접 확인할 manual QA 문서다.

현재 Phase 33은 `complete / manual_qa_completed` 상태다.
아래 항목은 사용자 manual QA에서 확인 완료되었다.

## 사용 방법

- 사용자는 `[x]`로 표시된 항목을 기준으로 QA 완료 상태를 확인했다.
- 저장 테스트를 하면 `.note/finance/registries/PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl`이 생성되거나 row가 추가된다.
- 테스트용 row가 불필요하면 QA 후 해당 파일 또는 테스트 row를 정리해도 된다.

## 1. Paper Ledger Draft / Save 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal`
  - 단일 후보 direct path의 Validation Pack 또는 저장 proposal detail
- 체크 항목:
  - [x] Validation Pack 아래 `Paper Tracking Ledger Draft`가 보이는지
  - [x] tracking start date, target weights, benchmark, review cadence, trigger, operator note가 보이는지
  - [x] `Save Paper Tracking Ledger`를 명시적으로 눌러야 저장되는지
  - [x] preview만 열어서는 paper ledger가 자동 저장되지 않는지
  - [x] 작성 중 proposal에서는 preview는 가능하지만 proposal draft 저장 전 paper ledger save가 차단되는지

## 2. 저장된 Paper Ledger 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal`
  - `저장된 Paper Tracking Ledger 확인`
- 체크 항목:
  - [x] 저장된 paper ledger 목록이 보이는지
  - [x] source candidate / proposal과 paper ledger record가 연결되어 보이는지
  - [x] active tracking / watch / paused / re-review / closed 상태가 읽히는지
  - [x] target component와 target weight가 저장 당시 조건과 맞게 보이는지
  - [x] benchmark, review cadence, review trigger, raw JSON을 확인할 수 있는지
  - [x] current candidate / Pre-Live / Portfolio Proposal registry를 덮어쓰지 않는지

## 3. Phase 34 Handoff 확인

- 확인 위치:
  - 저장된 paper ledger detail
- 체크 항목:
  - [x] Phase34 handoff route가 보이는지
  - [x] `READY_FOR_FINAL_SELECTION_REVIEW`는 Phase 34 최종 선정 검토 후보 가능으로 읽히는지
  - [x] `NEEDS_PAPER_TRACKING_REVIEW`는 paper tracking 조건 / 기록 보강 필요로 읽히는지
  - [x] `BLOCKED_FOR_FINAL_SELECTION_REVIEW`는 hard blocker 해결 전 차단으로 읽히는지
  - [x] 아직 live approval이나 주문 지시가 아니라는 경계가 보이는지
  - [x] `Open Final Selection`이 Phase 34 예정 기능으로 비활성 상태인지

## 4. 문서와 closeout 확인

- 확인 문서:
  - `.note/finance/phases/phase33/PHASE33_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/phases/phase33/PHASE33_COMPLETION_SUMMARY.md`
  - `.note/finance/phases/phase33/PHASE33_NEXT_PHASE_PREPARATION.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
- 체크 항목:
  - [x] Phase 33 상태가 `complete / manual_qa_completed`로 읽히는지
  - [x] Phase 34에서 무엇을 만들지 next phase preparation에 쉽게 설명되어 있는지
  - [x] `PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl`이 current candidate / Pre-Live / Portfolio Proposal registry와 별도 저장소로 설명되어 있는지

## 한 줄 판단 기준

이번 Phase33 QA는
**후보나 proposal을 실제 돈 없이 추적할 paper ledger로 저장하고 다시 읽을 수 있으며, 아직 최종 승인 / 주문이 아니라는 경계가 분명하면 통과**다.
