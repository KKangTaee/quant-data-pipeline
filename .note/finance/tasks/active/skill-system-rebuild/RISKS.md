# RISKS - Skill System Rebuild

Status: Active
Last Updated: 2026-05-13

## Risks

| Risk | Status | Mitigation |
|---|---|---|
| 이미 로드된 세션에는 삭제된 `finance-phase-management` metadata가 남을 수 있음 | accepted | 다음 세션부터 skill inventory가 갱신된다 |
| global `~/.codex/skills` 변경은 repo commit에 포함되지 않음 | open | 변경 내용은 task 문서와 최종 응답에 명시한다 |
| `finance-doc-sync`가 아직 길고 많은 역할을 들고 있음 | open | 3차에서 references 분리 |
| repo-local plugin은 여전히 draft placeholder가 남아 있음 | open | 4차에서 plugin 정리 |
