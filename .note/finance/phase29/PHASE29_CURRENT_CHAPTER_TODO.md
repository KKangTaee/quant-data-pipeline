# Phase 29 Current Chapter TODO

## 진행 상태

- `active`

## 검증 상태

- `manual_qa_pending`

## 현재 목표

Phase 29의 목표는 백테스트 결과를 바로 투자 추천으로 확정하는 것이 아니다.
current candidate registry에 남은 후보를 검토 보드로 읽고,
필요하면 compare 또는 Pre-Live Review로 넘기는 workflow를 표준화하는 것이다.

## 1. Candidate Review Board

- `completed` `Backtest > Candidate Review` panel 추가
  - current candidate registry의 active row를 후보 검토 보드로 보여준다.
- `completed` 후보별 review stage / 존재 이유 / 다음 행동 제안 추가
  - current anchor, near miss, scenario가 왜 존재하는지 화면에서 읽게 한다.
- `completed` 후보 상세 확인과 Pre-Live Review 이동 추가
  - 선택 후보를 Pre-Live Review로 넘기되, 아직 저장 전 초안이라는 안내를 보여준다.
- `completed` Candidate Review 안에서 compare re-entry 재사용
  - 대표 후보나 near-miss 후보 묶음을 compare form으로 채울 수 있게 했다.

## 2. 다음 작업 후보

- `pending` Latest Backtest Run -> candidate review handoff 검토
  - 새 실행 결과를 후보 검토 초안으로 남길 수 있는지 검토한다.
- `pending` History record -> candidate review handoff 검토
  - 과거 실행 기록에서 후보 검토로 넘기는 흐름이 필요한지 본다.
- `pending` current candidate registry guide 보강
  - 후보 등록 / near miss / scenario 기록 기준을 더 쉽게 정리한다.

## 3. Validation

- `completed` `python3 -m py_compile app/web/pages/backtest.py`
- `completed` `python3 plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate`
- `completed` `.venv` import smoke
- `completed` finance refinement hygiene check
- `completed` `git diff --check`
- `pending` targeted manual UI validation

## 4. Documentation Sync

- `completed` phase kickoff plan 문서 생성
- `completed` current chapter TODO 문서 생성
- `completed` first work-unit 문서 생성
- `completed` roadmap / doc index / work log / question log sync
- `completed` code_analysis sync
- `completed` glossary sync
- `completed` current candidate registry guide sync

## 현재 판단

Phase 29는 active 상태다.
첫 번째 작업 단위인 `Candidate Review Board`는 구현됐고,
다음 단계는 `.note/finance/phase29/PHASE29_TEST_CHECKLIST.md` 기준 사용자 QA다.
