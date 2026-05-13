# RISKS - Skill System Rebuild

Status: Active
Last Updated: 2026-05-13

## Risks

| Risk | Status | Mitigation |
|---|---|---|
| 이미 로드된 세션에는 삭제된 `finance-phase-management` metadata가 남을 수 있음 | accepted | 다음 세션부터 skill inventory가 갱신된다 |
| global `~/.codex/skills` 변경은 repo commit에 포함되지 않음 | mitigated | repo-local `plugins/quant-finance-workflow/skills/`를 원본으로 만들고 global은 mirror로 동기화 |
| 새 `finance-task-management` skill은 현재 세션 skill inventory에 즉시 표시되지 않을 수 있음 | accepted | 다음 세션부터 trigger 확인, 4차에서 실제 routing 점검 |
| `finance-doc-sync`가 아직 길고 많은 역할을 들고 있음 | mitigated | 3차에서 update matrix를 `references/doc-sync-matrix.md`로 분리 |
| repo-local plugin은 여전히 draft placeholder가 남아 있음 | open | 4차에서 plugin 정리 |
