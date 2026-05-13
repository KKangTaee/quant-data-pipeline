# STATUS - Skill System Rebuild

Status: Active
Last Updated: 2026-05-13

## Current Status

1차 stale 경로 보정을 완료했다.

완료:

- `finance-backtest-web-workflow`의 first-read 경로를 새 `docs/PROJECT_MAP`, `docs/architecture`, `docs/flows` 기준으로 변경
- `finance-db-pipeline`, `finance-factor-pipeline`, `finance-strategy-implementation`의 companion document / done condition을 새 docs 구조 기준으로 변경
- `finance-doc-sync`의 canonical documents, update target, report path, roadmap / glossary 참조를 새 구조 기준으로 변경
- legacy `finance-phase-management` skill 삭제
- stale path grep에서 legacy finance 문서 경로 참조가 남지 않는 것을 확인

## Next

- 2차: workflow skill을 새로 만들지, 기존 `finance-doc-sync` 일부를 분리할지 결정
- 2차: domain skill description과 trigger overlap 정리
- 3차: 긴 SKILL.md 내용을 references로 이동
