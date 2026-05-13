# STATUS - Skill System Rebuild

Status: Complete
Last Updated: 2026-05-13

## Current Status

사용자가 정의한 최종 taxonomy 기준으로 5차 보정까지 완료했다.

최종 구조는 공통 workflow skill 4개와 구현 domain skill 4개다.

완료:

- `finance-backtest-web-workflow`의 first-read 경로를 새 `docs/PROJECT_MAP`, `docs/architecture`, `docs/flows` 기준으로 변경
- `finance-db-pipeline`, `finance-factor-pipeline`, `finance-strategy-implementation`의 companion document / done condition을 새 docs 구조 기준으로 변경
- `finance-doc-sync`의 canonical documents, update target, report path, roadmap / glossary 참조를 새 구조 기준으로 변경
- legacy `finance-phase-management` skill 삭제
- stale path grep에서 legacy finance 문서 경로 참조가 남지 않는 것을 확인
- `finance-task-management`를 `finance-task-intake`로 rename하고 요청 접수 / 분류 / skill routing 역할로 좁혔다
- `finance-integration-review`를 추가해 merge conflict, worktree 통합, sub/parallel 결과 통합, staged diff 검토를 분리했다
- `finance-runbook-maintainer`를 추가해 반복 명령 / 운영 절차 / helper script 사용법의 runbook 정리를 분리했다
- domain skill description / boundary에 `finance-task-intake`와 `finance-doc-sync` 연결 역할을 반영했다
- `AGENTS.md`에 skill routing 기준 추가
- repo-local `.aiworkspace/plugins/quant-finance-workflow/skills/`를 finance skill 원본 위치로 정했다
- 8개 finance skill을 repo-local source로 정리하고 `SKILL.md` / `references/` 구조로 분리했다
- global `~/.codex/skills/finance-*`는 repo-local source와 동기화한 설치본으로 갱신했다
- repo-local `finance-backtest-candidate-refinement`는 phase worktree 공통 skill에서 제거했다
- repo-local skill의 `agents/openai.yaml` default prompt가 `$skill-name`을 명시하도록 정리했다
- `.aiworkspace/plugins/quant-finance-workflow/.codex-plugin/plugin.json`의 TODO placeholder와 존재하지 않는 hooks / MCP / app / asset 참조를 제거했다
- `.agents/plugins/marketplace.json`의 plugin source path를 실제 위치인 `./.aiworkspace/plugins/quant-finance-workflow`로 보정했다
- repo-local plugin source 8개 skill, global mirror 8개 skill, marketplace path, manifest JSON을 검증했다

## Next

- Skill System Rebuild는 완료. 다음 작업은 Practical Validation V2 P2 closeout 또는 P3 진입 여부 결정이다.
