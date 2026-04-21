# Phase 25 Completion Summary

## 목적

이 문서는 `Phase 25 Pre-Live Operating System And Deployment Readiness`를
closeout 시점에 정리하기 위한 문서다.

현재는 kickoff 직후의 draft다.
Phase 25가 끝나면 실제 완료 내용과 남은 blocker를 기준으로 갱신한다.

## 진행 상태

- `active`

## 검증 상태

- `not_ready_for_qa`

## 이번 phase에서 완료해야 할 것

### 1. Real-Money와 Pre-Live 경계 고정

- Real-Money는 개별 백테스트 실행의 검증 신호다.
- Pre-Live는 그 신호를 보고 paper / watchlist / hold / re-review 같은 운영 행동을 기록하는 절차다.

쉽게 말하면:

- Real-Money는 "무엇이 위험한가"를 보여주고,
  Pre-Live는 "그래서 다음에 무엇을 할 것인가"를 남긴다.

### 2. Pre-Live 후보 기록 포맷

- 후보를 관찰 대상으로 올릴 때 필요한 기록 항목을 정한다.

쉽게 말하면:

- 나중에 다시 봐도 "왜 이 후보를 보고 있었는지" 잊어버리지 않게 만든다.

현재 완료된 내용:

- `.note/finance/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`을 canonical 저장 위치로 정했다.
- `CURRENT_CANDIDATE_REGISTRY.jsonl`과는 분리하고, 필요할 때 `source_candidate_registry_id`로 연결하기로 했다.
- `manage_pre_live_candidate_registry.py` helper를 추가했다.
- `operations/PRE_LIVE_CANDIDATE_REGISTRY_GUIDE.md`를 추가했다.

### 3. Operator review workflow

- 후보를 watchlist, paper tracking, hold, reject, re-review 중 어디에 둘지 판단하는 흐름을 만든다.

쉽게 말하면:

- 좋은 백테스트 결과를 바로 실전 투입으로 착각하지 않게 중간 운영 단계를 만든다.

현재 완료된 내용:

- `draft-from-current` helper entry point를 추가했다.
- current candidate를 Pre-Live 기록 초안으로 변환할 수 있다.
- 기본값은 초안 출력이며, `--append`를 붙일 때만 실제 registry에 저장된다.
- 상태 추천 기준은 `paper_probation -> paper_tracking`, `watchlist -> watchlist`,
  blocker -> `hold`, reject/fail 계열 -> `reject`, 그 외 애매한 경우 -> `re_review`로 정리했다.

## 지금까지 완료된 것

- Phase 24를 `complete` / `manual_qa_completed`로 닫았다.
- Phase 25 plan / TODO / checklist / next-phase draft를 생성했다.
- Phase 25의 첫 작업 단위로 `Pre-Live Boundary And Operating Frame`을 정의했다.
- Real-Money 검증 신호와 Pre-Live 운영 점검의 차이를 Phase 25 문서에 반영했다.
- Phase 25의 두 번째 작업 단위로 `Pre-Live Candidate Record Contract`를 정의했다.
- Pre-Live candidate registry 저장 위치와 helper script를 추가했다.
- Phase 25의 세 번째 작업 단위로 `Operator Review Workflow`를 추가했다.
- current candidate에서 Pre-Live 운영 기록 초안을 만드는 `draft-from-current` 명령을 추가했다.

## 아직 남아 있는 것

- Backtest UI 안에서 바로 Pre-Live 초안을 만드는 버튼이나 dashboard가 필요한지 판단
- implementation 후 manual QA checklist 갱신

## closeout 판단

아직 Phase 25 closeout 상태가 아니다.
현재는 Phase 25가 시작되었고, 첫 번째 문서/운영 프레임 작업이 완료된 상태다.

쉽게 말하면:

- 이번 phase의 방향은 잡혔다.
- 후보 기록소와 helper도 생겼다.
- helper 기반 operator review workflow도 생겼다.
- 다음부터는 UI dashboard가 필요한지, 아니면 helper/report workflow로 충분한지 확인해야 한다.
