# NOTES - AI Workspace Migration

Status: Active
Last Updated: 2026-05-13

## Decisions

- `.aiworkspace/`를 AI / Codex 작업 문서와 도구의 top-level workspace로 둔다.
- 기존 `.note/finance`는 `.aiworkspace/note/finance`로 이동한다.
- 기존 `plugins/quant-finance-workflow`는 `.aiworkspace/plugins/quant-finance-workflow`로 이동한다.
- `~/.codex/skills/finance-*`는 repo-local skill source의 mirror / 설치본으로 유지한다.

## Dirty Artifact Handling

- 이동 전 `.note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`에 로컬 수정이 있었다.
- 커밋에는 경로 이동만 들어가도록 임시로 clean 상태를 이동하고, 로컬 수정본은 새 위치인 `.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`에 다시 적용했다.
- 따라서 최종 커밋 후에도 해당 run history 변경분은 unstaged local artifact로 남아야 한다.
