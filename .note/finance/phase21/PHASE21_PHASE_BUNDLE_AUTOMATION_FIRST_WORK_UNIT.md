# Phase 21 Phase Bundle Automation First Work Unit

## 목적
- 새 phase를 열 때 반복적으로 만들던 문서 묶음을 script로 자동 생성한다.

## 쉽게 말하면
- 이제부터는 phase를 새로 열 때 plan, TODO, completion, next-phase, checklist를 손으로 일일이 만들지 않아도 된다.

## 이번 작업에서 한 것
- `plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py`를 추가했다.
- 이 script는 아래 문서를 한 번에 만든다.
  - phase plan
  - current TODO
  - completion summary
  - next phase preparation
  - phase test checklist
- `PHASE_PLAN_TEMPLATE.md`와 `PHASE_TEST_CHECKLIST_TEMPLATE.md`를 읽어서 기본 구조를 그대로 따른다.

## 왜 이 작업이 필요한가
- phase 문서가 많아질수록, 시작할 때 문서 뼈대를 만드는 일도 반복된다.
- 이 반복을 자동화하면:
  - 문서 구조가 더 일정해지고
  - 빠뜨리는 문서가 줄고
  - 새 phase를 열 때 속도가 빨라진다.

## 확인한 것
- `Phase 21` 문서 묶음을 실제로 이 script로 생성했다.
- `--dry-run`으로 생성 경로만 먼저 확인하는 흐름도 가능하다.

## 기대 효과
- 다음 phase부터는 kickoff 문서를 더 일관된 형식으로 빠르게 열 수 있다.
- phase 문서가 template 규칙에서 덜 벗어난다.

## 한 줄 정리
- 첫 번째 작업은 **phase 문서를 여는 반복 작업을 자동화해서, 다음 phase kickoff를 더 빠르고 일정하게 만드는 것**이다.
