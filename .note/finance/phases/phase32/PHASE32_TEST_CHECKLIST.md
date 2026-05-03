# Phase 32 Test Checklist

## 목적

이 checklist는 Phase 32 `Robustness / Stress Validation Pack`을 사용자가 화면에서 확인하기 위한 문서다.

현재 Phase 32는 `complete / manual_qa_completed` 상태다.
아래 항목은 사용자 manual QA 완료 신호에 따라 모두 확인 완료로 기록한다.

## 사용 방법

- 아래 항목은 사용자가 직접 `[ ]`를 `[x]`로 바꾸며 확인했다.
- 주요 체크 항목이 완료되었으므로 Phase 32는 closeout 상태다.
- 별도 deferred 항목은 없다.

## 1. 단일 후보 Robustness / Stress Pack 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal`
  - current candidate 1개 선택
  - `4. Portfolio Risk / Validation Pack`
- 체크 항목:
  - [x] `Portfolio Risk / Live Readiness Validation Pack` 아래에 `Robustness / Stress Validation Preview`가 보이는지
  - [x] `Robustness Route`, `Robustness Score`, `Verdict`, `Next Action`이 보이는지
  - [x] component table에서 기간, CAGR, MDD, benchmark, contract summary, compare evidence 여부가 보이는지
  - [x] `Stress / Sensitivity Summary` table이 보이는지
  - [x] 단일 후보에서는 portfolio-only stress가 `NOT_APPLICABLE`로 읽힐 수 있는지
  - [x] preview를 열어도 proposal draft 저장이나 live approval이 자동 수행되지 않는지

## 2. 작성 중 Portfolio Proposal Robustness / Stress Pack 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal`
  - current candidate 2개 이상 선택
  - `2. 목적 / 역할 / 비중 설계`
  - `3. Proposal 저장 및 다음 단계 판단`
- 체크 항목:
  - [x] target weight 합계가 100%이고 active component에 `core_anchor`가 있으면 robustness preview가 생성되는지
  - [x] 기간 / contract / benchmark / compare evidence가 부족한 후보는 `Input Gaps` 또는 `Robustness Blockers`에서 이유가 보이는지
  - [x] `Suggested Sweeps`가 period split, recent-window, benchmark sensitivity, parameter sensitivity 같은 다음 실행 안내로 읽히는지
  - [x] `Stress / Sensitivity Summary`에서 `Input Status`와 `Result Status`가 구분되어 보이는지
  - [x] `Result Status = NOT_RUN`이 실패가 아니라 아직 실제 stress runner가 실행되지 않은 상태로 읽히는지
  - [x] `Save Portfolio Proposal Draft`는 별도 버튼으로 남아 있고 preview 표시만으로 자동 저장되지 않는지

## 3. 저장된 Portfolio Proposal 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal`
  - current candidate 2개 이상 선택
  - `4. 저장된 Portfolio Proposal 확인`
  - `Validation` tab
- 체크 항목:
  - [x] 저장 proposal validation 요약 표에 `Robustness Route`, `Robustness Score`, `Phase33 Handoff`가 보이는지
  - [x] 저장 proposal detail의 Validation Pack에서도 같은 robustness preview가 보이는지
  - [x] 저장 proposal detail에서 `Stress / Sensitivity Summary` table이 보이는지
  - [x] 저장 당시 evidence snapshot과 현재 current candidate / Pre-Live snapshot이 섞여도 route가 설명 가능한 상태로 읽히는지

## 4. Phase 33 Handoff 확인

- 확인 위치:
  - `Backtest > Portfolio Proposal > Validation Pack`
  - `Phase 33 Handoff`
  - `Phase 33 paper ledger 준비 기준`
- 체크 항목:
  - [x] `Phase 33 Handoff` route panel이 보이는지
  - [x] route가 `READY_FOR_PAPER_LEDGER_PREP`, `NEEDS_STRESS_INPUT_REVIEW`, `BLOCKED_FOR_PAPER_LEDGER` 중 하나로 읽히는지
  - [x] source id, component weight, tracking benchmark, stress summary contract 준비 상태가 표로 보이는지
  - [x] 이 handoff가 paper ledger 준비 가능성일 뿐, live approval이나 주문 지시가 아니라는 문구가 보이는지

## 5. Route 해석 확인

| Route | 확인 기준 |
|---|---|
| `READY_FOR_STRESS_SWEEP` | stress 검증을 실행할 기본 입력이 준비된 상태로 읽히는지 |
| `NEEDS_ROBUSTNESS_INPUT_REVIEW` | benchmark, compare evidence, 기간 길이 같은 입력 gap 보강 필요로 읽히는지 |
| `BLOCKED_FOR_ROBUSTNESS` | Phase 31 blocker, 성과 snapshot 누락, 기간 누락, contract 누락처럼 선해결 항목이 있는 상태로 읽히는지 |
| `READY_FOR_PAPER_LEDGER_PREP` | Phase 33에서 paper ledger row를 준비할 수 있는 상태로 읽히는지 |
| `NEEDS_STRESS_INPUT_REVIEW` | paper ledger 전에 stress 입력 보강이 필요한 상태로 읽히는지 |
| `BLOCKED_FOR_PAPER_LEDGER` | paper ledger 준비 전 반드시 해결할 blocker가 있는 상태로 읽히는지 |

체크 항목:

- [x] route 이름만 보고도 다음 행동이 대략 이해되는지
- [x] blocker / input gap 문구가 "무엇을 고쳐야 하는지"로 읽히는지
- [x] Phase32가 실제 기간 분할 백테스트나 parameter sweep을 이미 실행했다는 뜻으로 오해되지 않는지

## 6. 문서와 상태 확인

- 확인 문서:
  - `.note/finance/phases/phase32/PHASE32_ROBUSTNESS_AND_STRESS_VALIDATION_PACK_PLAN.md`
  - `.note/finance/phases/phase32/PHASE32_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/phases/phase32/PHASE32_COMPLETION_SUMMARY.md`
  - `.note/finance/phases/phase32/PHASE32_NEXT_PHASE_PREPARATION.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
- 체크 항목:
  - [x] Phase 32가 `complete / manual_qa_completed`로 표시되는지
  - [x] 1~4번째 작업이 모두 완료로 표시되는지
  - [x] Phase 32가 live approval / 최종 투자 선정 단계가 아니라는 경계가 문서와 UI에 남아 있는지
  - [x] Phase 33에서 실제로 무엇을 만들지 next phase preparation에 쉽게 설명되어 있는지

## 한 줄 판단 기준

이번 Phase32 QA는
**후보나 proposal을 stress 검증과 paper ledger 준비 상태로 읽을 수 있고, 아직 실제 승인 / 주문 / 최종 선정이 아니라는 경계가 분명하면 통과**다.
