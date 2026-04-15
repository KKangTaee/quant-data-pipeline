# Phase 20 Current Chapter TODO

## 상태
- `in_progress / current_candidate_reentry_first_unit_completed`

## 1. Candidate Inventory And Bundle Organization

- `completed` phase20 kickoff plan 문서 생성
- `completed` current candidate / workflow inventory first pass
  - strongest / near-miss candidate를 다시 보는 현재 경로 정리
  - compare / weighted / saved portfolio 전환 시 불편 지점 정리
- `completed` candidate bundle surface shortlist
  - current candidate를 UI에서 다시 쓰기 위한 묶음 단위 정의
- `completed` current candidate compare re-entry first work unit
  - `Compare & Portfolio Builder` 안에서 current anchor / near-miss를 바로 compare로 다시 보내는 surface 추가
  - current candidate registry를 quick action과 custom bundle selection에 연결

## 2. Compare And Portfolio Workflow Hardening

- `in_progress` compare-to-weighted bridge friction cleanup
  - compare 결과에서 weighted portfolio builder로 이어지는 흐름 점검
- `pending` weighted result re-entry flow 정리
  - weighted portfolio 결과를 저장 / 재실행 / 다시 비교하는 흐름 정리
- `pending` saved portfolio usability hardening shortlist
  - 저장된 포트폴리오를 다시 열었을 때 다음 행동이 더 분명하게 보이도록 개선 포인트 정리

## 3. Validation

- `completed` `py_compile`
- `completed` `.venv` import smoke
- `completed` current candidate registry helper smoke
  - registry row가 compare prefill contract로 변환되는지 확인
- `pending` targeted UI validation
  - current candidate re-entry -> compare
  - compare -> weighted portfolio
  - weighted -> saved portfolio
  - saved portfolio -> rerun / load / compare re-entry

## 4. Documentation Sync

- `completed` phase20 kickoff plan 문서 생성
- `completed` phase20 current chapter TODO 문서 생성
- `in_progress` roadmap / doc index / work log / question log sync
- `completed` phase20 first work-unit 문서 생성
  - `PHASE20_CURRENT_CANDIDATE_COMPARE_REENTRY_FIRST_WORK_UNIT.md`
