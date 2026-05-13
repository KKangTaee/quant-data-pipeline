# RISKS - Skill System Rebuild

Status: Active
Last Updated: 2026-05-13

## Risks

| Risk | Status | Mitigation |
|---|---|---|
| 이미 로드된 세션에는 삭제된 `finance-phase-management` metadata가 남을 수 있음 | accepted | 다음 세션부터 skill inventory가 갱신된다 |
| global `~/.codex/skills` 변경은 repo commit에 포함되지 않음 | accepted | repo에는 `AGENTS.md`와 task 문서로 변경 의도를 기록한다 |
| 새 `finance-task-management` skill은 현재 세션 skill inventory에 즉시 표시되지 않을 수 있음 | accepted | 다음 세션부터 trigger 확인, 4차에서 실제 routing 점검 |
| `finance-doc-sync`가 아직 길고 많은 역할을 들고 있음 | open | 3차에서 references 분리 |
| repo-local plugin은 여전히 draft placeholder가 남아 있음 | open | 4차에서 plugin 정리 |
