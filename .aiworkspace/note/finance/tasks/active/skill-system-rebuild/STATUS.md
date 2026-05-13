# STATUS - Skill System Rebuild

Status: Active
Last Updated: 2026-05-13

## Current Status

3차 SKILL.md 슬림화와 references 분리를 완료했다.

완료:

- `finance-backtest-web-workflow`의 first-read 경로를 새 `docs/PROJECT_MAP`, `docs/architecture`, `docs/flows` 기준으로 변경
- `finance-db-pipeline`, `finance-factor-pipeline`, `finance-strategy-implementation`의 companion document / done condition을 새 docs 구조 기준으로 변경
- `finance-doc-sync`의 canonical documents, update target, report path, roadmap / glossary 참조를 새 구조 기준으로 변경
- legacy `finance-phase-management` skill 삭제
- stale path grep에서 legacy finance 문서 경로 참조가 남지 않는 것을 확인
- 새 `finance-task-management` skill 생성
- domain skill description / boundary에 `finance-task-management`와 `finance-doc-sync` 연결 역할 반영
- `AGENTS.md`에 skill routing 기준 추가
- repo-local `.aiworkspace/plugins/quant-finance-workflow/skills/`를 finance skill 원본 위치로 정했다
- 6개 finance skill을 repo-local source로 추가하고 `SKILL.md` / `references/` 구조로 분리했다
- global `~/.codex/skills/finance-*`는 repo-local source와 동기화한 설치본으로 갱신했다

## Next

- 4차: plugin placeholder 정리와 실제 trigger 점검
