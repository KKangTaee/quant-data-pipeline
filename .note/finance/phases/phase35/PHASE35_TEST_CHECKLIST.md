# Phase 35 Test Checklist

## 목적

이 checklist는 Phase35의 workflow 단순화가 제대로 반영됐는지 확인하는 manual QA 문서다.

현재 Phase35는 `implementation_complete / manual_qa_pending` 상태다.

## 사용 방법

- `Backtest` workflow가 `Portfolio Proposal -> Final Review -> 최종 판단 완료`로 끝나는지 확인한다.
- 별도 후속 가이드 탭이나 추가 저장 UX가 보이지 않는지 확인한다.
- Final Review의 saved final decision review에서 최종 판단 상태가 충분히 읽히는지 확인한다.
- 이 흐름은 live approval, broker order, 자동매매, 수익 보장이 아니다.

## 1. Workflow Navigation 확인

- 확인 위치:
  - `Backtest`
- 체크 항목:
  - [ ] workflow navigation이 `Single Strategy`, `Compare & Portfolio Builder`, `Candidate Review`, `Portfolio Proposal`, `Final Review` 순서로 보이는지
  - [ ] 별도 `Post-Selection Guide` panel이 보이지 않는지
  - [ ] `Final Review`가 마지막 active workflow panel로 읽히는지
  - [ ] History와 Candidate Library는 기존처럼 Operations 보조 도구로 안내되는지

## 2. Final Review 최종 판단 저장 확인

- 확인 위치:
  - `Backtest > Final Review`
- 체크 항목:
  - [ ] 단일 후보 또는 saved proposal을 선택할 수 있는지
  - [ ] Validation / Robustness / Paper Observation 기준이 보이는지
  - [ ] 최종 판단 option에 선정 / 보류 / 거절 / 재검토가 보이는지
  - [ ] `최종 검토 결과 기록` 저장 action이 동작하는지
  - [ ] 저장 후 `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`에 row가 append되는지

## 3. 저장된 최종 판단 Review 확인

- 확인 위치:
  - `Backtest > Final Review`
  - `기록된 최종 검토 결과 확인`
- 체크 항목:
  - [ ] saved final decision table에 `투자 가능성` column이 보이는지
  - [ ] `SELECT_FOR_PRACTICAL_PORTFOLIO`는 `투자 가능 후보`로 읽히는지
  - [ ] `HOLD_FOR_MORE_PAPER_TRACKING`은 `내용 부족 / 관찰 필요`로 읽히는지
  - [ ] `REJECT_FOR_PRACTICAL_USE`는 `투자하면 안 됨`으로 읽히는지
  - [ ] `RE_REVIEW_REQUIRED`는 `재검토 필요`로 읽히는지
  - [ ] detail panel title이 `Final Review Status`로 읽히는지
  - [ ] selected component table이 계속 보이는지

## 4. 실행 경계 확인

- 확인 위치:
  - `Backtest > Final Review`
- 체크 항목:
  - [ ] `Post-Selection Guide 열기` 버튼이 보이지 않는지
  - [ ] `Live Approval / Order`가 disabled 상태로 보이는지
  - [ ] saved final decision JSON에서 `live_approval = false`인지
  - [ ] saved final decision JSON에서 `order_instruction = false`인지
  - [ ] final decision 저장이 current candidate / Pre-Live / Portfolio Proposal registry를 덮어쓰지 않는지

## 5. 코드 / 파일 경계 확인

- 확인 위치:
  - repository file tree
- 체크 항목:
  - [ ] `app/web/backtest_post_selection_guide.py` 파일이 없는지
  - [ ] `app/web/backtest_post_selection_guide_helpers.py` 파일이 없는지
  - [ ] `app/web/pages/backtest.py`에서 후속 가이드 render import가 없는지
  - [ ] `app/web/backtest_common.py` panel option에 후속 가이드가 없는지
  - [ ] `.note/finance/operations/POST_SELECTION_FINAL_INVESTMENT_GUIDE.md`가 더 이상 active guide로 남아 있지 않은지

## 6. 문서 확인

- 확인 문서:
  - `.note/finance/phases/phase35/PHASE35_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/phases/phase35/PHASE35_COMPLETION_SUMMARY.md`
  - `.note/finance/phases/phase35/PHASE35_NEXT_PHASE_PREPARATION.md`
  - `.note/finance/code_analysis/WEB_BACKTEST_UI_FLOW.md`
  - `.note/finance/operations/FINAL_PORTFOLIO_SELECTION_DECISIONS_GUIDE.md`
- 체크 항목:
  - [ ] Phase35가 별도 후속 가이드 구현이 아니라 workflow 단순화 phase로 설명되는지
  - [ ] 현재 흐름이 `Portfolio Proposal -> Final Review -> 최종 판단 완료`로 설명되는지
  - [ ] Final Review가 최종 판단 원본이라고 설명되는지
  - [ ] live approval / broker order / 자동매매가 아니라고 설명되는지

## 완료 판단

위 항목이 통과하면,
**사용자는 Portfolio Proposal 이후 Final Review에서 최종 실전 후보 여부를 판단하고 기본 후보 선정 workflow를 마무리할 수 있는 상태**로 본다.

다만 이것은 broker order, 자동매매, live approval, 수익 보장이 아니다.
