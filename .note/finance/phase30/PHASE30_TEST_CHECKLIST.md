# Phase 30 Test Checklist

## 목적

이 checklist는 Phase 30에서 만드는 product-flow 재정렬,
리팩토링 경계 검토, 이후 Portfolio Proposal / Pre-Live Monitoring surface가
사용자가 이해할 수 있는 흐름으로 연결되는지 확인하기 위한 문서다.

현재는 Phase 30 구현 완료 후 manual QA checklist다.
이 checklist 확인이 끝나면 Phase 30 closeout 여부를 판단한다.

## 사용 방법

- 아래 항목은 사용자가 직접 `[ ]`를 `[x]`로 바꾸며 확인한다.
- 특별한 사유가 없으면, 주요 체크 항목이 완료된 뒤 다음 작업 단위로 넘어간다.
- checklist에는 별도 `용어 기준` 섹션을 만들지 않는다.
- 용어 설명이 필요하면 각 체크 항목 안에 `어디서 무엇을 어떻게 확인하는지`를 직접 적는다.

## 1. Guide 흐름 확인

- 확인 위치:
  - `Guides > 테스트에서 상용화 후보 검토까지 사용하는 흐름`
  - `Guides > GTAA Risk-Off 후보군 보는 법`
- 체크 항목:
  - [ ] 1~5단계가 데이터 최신화, Single Strategy, Real-Money, Hold 해결, Compare로 이어지는 테스트 / 검증 구간으로 읽히는지
  - [ ] 6~10단계가 Phase 29 기능 나열이 아니라 후보 초안, 판단 기록, 후보 저장, 운영 관찰로 이어지는 후보 검토 / 운영 기록 구간으로 읽히는지
  - [ ] GTAA `Risk-Off Contract`에서 `Defensive Tickers`와 GTAA universe의 교집합만 실제 fallback 후보로 쓰인다는 점이 이해되는지
  - [ ] `Candidate Draft`가 좋은 백테스트 결과를 바로 후보 registry에 넣는 것이 아니라 저장 전 초안으로 설명되는지
  - [ ] `Candidate Review Note`가 사람의 판단과 다음 행동을 남기는 기록으로 설명되는지
  - [ ] `Current Candidate Registry`가 후보 저장소이지 투자 승인 저장소가 아니라고 읽히는지
  - [ ] `Pre-Live Review`가 live trading 승인 전 paper / watchlist / hold 운영 기록으로 설명되는지
  - [ ] `Portfolio Proposal`이 Phase 30에서 만든 후보 묶음 제안 초안이며 투자 승인과 구분되는지

## 2. 리팩토링 경계 확인

- 확인 위치:
  - `.note/finance/code_analysis/WEB_BACKTEST_UI_FLOW.md`
  - `.note/finance/phase30/PHASE30_PRODUCT_FLOW_REORIENTATION_AND_BACKTEST_REFACTOR_BOUNDARY_FIRST_WORK_UNIT.md`
- 체크 항목:
  - [ ] `backtest.py`가 왜 커졌는지 주요 책임 묶음이 이해되는지
  - [ ] Candidate Review / Pre-Live / registry helper가 먼저 분리 후보로 잡힌 이유가 이해되는지
  - [ ] Strategy forms를 가장 나중에 분리하자는 판단이 안전하게 느껴지는지
  - [ ] 실제 리팩토링이 아직 시작되지 않았고, 이번 작업은 경계 검토라는 점이 분명한지

## 3. Phase 30 문서 확인

- 확인 문서:
  - `.note/finance/phase30/PHASE30_PORTFOLIO_PROPOSAL_AND_PRE_LIVE_MONITORING_SURFACE_PLAN.md`
  - `.note/finance/phase30/PHASE30_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
- 체크 항목:
  - [ ] Phase 30이 implementation_complete / manual_qa_pending 상태이며, 사용 흐름 정렬 / proposal 계약 / registry helper 분리 / proposal draft UI / monitoring review / pre-live feedback / paper tracking feedback이 단계적으로 진행되었다고 읽히는지
  - [ ] 첫 작업이 사용 흐름 재정렬과 리팩토링 경계 검토로 설명되는지
  - [ ] 두 번째 작업이 Portfolio Proposal 계약 정의였고, 네 번째 작업에서 그 계약이 실제 UI / 저장소로 연결되었다고 읽히는지

## 4. Portfolio Proposal 계약 확인

- 확인 문서:
  - `.note/finance/phase30/PHASE30_PORTFOLIO_PROPOSAL_CONTRACT_SECOND_WORK_UNIT.md`
- 체크 항목:
  - [ ] Portfolio Proposal이 단순 saved portfolio나 weighted result가 아니라 후보 묶음 제안으로 설명되는지
  - [ ] proposal row에 목적, 후보 역할, 비중 근거, risk constraints, evidence snapshot, blocker, operator decision이 필요하다는 점이 이해되는지
  - [ ] `core_anchor`, `diversifier`, `defensive_sleeve`, `satellite`, `watch_only` 같은 후보 역할이 포트폴리오 안에서 왜 필요한지 이해되는지
  - [ ] `manual_weight` 또는 `equal_weight`로 먼저 시작하고 optimizer는 당장 제외한다는 판단이 안전하게 느껴지는지
  - [ ] `.note/finance/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`는 proposal draft가 저장될 append-only registry이며, 첫 저장 시 생성된다고 읽히는지
  - [ ] Proposal lifecycle이 draft / review_ready / paper_tracking / hold / rejected / superseded / live_readiness_candidate로 구분되고, live approval과 분리되는지

## 5. Registry I/O helper 리팩토링 확인

- 확인 위치:
  - `app/web/runtime/candidate_registry.py`
  - `app/web/pages/backtest.py`
  - `.note/finance/phase30/PHASE30_REGISTRY_IO_HELPER_REFACTOR_THIRD_WORK_UNIT.md`
- 체크 항목:
  - [ ] current candidate / candidate review note / pre-live registry의 JSONL read / append helper가 `app/web/runtime/candidate_registry.py`로 분리되었는지
  - [ ] Candidate Review UI, Pre-Live Review UI, Compare prefill, session state key는 바뀌지 않았다고 읽히는지
  - [ ] 이번 작업이 전체 `backtest.py` 리팩토링 완료가 아니라 첫 작은 helper split이라고 이해되는지
  - [ ] 이후 Candidate Review / Pre-Live / History / Saved Portfolio 추가 분리가 별도 작업으로 남아 있다고 읽히는지

## 6. Portfolio Proposal Draft UI 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal`
  - `.note/finance/operations/PORTFOLIO_PROPOSAL_REGISTRY_GUIDE.md`
  - `.note/finance/phase30/PHASE30_PORTFOLIO_PROPOSAL_DRAFT_UI_FOURTH_WORK_UNIT.md`
- 체크 항목:
  - [ ] Backtest panel 선택지에 `Portfolio Proposal`이 보이는지
  - [ ] 화면 상단에서 current candidates, pre-live records, saved proposals, live approval disabled 상태가 보이는지
  - [ ] `Create Proposal Draft` tab에서 current candidate 여러 개를 선택할 수 있는지
  - [ ] proposal objective 영역에서 Proposal ID, Status, Type, Capital Scope, Primary Goal, Secondary Goal, Review Cadence, Weighting Method가 보이는지
  - [ ] 선택한 후보별로 Proposal Role, Target Weight %, Weight Reason을 입력할 수 있는지
  - [ ] 후보별 CAGR, MDD, Promotion, Shortlist, Pre-Live 상태가 proposal 작성 맥락에서 함께 보이는지
  - [ ] target weight 합계가 100%가 아니면 저장 전 blocker가 표시되는지
  - [ ] `Portfolio Proposal JSON Preview`에서 저장될 row 구조를 확인할 수 있는지
  - [ ] `Save Portfolio Proposal Draft`가 live approval이나 주문 지시가 아니라 proposal draft 저장으로 읽히는지
  - [ ] `Proposal Registry` tab에서 저장된 proposal draft를 다시 inspect할 수 있는지
  - [ ] proposal 저장이 current candidate registry 또는 pre-live registry를 자동 변경하지 않는다고 이해되는지

## 7. Portfolio Proposal Monitoring Review 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal > Monitoring Review`
  - `.note/finance/phase30/PHASE30_PORTFOLIO_PROPOSAL_MONITORING_REVIEW_FIFTH_WORK_UNIT.md`
- 체크 항목:
  - [ ] 저장된 proposal이 없을 때 빈 상태 안내가 보이는지
  - [ ] proposal을 저장한 뒤 `Monitoring Review` tab에서 monitoring summary table이 보이는지
  - [ ] summary table에 Proposal ID, Status, Monitoring State, Components, Weight Total, Blockers, Review Gaps, Review Date, Next Action이 보이는지
  - [ ] proposal을 선택하면 objective, construction, component monitoring table이 보이는지
  - [ ] component table에서 후보별 Proposal Role, Target Weight, Data Trust, Pre-Live, Promotion, Shortlist, Deployment가 보이는지
  - [ ] Blockers와 Review Gaps가 분리되어 보이는지
  - [ ] Operator Decision과 proposal JSON을 다시 inspect할 수 있는지
  - [ ] `Monitoring State`가 live approval이나 주문 지시가 아니라 review 요약으로 읽히는지

## 8. Portfolio Proposal Pre-Live Feedback 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal > Pre-Live Feedback`
  - `.note/finance/phase30/PHASE30_PORTFOLIO_PROPOSAL_PRE_LIVE_FEEDBACK_SIXTH_WORK_UNIT.md`
- 체크 항목:
  - [ ] 저장된 proposal이 없을 때 빈 상태 안내가 보이는지
  - [ ] proposal을 저장한 뒤 Pre-Live feedback summary table이 보이는지
  - [ ] summary table에 Linked Pre-Live, Paper Tracking, Status Drift, Overdue Reviews, Feedback Gaps가 보이는지
  - [ ] proposal을 선택하면 component별 Saved Pre-Live와 Current Pre-Live가 함께 보이는지
  - [ ] Status Drift가 proposal 저장 당시 snapshot과 현재 Pre-Live 상태 차이로 읽히는지
  - [ ] Current Review Date, Review Overdue, Tracking Cadence, Current Next Action이 보이는지
  - [ ] Feedback Gaps가 자동 승인 / 자동 수정이 아니라 운영 재확인 항목으로 읽히는지
  - [ ] 상태를 바꾸려면 `Backtest > Pre-Live Review`에서 별도 record를 저장해야 한다고 이해되는지

## 9. Portfolio Proposal Paper Tracking Feedback 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal > Paper Tracking Feedback`
  - `.note/finance/phase30/PHASE30_PORTFOLIO_PROPOSAL_PAPER_TRACKING_FEEDBACK_SEVENTH_WORK_UNIT.md`
- 체크 항목:
  - [ ] 저장된 proposal이 없을 때 빈 상태 안내가 보이는지
  - [ ] proposal을 저장한 뒤 Paper Tracking Feedback summary table이 보이는지
  - [ ] summary table에 Paper Tracking, Missing Current Result, Worsened, Stable / Better, Feedback Gaps가 보이는지
  - [ ] proposal을 선택하면 component별 Saved CAGR, Current CAGR, CAGR Delta가 보이는지
  - [ ] component별 Saved MDD, Current MDD, MDD Delta가 보이는지
  - [ ] Performance Signal이 `needs_paper_tracking`, `missing_current_result`, `missing_saved_snapshot`, `worsened`, `stable_or_better` 중 하나로 읽히는지
  - [ ] Tracking Cadence, Stop Condition, Success Condition이 Pre-Live tracking plan에서 읽힌 정보로 보이는지
  - [ ] Feedback Gaps가 paper tracking 미진입, missing result, CAGR / MDD 악화 같은 재확인 항목으로 읽히는지
  - [ ] 이 tab이 실제 paper PnL 자동 계산, proposal 자동 수정, live approval이 아니라 최신 Pre-Live result snapshot을 읽는 보조 surface로 이해되는지

## 한 줄 판단 기준

이번 Phase 30 QA는
**새 기능이 많아졌는가**가 아니라,
**Phase 29 이후 흐름, Portfolio Proposal 계약, 첫 registry helper split, Proposal Draft UI, Monitoring Review, Pre-Live Feedback, Paper Tracking Feedback이 live approval과 구분되는 방식으로 이해되고 QA 가능한가**
를 확인한다.
