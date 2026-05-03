# Phase 31 Test Checklist

## 목적

이 checklist는 Phase 31에서 구현한 Portfolio Risk / Live Readiness Validation 흐름이
Candidate Review / Pre-Live / Portfolio Proposal과 중복되지 않고,
실전 후보 검토 전 필요한 위험 검증으로 읽히는지 확인하기 위한 문서다.

현재는 Phase 31 구현 완료 후 manual QA checklist다.
이 checklist 확인이 끝나면 Phase 31 closeout 여부를 판단한다.

## 사용 방법

- 아래 항목은 사용자가 직접 `[ ]`를 `[x]`로 바꾸며 확인한다.
- 일부 항목이 후속 phase로 넘어가면 그 이유를 completion summary에 남긴다.
- 이 checklist는 live approval이나 주문 가능 여부를 확인하는 문서가 아니다.

## 1. 단일 후보 Validation Pack 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal`
- 체크 항목:
  - [x] `Proposal Components`에서 후보 1개를 선택하면 `단일 후보 직행 평가`가 열리는지
  - [x] `3. Live Readiness 직행 평가` 아래에 `4. Portfolio Risk / Validation Pack`이 보이는지
  - [x] Validation Route, Risk Score, Source, Components, Weight Total, Max Weight, Next Phase가 보이는지
  - [x] component table에 Registry ID, Role, Weight, Family, Benchmark, Universe, Factors, Pre-Live, Data Trust, Promotion, Deployment가 보이는지
  - [x] hard blocker / paper tracking gap / review gap이 분리되어 보이는지
  - [x] `Validation 기준 / Phase 32 handoff` expander에서 checks와 handoff summary를 확인할 수 있는지
  - [ ] 단일 후보 직행 평가에서는 `저장된 Portfolio Proposal 확인` 목록이 노출되지 않는지

## 2. 작성 중 Proposal Validation Pack 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal > 포트폴리오 초안 작성`
- 체크 항목:
  - [x] 후보 2개 이상을 선택하면 `목적 / 역할 / 비중 설계`가 열리는지
  - [x] 후보별 Proposal Role, Target Weight, Weight Reason을 입력한 뒤 저장 전 Validation Pack이 보이는지
  - [x] target weight 합계가 100%가 아니면 hard blocker 또는 저장 blocker가 보이는지
  - [x] 저장 blocker가 보일 때 `Target Weight 합계를 100%로 맞추세요`, `core_anchor 필요`처럼 무엇을 고쳐야 하는지 알 수 있는 안내가 같이 보이는지
  - [x] core_anchor가 없으면 validation에서 blocker 또는 review gap으로 읽히는지
  - [x] 같은 family / benchmark / universe / factor set에 몰리면 review gap이 표시되는지
  - [x] Validation Pack을 펼쳐도 `Save Portfolio Proposal Draft`가 자동 실행되지 않고, `Open Live Readiness`는 비활성 상태로 남는지
  - [ ] `Save Portfolio Proposal Draft`를 클릭하면 저장 성공 안내가 보이고, 안내 문구가 `4. 저장된 Portfolio Proposal 확인`으로 이어지는지

### Proposal Role 확인 기준

- `core_anchor`: 포트폴리오의 중심 후보다. active weight가 있는 proposal에는 최소 1개가 필요하다.
- `return_driver`: 수익률 기여를 기대하는 공격 후보지만, core anchor 없이 이것만 있으면 차단된다.
- `diversifier`: core anchor와 다른 위험 원천을 섞어 변동성을 낮추는 보조 후보다.
- `defensive_sleeve`: 하락장 / risk-off 구간 완충을 기대하는 방어 후보다.
- `satellite`: 작은 비중으로 특정 아이디어를 더하는 보조 후보다.
- `watch_only`: 이번 proposal에서는 관찰만 하고 보통 active weight를 주지 않는 후보다.

## 3. 저장된 Portfolio Proposal 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal`
  - 후보 2개 이상 선택 후 `4. 저장된 Portfolio Proposal 확인 > Validation Pack`
- 체크 항목:
  - [ ] 저장된 proposal이 없을 때 `아직 저장된 Portfolio Proposal이 없습니다.` 안내가 보이는지
  - [ ] 후보 2개 이상을 선택한 포트폴리오 초안 작성 흐름에서만 저장된 proposal 목록이 보이는지
  - [ ] proposal 저장 후 `Saved Proposals` count 또는 summary table에 새 proposal이 반영되는지
  - [ ] 저장된 proposal이 있으면 summary table에 Proposal ID, Validation Route, Score, Components, Weight Total, Max Weight, Hard Blockers, Paper Gaps, Review Gaps가 보이는지
  - [ ] `Review Validation Pack`에서 proposal을 선택하면 상세 validation panel이 보이는지
  - [ ] 저장된 proposal의 Monitoring / Pre-Live Feedback / Paper Tracking / Raw JSON tab도 기존처럼 동작하는지

- QA reset 참고:
  - 저장된 proposal을 초기화해야 하면 `.note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`을 삭제해도 된다.
  - 다음에 `Save Portfolio Proposal Draft`를 실행하면 앱이 필요한 JSONL 파일을 다시 만든다.

## 4. Phase 32 Handoff 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal > 단일 후보 또는 Portfolio Proposal Validation Pack > Validation 기준 / Phase 32 handoff`
  - `.note/finance/phases/phase31/PHASE31_NEXT_PHASE_PREPARATION.md`
- 체크 항목:
  - [ ] `READY_FOR_ROBUSTNESS_REVIEW`는 Phase 32 robustness 검증 후보 가능으로 읽히는지
  - [ ] `PAPER_TRACKING_REQUIRED`는 paper tracking 보강 필요로 읽히는지
  - [ ] `NEEDS_PORTFOLIO_RISK_REVIEW`는 비중 / 중복 / Data Trust gap 보강 필요로 읽히는지
  - [ ] `BLOCKED_FOR_LIVE_READINESS`는 hard blocker 해결 전 차단으로 읽히는지
  - [ ] Phase 32에서 실제로 무엇을 검증할지 next phase preparation에 쉽게 설명되어 있는지

## 5. 문서와 closeout 확인

- 확인 문서:
  - `.note/finance/phases/phase31/PHASE31_PORTFOLIO_RISK_AND_LIVE_READINESS_VALIDATION_PLAN.md`
  - `.note/finance/phases/phase31/PHASE31_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/phases/phase31/PHASE31_COMPLETION_SUMMARY.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
- 체크 항목:
  - [ ] Phase 31이 `implementation_complete / manual_qa_pending` 상태로 설명되는지
  - [ ] Phase 31이 duplicate decision record가 아니라 기존 후보/Proposal을 읽는 검증 단계로 설명되는지
  - [ ] Phase 30 manual QA pending 상태와 Phase 31 manual QA pending 상태가 혼동되지 않는지

## 한 줄 판단 기준

이번 Phase 31 QA는
**후보 또는 Portfolio Proposal을 실전 검토 후보로 더 밀어도 되는지, 투자 승인과 분리된 위험 검증 pack으로 이해할 수 있는가**
를 확인한다.
