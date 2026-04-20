# Phase 25 Current Chapter TODO

## 상태

- `active / first_work_unit_completed`

## 현재 목표

`Phase 25`의 목표는 live trading을 여는 것이 아니다.
백테스트 결과와 Real-Money 검증 신호를 보고,
실제 돈을 넣기 전 어떤 후보를 관찰하고 보류하고 다시 볼지 기록하는
Pre-Live 운영 점검 체계를 만드는 것이다.

## 1. Pre-Live Boundary And Operating Frame

- `completed` Real-Money와 Pre-Live 경계 정의
  - Real-Money는 개별 백테스트 결과에 붙는 검증 신호다.
  - Pre-Live는 그 신호를 보고 다음 운영 행동을 기록하는 절차다.
- `completed` Phase 25 plan 문서 작성
  - Phase 25가 투자 승인 단계가 아니라 paper / watchlist / review 운영 준비 단계라는 점을 고정했다.
- `completed` first work-unit 문서 작성
  - 운영 상태와 기록 대상 필드를 먼저 정리했다.

## 2. Pre-Live Candidate Record

- `in_progress` 후보 기록 포맷 설계
  - source run, strategy, settings, Real-Money signal, blocker, next action, review date를 어떻게 남길지 정한다.
- `pending` registry / report 위치 결정
  - `CURRENT_CANDIDATE_REGISTRY.jsonl`과 별도로 둘지,
    연결 pointer만 둘지 판단한다.

## 3. Operator Review Workflow

- `pending` 상태 전환 기준 정의
  - `watchlist`, `paper_tracking`, `hold`, `reject`, `re_review`를 어떤 경우에 쓰는지 정한다.
- `pending` UI 또는 report entry point 검토
  - Backtest result에서 바로 Pre-Live 기록으로 넘길지,
    먼저 report-only workflow로 시작할지 검토한다.

## 4. Validation

- `pending` 문서 기준 QA
  - Phase 25 계획과 first work-unit이 사용자가 읽고 이해 가능한지 확인한다.
- `pending` implementation validation
  - 실제 UI나 persistence를 추가한 뒤 targeted validation을 수행한다.
- `pending` Phase 25 manual checklist handoff
  - 구현 단위가 끝나면 `PHASE25_TEST_CHECKLIST.md`를 실제 검수 항목으로 갱신한다.

## 5. Documentation Sync

- `completed` phase kickoff bundle 생성
- `completed` phase plan 문서 작성
- `completed` current chapter TODO 문서 작성
- `completed` first work-unit 문서 작성
- `completed` Phase 24 closeout 문서 sync
- `completed` roadmap / doc index / work log / question log sync
- `pending` Phase 25 구현 후 completion / next-phase 문서 갱신

## 현재 판단

Phase 25는 시작되었고,
첫 번째 작업인 `Pre-Live 경계와 운영 상태 정의`는 완료했다.

다음 작업은 실제 후보 기록 포맷과 저장 위치를 정하는 것이다.
아직 live trading이나 투자 승인 기능은 열지 않는다.
