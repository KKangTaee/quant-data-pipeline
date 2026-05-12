# RISKS - Finance Documentation System Rebuild

Status: Active
Last Updated: 2026-05-12

## P1 - 중요한 과거 맥락 손실

Risk:

- 기존 문서 tree를 삭제하면 phase별 세부 결정이 바로 보이지 않을 수 있다.

Mitigation:

- 새 `docs/`에는 현재 작업 재개에 필요한 핵심만 승격한다.
- 삭제된 세부 문서는 Git history에서 복구할 수 있다는 전제로 진행한다.
- 대량 삭제는 1차 작업 이후 사용자 확인을 받고 진행한다.

## P1 - AGENTS.md와 새 구조 불일치

Risk:

- 새 docs 구조를 만들었지만 `AGENTS.md`가 기존 경로를 계속 가리키면 다음 Codex 세션이 혼란스러울 수 있다.

Mitigation:

- 2차 작업에서 `AGENTS.md`를 새 read order 기준으로 축약한다.
- 1차 작업 final response에서 아직 `AGENTS.md`가 구 구조를 가리킨다는 점을 명시한다.

## P2 - 기존 phase 문서와 새 phase skeleton 혼재

Risk:

- 1차 작업 후에는 `phases/phase*/`와 `phases/active/`가 동시에 존재한다.

Mitigation:

- 이는 의도적인 중간 상태다.
- 3차 작업에서 기존 phase tree 삭제 또는 summary migration을 수행한다.

## P2 - Runtime artifact가 계속 dirty로 남음

Risk:

- `run_history`, `.DS_Store`, `.playwright-mcp/`가 git status에 계속 보일 수 있다.

Mitigation:

- 이번 1차 커밋에는 새 문서만 stage한다.
- runtime/generated artifact는 커밋하지 않는다.
