# Phase 32 Test Checklist

## 목적

이 checklist는 Phase 32 `Robustness / Stress Validation Pack`을 사용자가 화면에서 확인하기 위한 문서다.

현재 Phase 32는 `active / not_ready_for_qa` 상태이며,
아래 항목은 첫 번째 작업인 `Robustness / Stress Validation Preview` 확인 기준이다.
phase 전체 QA handoff 전에는 stress result contract와 summary surface 항목이 더 추가될 수 있다.

## 사용 방법

- 아래 항목은 사용자가 직접 `[ ]`를 `[x]`로 바꾸며 확인한다.
- 현재는 최종 closeout checklist가 아니라 첫 구현 단위 smoke / manual preview checklist로 읽는다.
- Phase 32 전체 구현이 끝나면 이 checklist를 최종 QA용으로 다시 정리한다.

## 1. 단일 후보 Robustness Preview 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal`
  - current candidate 1개 선택
  - `4. Portfolio Risk / Validation Pack`
- 체크 항목:
  - [ ] `Portfolio Risk / Live Readiness Validation Pack` 아래에 `Robustness / Stress Validation Preview`가 보이는지
  - [ ] `Robustness Route`, `Robustness Score`, `Verdict`, `Next Action`이 보이는지
  - [ ] component table에서 기간, CAGR, MDD, benchmark, contract summary, compare evidence 여부가 보이는지
  - [ ] 이 preview가 proposal draft 저장이나 live approval을 자동 수행하지 않는지

## 2. 작성 중 Portfolio Proposal Preview 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal`
  - current candidate 2개 이상 선택
  - `2. 목적 / 역할 / 비중 설계`
  - `3. Proposal 저장 및 다음 단계 판단`
- 체크 항목:
  - [ ] target weight 합계가 100%이고 active component에 `core_anchor`가 있으면 robustness preview가 생성되는지
  - [ ] 기간 / contract / benchmark / compare evidence가 부족한 후보는 `Input Gaps` 또는 `Robustness Blockers`에서 이유가 보이는지
  - [ ] `Suggested Sweeps`가 period split, recent-window, benchmark sensitivity, parameter sensitivity 같은 다음 실행 안내로 읽히는지
  - [ ] `Save Portfolio Proposal Draft`는 별도 버튼으로 남아 있고 preview 표시만으로 자동 저장되지 않는지

## 3. 저장된 Portfolio Proposal Preview 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal`
  - current candidate 2개 이상 선택
  - `4. 저장된 Portfolio Proposal 확인`
  - 저장된 proposal 선택
- 체크 항목:
  - [ ] 저장 proposal validation 요약 표에 `Robustness Route`와 `Robustness Score`가 보이는지
  - [ ] 저장 proposal detail의 Validation Pack에서도 같은 robustness preview가 보이는지
  - [ ] 저장 당시 evidence snapshot과 현재 current candidate / Pre-Live snapshot이 섞여도 route가 설명 가능한 상태로 읽히는지

## 4. Route 해석 확인

| Route | 확인 기준 |
|---|---|
| `READY_FOR_STRESS_SWEEP` | stress 검증을 실행할 기본 입력이 준비된 상태로 읽히는지 |
| `NEEDS_ROBUSTNESS_INPUT_REVIEW` | benchmark, compare evidence, 기간 길이 같은 입력 gap 보강 필요로 읽히는지 |
| `BLOCKED_FOR_ROBUSTNESS` | Phase 31 blocker, 성과 snapshot 누락, 기간 누락, contract 누락처럼 선해결 항목이 있는 상태로 읽히는지 |

체크 항목:

- [ ] route 이름만 보고도 다음 행동이 대략 이해되는지
- [ ] blocker / input gap 문구가 "무엇을 고쳐야 하는지"로 읽히는지
- [ ] 이 기능이 실제 기간 분할 백테스트나 parameter sweep을 이미 실행했다는 뜻으로 오해되지 않는지

## 5. 문서와 상태 확인

- 확인 문서:
  - `.note/finance/phases/phase32/PHASE32_ROBUSTNESS_AND_STRESS_VALIDATION_PACK_PLAN.md`
  - `.note/finance/phases/phase32/PHASE32_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/phases/phase32/PHASE32_ROBUSTNESS_INPUT_PREVIEW_FIRST_WORK_UNIT.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
- 체크 항목:
  - [ ] Phase 32가 `active / not_ready_for_qa`로 표시되는지
  - [ ] 첫 번째 작업이 robustness input preview라는 점이 문서에 설명되어 있는지
  - [ ] Phase 32가 live approval / 최종 투자 선정 단계가 아니라는 경계가 문서와 UI에 남아 있는지

## 한 줄 판단 기준

이번 첫 구현 단위는
**후보나 proposal을 stress 검증으로 넘기기 전에 필요한 입력이 충분한지 사용자가 읽을 수 있으면 통과**다.
