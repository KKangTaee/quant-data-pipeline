# RISKS - AI Workspace Migration

Status: Active
Last Updated: 2026-05-13

| Risk | Status | Mitigation |
|---|---|---|
| 경로 참조 수가 많아 stale path가 남을 수 있음 | mitigated | active code/docs old path grep 통과 |
| JSONL registry / run history 내용 변경이 커밋에 섞일 수 있음 | mitigated | registry path 문자열은 migration 범위로 갱신, run history local artifact는 stage 제외 |
| global skill mirror가 repo-local source와 어긋날 수 있음 | mitigated | repo-local skill을 `~/.codex/skills`로 재동기화하고 양쪽 validate |
| helper scripts가 새 plugin 위치를 못 찾을 수 있음 | mitigated | py_compile, phase bootstrap dry-run, registry validate 통과 |
