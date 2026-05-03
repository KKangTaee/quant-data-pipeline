# Phase 34 Test Checklist

## 목적

이 checklist는 Phase 34 `Final Portfolio Selection Decision Pack` 구현이 끝난 뒤 사용자가 직접 확인할 manual QA 문서다.

현재 Phase 34는 `implementation_complete / manual_qa_pending` 상태다.
아래 항목을 확인한 뒤 `[ ]`를 `[x]`로 바꾸면 된다.

## 사용 방법

- `Backtest > Portfolio Proposal`에서 저장된 Paper Tracking Ledger가 최소 1개 있어야 Phase34 decision pack을 확인할 수 있다.
- 저장된 ledger가 없다면 Phase33 경로에서 `Save Paper Tracking Ledger`를 먼저 저장한다.
- QA 중 저장되는 final decision은 `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`에 append-only로 남는다.

## 1. Final Decision Evidence Pack 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal`
  - 저장된 Paper Tracking Ledger detail 또는 Phase34 final decision 영역
- 체크 항목:
  - [ ] 저장된 paper ledger row를 선택하면 `Final Selection Decision Pack`이 보이는지
  - [ ] source paper ledger, source candidate / proposal, target weights, benchmark, review cadence가 보이는지
  - [ ] Decision Evidence Route가 `READY_FOR_FINAL_DECISION`, `FINAL_DECISION_NEEDS_REVIEW`, `FINAL_DECISION_BLOCKED` 중 하나로 읽히는지
  - [ ] Evidence checks에서 Phase31 validation, Phase32 robustness / stress, Phase33 paper tracking 근거가 한 묶음으로 읽히는지
  - [ ] missing evidence와 blocker가 다음 행동으로 설명되는지

## 2. Final Decision Route 확인

- 확인 위치:
  - Final decision draft / preview 영역
- 체크 항목:
  - [ ] `SELECT_FOR_PRACTICAL_PORTFOLIO`는 최종 실전 후보 선정으로 읽히는지
  - [ ] `HOLD_FOR_MORE_PAPER_TRACKING`은 추가 관찰 필요로 읽히는지
  - [ ] `REJECT_FOR_PRACTICAL_USE`는 현 조건에서 실전 후보 제외로 읽히는지
  - [ ] `RE_REVIEW_REQUIRED`는 blocker / 데이터 gap / operator constraint 재검토로 읽히는지
  - [ ] 어떤 route도 live approval이나 주문 지시로 보이지 않는지
  - [ ] `SELECT_FOR_PRACTICAL_PORTFOLIO` 선택 시 evidence blocker가 있으면 저장 전 차단되는지
  - [ ] 보류 / 거절 / 재검토 route는 사용자 사유를 남길 때 판단 기록으로 저장 가능한지

## 3. 저장된 Final Decision 확인

- 확인 위치:
  - 저장된 final decision review section
- 체크 항목:
  - [ ] final decision row가 명시 저장 버튼으로만 append되는지
  - [ ] 저장된 decision record에서 source paper ledger와 selected components가 연결되어 보이는지
  - [ ] current candidate / Pre-Live / Portfolio Proposal / Paper Ledger registry를 덮어쓰지 않는지
  - [ ] Phase35 handoff가 선정 이후 운영 기준 준비 상태로 읽히는지
  - [ ] 저장 성공 후 `저장된 Final Selection Decision 확인` 영역에서 방금 저장한 row가 보이는지
  - [ ] `Live Approval`, `Order`가 Disabled로 읽히는지

## 4. 문서와 closeout 확인

- 확인 문서:
  - `.note/finance/phases/phase34/PHASE34_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/phases/phase34/PHASE34_COMPLETION_SUMMARY.md`
  - `.note/finance/phases/phase34/PHASE34_NEXT_PHASE_PREPARATION.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
  - `.note/finance/operations/FINAL_PORTFOLIO_SELECTION_DECISIONS_GUIDE.md`
- 체크 항목:
  - [ ] Phase 34 상태가 구현 상태와 맞는지
  - [ ] Phase 35에서 무엇을 만들지 next phase preparation에 쉽게 설명되어 있는지
  - [ ] final decision이 live approval / order instruction과 별도 개념으로 설명되어 있는지

## 한 줄 판단 기준

이번 Phase34 QA는
**paper tracking까지 본 후보나 proposal을 선정 / 보류 / 거절 / 재검토로 명시 판단할 수 있고, 아직 주문이나 live approval이 아니라는 경계가 분명하면 통과**다.
