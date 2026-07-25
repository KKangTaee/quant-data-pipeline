# Finance Canonical Docs Alignment V1 Risks

## Open Risks

### 완료 이력이 사라진 것으로 오해할 위험

- 대응: 원본 task / phase 기록을 보존하고 INDEX와 ROADMAP에서 discovery link를 제공한다.

### 문서를 줄이면서 중요한 current contract를 제거할 위험

- 대응: route, layer, storage, workflow, safety boundary별 validation checklist를 사용한다.

### active와 paused를 다시 혼동할 위험

- 대응: Roadmap에서 `Active / Paused / Verification-Only`를 별도 상태로 정의한다.

### Project Map이 다시 세부 구현 dump가 될 위험

- 대응: 중앙 지도는 entry point와 owner까지만 두고 algorithm / payload / UI history는 focused doc으로 연결한다.

### unrelated dirty worktree 파일이 포함될 위험

- 대응: exact path staging과 staged-name audit를 수행한다.

## Current Blockers

없음.

## Non-Blocking Follow-Up

- `tasks/active/`와 `phases/active/`의 retained completed board 물리 이동은 별도 승인
  범위다.
- two Verification-Only task의 actual Browser QA와 status closeout은 이번 문서
  개편이 아니라 각 owning task에서 수행한다.
