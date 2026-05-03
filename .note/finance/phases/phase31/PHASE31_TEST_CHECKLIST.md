# Phase 31 Test Checklist

## 목적

이 checklist는 Phase 31에서 만드는 Portfolio Risk / Live Readiness Validation 흐름이
Candidate Review / Pre-Live / Portfolio Proposal과 중복되지 않고,
실전 후보 검토 전 필요한 위험 검증으로 읽히는지 확인하기 위한 문서다.

현재는 Phase 31 kickoff checklist 초안이다.
실제 구현이 끝나면 화면 경로와 체크 항목을 구현 결과에 맞춰 갱신한다.

## 사용 방법

- 아래 항목은 사용자가 직접 `[ ]`를 `[x]`로 바꾸며 확인한다.
- Phase 31 구현 완료 후 targeted manual QA에 사용한다.
- 일부 항목이 후속 phase로 넘어가면 그 이유를 completion summary에 남긴다.

## 1. Validation Pack 위치 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal`
- 체크 항목:
  - [ ] 단일 후보 또는 저장된 proposal draft를 선택한 뒤 Portfolio Risk / Live Readiness Validation 결과를 볼 수 있는지
  - [ ] 이 화면이 live approval이나 주문 지시가 아니라 검증 surface로 읽히는지
  - [ ] Candidate Review의 `다음 단계 진행 판단`이나 Portfolio Proposal의 `Live Readiness 진입 평가`를 반복 저장하는 UI로 보이지 않는지

## 2. 입력 계약 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal > Validation Pack`
- 체크 항목:
  - [ ] 단일 후보 direct path와 다중 후보 proposal path가 같은 validation panel에서 읽히는지
  - [ ] Current Candidate, Pre-Live Record, Proposal Draft 중 어떤 입력을 읽고 있는지 표시되는지
  - [ ] 입력이 부족할 때 사용자가 어느 이전 단계로 돌아가야 하는지 보이는지

## 3. Portfolio Risk Summary 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal > Validation Pack > Portfolio Risk Summary`
- 체크 항목:
  - [ ] 후보 수, target weight 합계, core anchor 유무가 보이는지
  - [ ] concentration 또는 active 후보 상태 blocker가 있으면 차단 항목으로 보이는지
  - [ ] `ready`, `review required`, `blocked` 같은 route가 투자 승인과 분리된 검증 신호로 읽히는지

## 4. Component Risk / Overlap 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal > Validation Pack > Component Risk`
- 체크 항목:
  - [ ] 후보별 role, target weight, strategy family, benchmark, Pre-Live status, promotion, deployment가 함께 보이는지
  - [ ] 같은 strategy family, universe, factor, benchmark 편중이 가능한 범위에서 표시되는지
  - [ ] hard blocker와 review gap이 구분되어 보이는지

## 5. Phase 32 Handoff 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal > Validation Pack > Next Action`
  - `.note/finance/phases/phase31/PHASE31_NEXT_PHASE_PREPARATION.md`
- 체크 항목:
  - [ ] validation 결과가 Phase 32 robustness 검증으로 넘길 수 있는지 설명하는지
  - [ ] paper tracking이 먼저 필요한 후보와 robustness로 넘길 후보가 구분되는지
  - [ ] Phase 32에서 실제로 무엇을 검증할지 next phase preparation에 쉽게 설명되어 있는지

## 6. 문서와 closeout 확인

- 확인 문서:
  - `.note/finance/phases/phase31/PHASE31_PORTFOLIO_RISK_AND_LIVE_READINESS_VALIDATION_PLAN.md`
  - `.note/finance/phases/phase31/PHASE31_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/phases/phase31/PHASE31_COMPLETION_SUMMARY.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
- 체크 항목:
  - [ ] Phase 31이 `Portfolio Risk / Live Readiness Validation`으로 설명되는지
  - [ ] Phase 31이 duplicate decision record가 아니라 기존 후보/Proposal을 읽는 검증 단계로 설명되는지
  - [ ] Phase 30 manual QA pending 상태와 Phase 31 active 상태가 혼동되지 않는지

## 한 줄 판단 기준

이번 Phase 31 QA는
**후보 또는 Portfolio Proposal을 실전 검토 후보로 더 밀어도 되는지, 투자 승인과 분리된 위험 검증 pack으로 이해할 수 있는가**
를 확인한다.
