# Post-Merge Active State Cleanup 2026-06-07

Status: Active
Last Updated: 2026-06-07

## 이걸 하는 이유?

1차는 병합 후 제품 흐름을 정리했고, 2차는 UI / service / runtime / loader / DB / storage 경계를 정리했다.
3차는 `.aiworkspace/note/finance/tasks/active/`와 `.aiworkspace/note/finance/phases/active/`에 남아 있는 완료 기록이 실제 active work처럼 보이는 문제를 줄인다.

현재 폴더 구조에는 과거 worktree에서 완료한 task / phase board가 handoff와 추적용으로 많이 남아 있다.
한 번에 모두 `done/`으로 이동하면 과거 root log, phase closeout, task reference link가 깨질 수 있으므로, 이번 작업은 물리 이동보다 active-state manifest와 README 정렬을 우선한다.

## Scope

- `tasks/active`와 `phases/active`의 현재 수량과 의미를 조사한다.
- current active task / phase가 없다는 상태를 README, roadmap, index, root handoff에 맞춘다.
- `tasks/active/STATUS_MANIFEST.md`와 `phases/active/STATUS_MANIFEST.md`를 추가해 retained record 해석 규칙을 둔다.
- `tasks/done/README.md`와 `phases/done/README.md`에 현재 done 폴더의 역할을 명확히 한다.

## Out Of Scope

- 170개 task 폴더 대량 이동
- 11개 phase board 대량 이동
- registry / saved JSONL rewrite
- `.note/` legacy/local artifact 삭제 또는 stage
- 코드 / UI / DB 동작 변경
- 새로운 phase opening

## Completion Criteria

- 현재 active task / phase가 none이라는 상태가 index / roadmap / README / root handoff에서 일치한다.
- `tasks/active`와 `phases/active`에 남은 폴더가 retained work record임을 manifest가 설명한다.
- physical archive migration은 다음 승인 후보로 남기고, 이번 3차 완료를 전체 cleanup 완료처럼 과장하지 않는다.
- docs-only 검증을 실행하고 결과를 `RUNS.md`에 기록한다.
