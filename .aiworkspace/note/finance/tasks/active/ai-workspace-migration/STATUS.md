# STATUS - AI Workspace Migration

Status: Active
Last Updated: 2026-05-13

## Current Status

구현과 검증 완료.

완료:

- `.note/finance`를 `.aiworkspace/note/finance`로 이동
- `plugins/quant-finance-workflow`를 `.aiworkspace/plugins/quant-finance-workflow`로 이동
- 코드 / 문서 / skill의 주요 path 문자열을 새 경로로 일괄 갱신
- `.aiworkspace/README.md` 추가
- `.gitignore`의 old `.note/finance` artifact ignore를 `.aiworkspace/note/finance` 기준으로 갱신
- repo-local skill source를 global `~/.codex/skills/finance-*` mirror로 동기화
- registry JSONL 내부의 문서 경로 문자열을 새 canonical 위치로 갱신해 registry validator 통과
- Python compile, phase bootstrap dry-run, current/pre-live registry validate, skill validate 통과

커밋 전 확인:

- tracked `BACKTEST_RUN_HISTORY.jsonl`은 경로 이동만 staged이고, 로컬 내용 변경은 unstaged로 보존
- untracked `PORTFOLIO_SELECTION_SOURCES.jsonl`는 stage 제외
- `finance/.DS_Store`는 stage 제외
