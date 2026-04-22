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

- `completed` Latest Backtest Run -> candidate review handoff
  - 새 실행 결과를 후보 검토 초안으로 보낼 수 있게 했다.
- `completed` History record -> candidate review handoff
  - 과거 실행 기록에서 후보 검토 초안으로 넘기는 버튼을 추가했다.
- `completed` Candidate Intake Draft -> Candidate Review Note 저장
  - 후보 검토 초안을 current candidate registry에 바로 넣지 않고,
    별도 review note로 operator decision / reason / next action을 남길 수 있게 했다.
- `completed` current candidate registry guide 보강
  - 후보 등록 / near miss / scenario 기록 기준을 더 쉽게 정리한다.
- `pending` candidate review note -> current candidate registry 등록 기준 정리
  - review note 중 어떤 경우에 실제 후보 registry row로 남길지 후속 기준을 정한다.

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
- `completed` second work-unit 문서 생성
- `completed` third work-unit 문서 생성
- `completed` roadmap / doc index / work log / question log sync
- `completed` code_analysis sync
- `completed` glossary sync
- `completed` current candidate registry guide sync

## 현재 판단

Phase 29는 active 상태다.
첫 번째 작업 단위인 `Candidate Review Board`와
두 번째 작업 단위인 `Result To Candidate Review Handoff`,
세 번째 작업 단위인 `Candidate Review Note`는 구현됐다.
다음 단계는 `.note/finance/phase29/PHASE29_TEST_CHECKLIST.md` 기준 사용자 QA다.
