# STATUS - Product Research Output Contract

Status: Complete
Last Updated: 2026-05-13

## Current Status

완료.

## Completed

- 사용자 피드백을 반영해 실제 리서치 산출물은 `tasks/active`가 아니라 `researches/active`에 두는 방향으로 확정했다.
- `.aiworkspace/note/finance/researches/README.md`, `active/`, `done/` 구조를 추가했다.
- `AGENTS.md`, docs index, roadmap, project map에 product direction research 위치를 반영했다.
- `finance-task-intake`와 3개 product research skill의 output contract를 `researches/active/<research-id>/` 기준으로 수정했다.
- global `~/.codex/skills` mirror를 동기화했다.
- 4개 스킬 quick validation과 `git diff --check`를 통과했다.
- 사용자 피드백에 따라 폴더명을 `research/`에서 `researches/`로 rename하고 모든 경로 참조를 정리했다.

## Next

- 2단계 실제 리서치 run을 시작할 때 `researches/active/<research-id>/`에 research bundle을 생성한다.
