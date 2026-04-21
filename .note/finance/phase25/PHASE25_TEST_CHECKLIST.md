# Phase 25 Test Checklist

## 목적

이 checklist는 Phase 25에서 만든 Pre-Live 운영 점검 흐름을
사용자가 실제로 이해하고 검수할 수 있는지 확인하기 위한 문서다.

현재는 kickoff 직후 draft다.
실제 UI 또는 저장 기능이 추가되면 확인 위치와 체크 항목을 더 구체적으로 갱신한다.

## 사용 방법

- 아래 항목은 사용자가 직접 `[ ]`를 `[x]`로 바꾸며 확인한다.
- 특별한 사유가 없으면, 모든 주요 체크 항목이 완료된 뒤 다음 major phase로 넘어간다.
- checklist에는 별도 `용어 기준` 섹션을 만들지 않는다.
- 용어 설명이 필요하면 각 체크 항목 안에 `어디서 무엇을 어떻게 확인하는지`를 직접 적는다.

## 1. Phase 25 방향 확인

- 확인 위치:
  - `.note/finance/phase25/PHASE25_PRE_LIVE_OPERATING_SYSTEM_AND_DEPLOYMENT_READINESS_PLAN.md`
  - `.note/finance/phase25/PHASE25_PRE_LIVE_BOUNDARY_AND_OPERATING_FRAME_FIRST_WORK_UNIT.md`
- 체크 항목:
  - [ ] Phase 25가 live trading이나 투자 승인 단계가 아니라 pre-live 운영 점검 단계라는 점이 이해되는지
  - [ ] `Real-Money 검증 신호`는 백테스트 결과에 붙는 진단표이고, `Pre-Live 운영 점검`은 그 다음 행동을 기록하는 절차라는 차이가 이해되는지
  - [ ] `watchlist`, `paper tracking`, `hold`, `re-review`가 후보를 관리하기 위한 상태라는 점이 이해되는지

## 2. 후보 기록 포맷 확인

- 확인 위치:
  - `.note/finance/phase25/PHASE25_PRE_LIVE_CANDIDATE_RECORD_CONTRACT_SECOND_WORK_UNIT.md`
  - `.note/finance/operations/PRE_LIVE_CANDIDATE_REGISTRY_GUIDE.md`
  - `plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py`
- 체크 항목:
  - [ ] `CURRENT_CANDIDATE_REGISTRY.jsonl`은 후보 자체를 저장하고, `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`은 후보의 운영 상태를 저장한다는 차이가 이해되는지
  - [ ] 후보 기록 필드에 source / strategy_or_bundle / settings_snapshot / result_snapshot / real_money_signal / pre_live_status / operator_reason / next_action / review_date가 포함되는지
  - [ ] `pre_live_status`가 `watchlist`, `paper_tracking`, `hold`, `reject`, `re_review` 중 하나로 정리되어 있는지
  - [ ] helper script의 `template`, `list`, `show`, `append`, `validate` 역할이 이해되는지

## 3. operator review workflow 확인

- 확인 위치:
  - 다음 작업에서 추가될 operator review workflow 문서 또는 UI
- 체크 항목:
  - [ ] 사용자가 결과를 보고 `watchlist`, `paper tracking`, `hold`, `reject`, `re-review` 중 다음 행동을 고를 수 있는지
  - [ ] 선택한 상태가 단순 메모가 아니라 나중에 다시 찾을 수 있는 기록으로 남는지
  - [ ] Real-Money 검증 신호와 Pre-Live 운영 상태가 화면에서 섞여 보이지 않는지

## 4. 문서와 closeout 확인

- 확인 문서:
  - `.note/finance/phase25/PHASE25_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/phase25/PHASE25_COMPLETION_SUMMARY.md`
  - `.note/finance/phase25/PHASE25_NEXT_PHASE_PREPARATION.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
- 체크 항목:
  - [ ] Phase 25 상태가 실제 구현 상태와 맞는지
  - [ ] 새 문서가 index에서 바로 찾히는지
  - [ ] 다음 단계로 넘어가기 위한 설명이 충분한지

## 한 줄 판단 기준

이번 checklist는
**좋은 전략을 골랐는가**가 아니라,
**좋아 보이는 백테스트 결과를 실전 전 운영 상태로 안전하게 관리할 수 있는가**
를 확인하는 문서다.
