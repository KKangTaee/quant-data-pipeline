# Phase 25 Current Chapter TODO

## 진행 상태

- `complete`

## 검증 상태

- `manual_qa_completed`

## 현재 목표

`Phase 25`의 목표는 live trading을 여는 것이 아니다.
백테스트 결과와 Real-Money 검증 신호를 보고,
실제 돈을 넣기 전 어떤 후보를 관찰하고 보류하고 다시 볼지 기록하는
Pre-Live 운영 점검 체계를 만드는 것이다.

## 1. Pre-Live Boundary And Operating Frame

- `completed` Real-Money와 Pre-Live 경계 정의
  - Real-Money는 개별 백테스트 결과에 붙는 검증 신호다.
  - Pre-Live는 그 신호를 보고 다음 운영 행동을 기록하는 절차다.
  - 사용자 QA 피드백을 반영해, Pre-Live의 핵심은 상태값 자체가 아니라 `operator_reason`, `next_action`, `review_date`, `tracking_plan`을 포함한 다음 행동 기록이라고 명확히 했다.
- `completed` Phase 25 plan 문서 작성
  - Phase 25가 투자 승인 단계가 아니라 paper / watchlist / review 운영 준비 단계라는 점을 고정했다.
- `completed` first work-unit 문서 작성
  - 운영 상태와 기록 대상 필드를 먼저 정리했다.

## 2. Pre-Live Candidate Record

- `completed` 후보 기록 포맷 설계
  - source run, strategy, settings, Real-Money signal, blocker, next action, review date를 어떻게 남길지 정한다.
- `completed` registry / report 위치 결정
  - `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`을 별도 운영 기록소로 둔다.
  - `CURRENT_CANDIDATE_REGISTRY.jsonl`과는 `source_candidate_registry_id`로 연결한다.
- `completed` helper script 추가
  - `manage_pre_live_candidate_registry.py`로 template / list / show / append / validate를 지원한다.

## 3. Operator Review Workflow

- `completed` 상태 전환 기준 정의
  - `watchlist`, `paper_tracking`, `hold`, `reject`, `re_review`를 어떤 경우에 쓰는지 정한다.
- `completed` report/helper entry point 추가
  - `manage_pre_live_candidate_registry.py draft-from-current <registry_id>`로 current candidate에서 Pre-Live 기록 초안을 만든다.
  - 기본값은 출력만 하며, `--append`를 붙일 때만 실제 registry에 저장한다.
- `completed` Backtest UI entry point 추가
  - `Backtest > Pre-Live Review` 패널에서 current candidate를 선택하고 Pre-Live 기록 초안을 확인할 수 있다.
  - `Save Pre-Live Record`를 누를 때만 `.note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`에 저장된다.
  - 저장된 active Pre-Live record는 같은 패널의 registry tab에서 확인할 수 있다.

## 4. Validation

- `completed` manual QA
  - 사용자가 `PHASE25_TEST_CHECKLIST.md` 기준으로 Phase 25 Pre-Live 흐름을 검수 완료했다.
- `completed` implementation validation
  - 실제 UI나 persistence를 추가한 뒤 targeted validation을 수행한다.
- `completed` Phase 25 manual checklist handoff
  - 구현 단위가 끝나면 `PHASE25_TEST_CHECKLIST.md`를 실제 검수 항목으로 갱신한다.

## 5. Documentation Sync

- `completed` phase kickoff bundle 생성
- `completed` phase plan 문서 작성
- `completed` current chapter TODO 문서 작성
- `completed` first work-unit 문서 작성
- `completed` second work-unit 문서 작성
- `completed` Pre-Live candidate registry guide 작성
- `completed` third work-unit 문서 작성
- `completed` fourth work-unit 문서 작성
- `completed` Phase 24 closeout 문서 sync
- `completed` roadmap / doc index / work log / question log sync
- `completed` Phase 25 구현 후 completion / next-phase 문서 갱신

## 현재 판단

Phase 25는 구현과 사용자 manual QA가 모두 완료되었다.
이번 phase에서 Real-Money 검증 신호와 Pre-Live 운영 점검의 경계를 고정했고,
current candidate를 Pre-Live 기록 초안으로 바꾸는 helper와
`Backtest > Pre-Live Review` UI까지 연결했다.

아직 live trading이나 자동 투자 승인 기능은 열지 않는다.
다음 phase는 Pre-Live 기록을 실제 운영 점검에 어떻게 더 잘 활용할지,
또는 product foundation의 다음 빈틈을 어디부터 메울지 사용자와 방향을 확인한 뒤 연다.
