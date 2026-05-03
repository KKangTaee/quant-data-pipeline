# Phase 34 Test Checklist

## 목적

이 checklist는 Phase 34 `Final Review / Final Portfolio Selection Decision Pack` 구현이 끝난 뒤 사용자가 직접 확인할 manual QA 문서다.

현재 Phase 34는 `implementation_complete / manual_qa_pending` 상태다.
아래 항목을 확인한 뒤 `[ ]`를 `[x]`로 바꾸면 된다.

## 사용 방법

- `Backtest > Portfolio Proposal`은 후보를 묶어 proposal draft를 저장하거나 단일 후보 직행 가능성을 확인하는 탭이다.
- `Backtest > Final Review`는 단일 후보 또는 저장된 proposal을 골라 validation, robustness / stress 질문, paper observation 기준, 최종 판단을 한 번에 기록하는 탭이다.
- `Save Paper Tracking Ledger`는 이번 사용자-facing 흐름의 필수 단계가 아니다. 관찰 기준은 Final Review의 최종 검토 기록 안에 함께 저장된다.
- QA 중 저장되는 final review record는 `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`에 append-only로 남는다.

## 1. Portfolio Proposal 경계 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal`
- 체크 항목:
  - [ ] 단일 후보를 1개 선택하면 기본값이 `단일 후보 직행 평가`로 열리는지
  - [ ] 단일 후보 직행 경로에서 proposal draft 저장 버튼이 보이지 않고 `Open Final Review`가 보이는지
  - [ ] 2개 이상 후보를 선택하면 `포트폴리오 초안 작성` 경로로 열리는지
  - [ ] 다중 후보 경로에서 `Save Portfolio Proposal Draft`와 `Open Final Review`가 보이는지
  - [ ] `Save Paper Tracking Ledger`와 `Save Final Selection Decision`이 Portfolio Proposal 탭의 주 흐름에 노출되지 않는지
  - [ ] 저장된 proposal 확인 영역이 Monitoring / Pre-Live Feedback / Paper Feedback / Raw JSON 중심으로 읽히는지

## 2. Final Review 대상 선택 확인

- 확인 위치:
  - `Backtest > Final Review`
- 체크 항목:
  - [ ] 상단 card에서 `Paper Ledger Save = Not Required`가 보이는지
  - [ ] 상단 card에서 `Live Approval = Disabled`가 보이는지
  - [ ] `최종 검토 대상 선택`에서 current candidate와 saved proposal을 선택할 수 있는지
  - [ ] 선택한 source의 `Source Type`과 `Source ID`가 보이는지
  - [ ] source를 바꿔도 자동 저장이나 live approval이 수행되지 않는지

## 3. 검증 / 관찰 기준 확인

- 확인 위치:
  - `Backtest > Final Review`
  - `2. 검증 근거 확인`
  - `3. Robustness / Stress 질문 확인`
  - `4. Paper Observation 기준 확인`
- 체크 항목:
  - [ ] validation route, score, hard blockers, weight total, component table이 보이는지
  - [ ] robustness / stress summary가 실제 stress runner 실행 결과가 아니라 최종 검토 전 확인 질문으로 읽히는지
  - [ ] paper observation이 `Inline Observation`으로 표시되는지
  - [ ] 별도 ledger 저장 없이 review cadence, benchmark, 재검토 trigger가 최종 검토 기록에 포함될 기준으로 보이는지
  - [ ] target weight 합계가 100%가 아니거나 active component가 없으면 blocker가 사용자가 고칠 항목으로 읽히는지

## 4. 최종 검토 결과 기록 확인

- 확인 위치:
  - `Backtest > Final Review`
  - `5. 최종 판단 및 테스트 검증`
  - `6. 기록된 최종 검토 결과 확인`
- 체크 항목:
  - [ ] 최종 판단 route가 `SELECT_FOR_PRACTICAL_PORTFOLIO`, `HOLD_FOR_MORE_PAPER_TRACKING`, `REJECT_FOR_PRACTICAL_USE`, `RE_REVIEW_REQUIRED` 중 하나로 선택되는지
  - [ ] 화면의 주 저장 버튼이 `최종 검토 결과 기록` 하나로 읽히는지
  - [ ] `SELECT_FOR_PRACTICAL_PORTFOLIO`는 evidence blocker가 있으면 기록 전 차단되는지
  - [ ] 보류 / 거절 / 재검토 route는 사용자 판단 사유를 남기면 기록 가능한지
  - [ ] 저장 후 `기록된 최종 검토 결과 확인` 영역에서 방금 저장한 row가 보이는지
  - [ ] 저장된 record의 `Observation`이 `paper_observation_*` 형태로 보이고, 별도 `source_paper_ledger_id`가 필수처럼 보이지 않는지
  - [ ] 저장된 record에서 source, selected components, evidence route, Phase35 handoff가 연결되어 보이는지
  - [ ] `Live Approval`, `Order`가 Disabled로 읽히는지

## 5. 문서와 closeout 확인

- 확인 문서:
  - `.note/finance/phases/phase34/PHASE34_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/phases/phase34/PHASE34_COMPLETION_SUMMARY.md`
  - `.note/finance/phases/phase34/PHASE34_NEXT_PHASE_PREPARATION.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
  - `.note/finance/operations/FINAL_PORTFOLIO_SELECTION_DECISIONS_GUIDE.md`
- 체크 항목:
  - [ ] Phase 34 상태가 구현 상태와 맞는지
  - [ ] Phase 34가 Portfolio Proposal 탭 안에 저장 버튼을 계속 늘리는 흐름이 아니라 Final Review 탭으로 분리됐다고 설명되는지
  - [ ] Phase 35에서 무엇을 만들지 next phase preparation에 쉽게 설명되어 있는지
  - [ ] final review record가 live approval / order instruction과 별도 개념으로 설명되어 있는지

## 한 줄 판단 기준

이번 Phase34 QA는
**Portfolio Proposal은 초안 작성에 머물고, Final Review에서 검증 근거 / paper observation 기준 / 최종 판단을 하나의 기록으로 남기며, 아직 주문이나 live approval이 아니라는 경계가 분명하면 통과**다.
