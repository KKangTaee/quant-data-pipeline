# Phase 20 Test Checklist

## 목적

- `Phase 20`에서 정리한 candidate consolidation / operator workflow hardening이
  실제 UI에서 자연스럽게 이어지는지 확인한다.
- 이번 checklist는
  "새 후보가 더 추가됐는가"보다
  **현재 후보를 다시 꺼내고, compare하고, 저장하고, 다시 이어 쓰는 흐름이 편해졌는가**
  를 보는 데 초점을 둔다.

## 사용 방법

- 아래 항목은 직접 `[ ]`를 `[x]`로 바꾸며 확인한다.
- 특별한 사유가 없으면, 주요 체크 항목이 모두 완료된 뒤 다음 major phase로 넘어간다.
- 일부 항목을 보류하면 그 이유를 이 문서나 handoff에 짧게 남긴다.

## 추천 실행 순서

1. current candidate를 compare로 다시 불러오는 흐름 확인
2. compare -> weighted portfolio 흐름 확인
3. saved portfolio 재진입 흐름 확인
4. phase closeout 문서와 index 확인

## 1. current candidate re-entry 확인

- 확인 위치:
  - `Backtest > Compare & Portfolio Builder > Current Candidate Re-entry`
- 체크 항목:
  - [ ] `Current Candidate Re-entry` 섹션이 보이는지
  - [ ] `Load Current Anchors`와 `Load Lower-MDD Near Misses` quick action이 보이는지
  - [ ] `Inspect Current Candidate Bundle Options` 안에서 후보 제목, family, 역할, contract 요약이 읽기 쉽게 보이는지
  - [ ] 여러 후보를 직접 선택해서 `Load Selected Candidates Into Compare`를 누를 수 있는지
  - [ ] 불가능한 조합일 때 왜 막히는지 안내 문구가 이해되게 보이는지
  - [ ] current candidate를 불러온 뒤 compare form에 strategy/period/override가 자연스럽게 채워지는지

## 2. compare -> weighted portfolio 흐름 확인

- 확인 위치:
  - `Backtest > Compare & Portfolio Builder`
  - compare 실행 후 `Weighted Portfolio Builder`
- 체크 항목:
  - [ ] compare를 실행한 뒤 `Weighted Portfolio Builder` 위에 `Current Compare Bundle` 요약이 보이는지
  - [ ] `Current Compare Bundle`에서 `Source`, `Label`, `Strategies`가 현재 compare 맥락과 맞게 보이는지
  - [ ] registry 기반 current candidate를 compare로 불러왔을 때 registry ids 또는 source 정보가 요약에 보이는지
  - [ ] weighted portfolio를 만들 때 compare source 맥락을 잃지 않고 바로 이어서 저장할 수 있는지
  - [ ] weighted portfolio 결과가 생성된 뒤 다음 행동이 자연스럽게 이해되는지

## 3. saved portfolio 재진입 흐름 확인

- 확인 위치:
  - `Backtest > Compare & Portfolio Builder > Saved Portfolios`
- 체크 항목:
  - [ ] 현재 weighted portfolio를 저장할 때 이름 placeholder가 source label 또는 strategy 조합 기준으로 자연스럽게 보이는지
  - [ ] 저장된 포트폴리오 목록에 `Source` 컬럼이 보이는지
  - [ ] 저장된 포트폴리오 상세에서 `Source & Next Step` 탭이 보이는지
  - [ ] `Source & Next Step` 탭에서 이 포트폴리오가 어디서 왔는지와 다음 행동이 쉽게 읽히는지
  - [ ] `Edit In Compare`가 저장된 전략 조합과 weights를 compare 화면으로 다시 채워주는지
  - [ ] `Replay Saved Portfolio`가 저장된 compare context와 weights를 그대로 다시 실행하는지
  - [ ] saved portfolio를 다시 열었을 때 "수정할지 / 그대로 재실행할지" 판단이 더 쉬워졌는지

## 4. phase closeout 문서와 index 확인

- 확인 문서:
  - [PHASE20_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase20/PHASE20_CURRENT_CHAPTER_TODO.md)
  - [PHASE20_COMPLETION_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase20/PHASE20_COMPLETION_SUMMARY.md)
  - [PHASE20_NEXT_PHASE_PREPARATION.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase20/PHASE20_NEXT_PHASE_PREPARATION.md)
  - [PHASE20_CANDIDATE_CONSOLIDATION_AND_OPERATOR_WORKFLOW_HARDENING_PLAN.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase20/PHASE20_CANDIDATE_CONSOLIDATION_AND_OPERATOR_WORKFLOW_HARDENING_PLAN.md)
  - [PHASE20_CURRENT_CANDIDATE_COMPARE_REENTRY_FIRST_WORK_UNIT.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase20/PHASE20_CURRENT_CANDIDATE_COMPARE_REENTRY_FIRST_WORK_UNIT.md)
  - [PHASE20_COMPARE_WEIGHTED_AND_SAVED_REENTRY_HARDENING_SECOND_WORK_UNIT.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase20/PHASE20_COMPARE_WEIGHTED_AND_SAVED_REENTRY_HARDENING_SECOND_WORK_UNIT.md)
  - [FINANCE_DOC_INDEX.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/FINANCE_DOC_INDEX.md)
  - [MASTER_PHASE_ROADMAP.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/MASTER_PHASE_ROADMAP.md)
- 체크 항목:
  - [ ] Phase 20 상태가 `practical closeout / manual_validation_pending`으로 보이는지
  - [ ] Phase 20 first/second work-unit, completion summary, next preparation, checklist 문서를 index에서 바로 찾을 수 있는지
  - [ ] roadmap에 Phase 20가 operator workflow hardening closeout 기준으로 반영됐는지
  - [ ] completion summary가 "무엇이 쉬워졌는지"를 쉽게 설명하는지
  - [ ] next phase preparation 문서가 다음 질문을 이해하기 쉽게 정리하는지

## 한 줄 판단 기준

- 이번 checklist는
  "기능이 더 많아졌는가"보다,
  **현재 후보를 다시 보고 비교하고 저장하고 다시 이어 쓰는 흐름이 실제로 더 자연스러워졌는가**
  를 확인하는 checklist다.
