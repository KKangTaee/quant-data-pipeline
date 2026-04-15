# Phase 21 Test Checklist

## 목적

- 이번 checklist는 `Phase 21`에서 추가한 automation과 persistence baseline이 실제로 다시 쓸 수 있는지 확인하는 문서다.
- 숫자 검증보다 script / workflow / 문서 재사용성 검증에 더 가깝다.

## 사용 방법

- 아래 항목은 사용자가 직접 `[ ]`를 `[x]`로 바꾸며 확인한다.
- 특별한 사유가 없으면, 모든 주요 체크 항목이 완료된 뒤 다음 major phase로 넘어간다.
- 일부 항목을 나중으로 미루면 그 이유를 문서나 handoff에 짧게 남긴다.
- `Phase 20`에서 바뀐 compare / saved portfolio 버튼 이름은 이 checklist의 핵심 검증 대상이 아니다.
  이번 checklist는 UI polish보다 script / registry / workflow 문서 재사용성이 실제로 동작하는지 확인하는 데 더 가깝다.

## 추천 실행 순서

1. phase bundle automation 확인
2. current candidate registry 확인
3. plugin / skill / 문서 연결 확인

## 1. phase bundle automation 확인

- 확인 위치:
  - terminal
  - `plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py`
- 체크 항목:
  - [ ] `--dry-run`으로 새 phase 문서 묶음 경로가 예상대로 나오는지
  - [ ] 실제 실행 시 phase plan / TODO / completion / next-phase / checklist가 한 번에 생성되는지
  - [ ] 생성된 문서가 `PHASE_PLAN_TEMPLATE.md`, `PHASE_TEST_CHECKLIST_TEMPLATE.md` 구조를 잘 따르는지

## 2. current candidate registry 확인

- 확인 위치:
  - terminal
  - `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl`
  - `plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py`
- 체크 항목:
  - [ ] `seed-current-practical` 후 current candidate row가 생성되는지
  - [ ] `list`에서 `Value`, `Quality`, `Quality + Value` 후보가 보이는지
  - [ ] `show <registry_id>`로 특정 후보 상세를 다시 읽을 수 있는지
  - [ ] `validate`가 필수 필드와 문서 경로를 점검하는지

## 3. plugin / skill / workflow 연결 확인

- 확인 위치:
  - `plugins/quant-finance-workflow/skills/finance-backtest-candidate-refinement/SKILL.md`
  - `plugins/quant-finance-workflow/skills/finance-backtest-candidate-refinement/references/repo-workflow.md`
  - `plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
- 체크 항목:
  - [ ] skill 문서에서 새 script와 registry 흐름이 설명되는지
  - [ ] hygiene script가 current candidate registry를 같이 점검하는지
  - [ ] candidate-facing 문서를 바꿀 때 registry도 같이 보라는 흐름이 문서에 드러나는지

## 4. 문서와 closeout 확인

- 확인 문서:
  - `PHASE21_CURRENT_CHAPTER_TODO.md`
  - `PHASE21_COMPLETION_SUMMARY.md`
  - `PHASE21_NEXT_PHASE_PREPARATION.md`
  - `MASTER_PHASE_ROADMAP.md`
  - `FINANCE_DOC_INDEX.md`
- 체크 항목:
  - [ ] phase 상태가 현재 구현 상태와 맞는지
  - [ ] 새 문서가 index에서 바로 찾히는지
  - [ ] 다음 단계로 넘어가기 위한 설명이 충분한지

## 한 줄 판단 기준

- 이번 checklist는
  **"이제 반복 문서 작업과 current candidate 관리가 이전보다 덜 수동적으로 가능한가"**
  를 확인하는 문서다.
