# Phase 25 Test Checklist

## 목적

이 checklist는 Phase 25에서 만든 Pre-Live 운영 점검 흐름을
사용자가 실제로 이해하고 검수할 수 있는지 확인하기 위한 문서다.

현재 확인 대상은 `helper 기반 Pre-Live 초안 생성 흐름`과
`Backtest > Pre-Live Review` UI다.

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
  - [x] Phase 25가 live trading이나 투자 승인 단계가 아니라 pre-live 운영 점검 단계라는 점이 이해되는지
  - [x] `Real-Money 검증 신호`는 백테스트 결과에 붙는 진단표이고, `Pre-Live 운영 점검`은 그 다음 행동을 기록하는 절차라는 차이가 이해되는지
  - [x] `watchlist`, `paper tracking`, `hold`, `re-review`가 후보를 관리하기 위한 상태라는 점이 이해되는지
  - [x] Pre-Live의 핵심이 상태값 자체가 아니라 `operator_reason`, `next_action`, `review_date`, `tracking_plan`을 함께 남기는 다음 행동 기록이라는 점이 이해되는지

## 2. 후보 기록 포맷 확인

- 확인 위치:
  - `.note/finance/phase25/PHASE25_PRE_LIVE_CANDIDATE_RECORD_CONTRACT_SECOND_WORK_UNIT.md`
  - `.note/finance/operations/PRE_LIVE_CANDIDATE_REGISTRY_GUIDE.md`
  - `plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py`
- 체크 항목:
  - [x] `CURRENT_CANDIDATE_REGISTRY.jsonl`은 후보 자체를 저장하고, `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`은 후보의 운영 상태를 저장한다는 차이가 이해되는지
  - [x] 후보 기록 필드에 source / strategy_or_bundle / settings_snapshot / result_snapshot / real_money_signal / pre_live_status / operator_reason / next_action / review_date가 포함되는지
  - [x] `pre_live_status`가 `watchlist`, `paper_tracking`, `hold`, `reject`, `re_review` 중 하나로 정리되어 있는지
  - [x] `tracking_plan`에 cadence / stop_condition / success_condition이 들어가며, 이것이 Real-Money 상태값과 Pre-Live를 구분하는 핵심 정보라는 점이 이해되는지
  - [x] helper script의 `template`, `list`, `show`, `append`, `validate` 역할이 이해되는지

## 3. operator review workflow 확인

- 확인 위치:
  - `.note/finance/phase25/PHASE25_OPERATOR_REVIEW_WORKFLOW_THIRD_WORK_UNIT.md`
  - `.note/finance/phase25/PHASE25_PRE_LIVE_REVIEW_UI_FOURTH_WORK_UNIT.md`
  - `.note/finance/operations/PRE_LIVE_CANDIDATE_REGISTRY_GUIDE.md`
  - `plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py`
- 확인 방법:
  - current candidate 목록을 먼저 확인한다.
    ```bash
    python3 plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py list
    ```
  - 그중 하나를 골라 Pre-Live 초안을 출력한다.
    ```bash
    python3 plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py draft-from-current value_current_anchor_top14_psr
    ```
  - 실제 저장이 아니라 초안 확인만 할 때는 `--append`를 붙이지 않는다.
- 체크 항목:
  - [x] `draft-from-current` 결과에서 원본 후보 id가 `source_candidate_registry_id`로 연결되는지
  - [x] `shortlist = paper_probation` 후보가 기본적으로 `pre_live_status = paper_tracking` 초안으로 나오는지
  - [x] `shortlist = watchlist` 후보가 기본적으로 `pre_live_status = watchlist` 초안으로 나오는지
  - [x] `operator_reason`, `next_action`, `tracking_plan`이 사람이 읽을 수 있는 설명으로 채워지는지
  - [x] `--append`를 붙일 때만 실제 `.note/finance/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`에 저장된다는 점이 이해되는지
  - [x] Real-Money 검증 신호와 Pre-Live 운영 상태가 문서와 helper output에서 구분되어 보이는지

## 4. Backtest UI Pre-Live Review 확인

- 확인 위치:
  - `Backtest > Pre-Live Review`
- 체크 항목:
  - [x] Backtest panel에 `Pre-Live Review`가 보이는지
  - [x] `Create From Current Candidate` 탭에서 current candidate 목록이 보이는지
  - [x] 후보를 선택하면 `Promotion`, `Shortlist`, `Deployment`, `Default Status`가 보이는지
  - [x] `Pre-Live Status`, `Operator Reason`, `Next Action`, `Review Date`를 확인하거나 수정할 수 있는지
  - [x] 저장 전 JSON 초안이 보이고, 저장 버튼을 누르기 전에는 registry에 기록되지 않는다는 점이 이해되는지
  - [x] `Save Pre-Live Record`를 누르면 `Pre-Live Registry` 탭에서 저장된 active record가 보이는지
  - [x] 화면 문구가 live trading 승인이나 실제 투자 실행으로 오해되지 않는지

## 5. 문서와 closeout 확인

- 확인 문서:
  - `.note/finance/phase25/PHASE25_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/phase25/PHASE25_COMPLETION_SUMMARY.md`
  - `.note/finance/phase25/PHASE25_NEXT_PHASE_PREPARATION.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
- 체크 항목:
  - [x] Phase 25 상태가 실제 구현 상태와 맞는지
  - [x] 새 문서가 index에서 바로 찾히는지
  - [x] 다음 단계로 넘어가기 위한 설명이 충분한지

## 한 줄 판단 기준

이번 checklist는
**좋은 전략을 골랐는가**가 아니라,
**좋아 보이는 백테스트 결과를 실전 전 운영 상태로 안전하게 관리할 수 있는가**
를 확인하는 문서다.
