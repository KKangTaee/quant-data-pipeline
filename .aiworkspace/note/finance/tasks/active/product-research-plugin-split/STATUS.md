# STATUS - Product Research Plugin Split

Status: Complete
Last Updated: 2026-05-14

## Current Status

완료. product research 관련 source를 별도 plugin으로 이동하고, 문서/marketplace 경계를 갱신했다.

## Completed

- 사용자의 요청을 plugin boundary split 작업으로 분류했다.
- `finance-task-intake`, `plugin-creator`, `skill-creator` 지침을 확인했다.
- 새 plugin 이름을 `quant-finance-product-research`로 정했다.
- product research 관련 4개 skill과 helper script 2개를 새 plugin 아래로 이동했다.
- 새 plugin manifest와 marketplace entry를 추가했다.
- 기존 `quant-finance-workflow` plugin manifest에서 product research 설명을 제거했다.
- `AGENTS.md`, `.aiworkspace/README.md`, `docs/ROADMAP.md`에 새 plugin 경계를 반영했다.
- repo-local source와 global `~/.codex/skills` mirror 정합성을 확인했다.
- skill quick validation, script py_compile, bootstrap dry-run, active research bundle check, plugin JSON validation, `git diff --check`를 통과했다.

## Next

- product research 관련 후속 작업은 `.aiworkspace/plugins/quant-finance-product-research/`를 source-of-truth로 사용한다.
