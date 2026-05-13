# NOTES - Skill System Rebuild

Status: Active
Last Updated: 2026-05-13

## Notion Guide Interpretation

확인한 핵심 방향:

- 처음부터 plugin을 크게 만들지 않는다.
- 반복되는 작업 방식을 먼저 skill로 만들고, 실제로 안정되면 plugin으로 승격한다.
- skill은 `SKILL.md`, `references/`, `scripts/`로 분리한다.
- `SKILL.md`는 긴 프로젝트 문서를 복사하는 곳이 아니라 progressive disclosure entry point다.

## 1차 판단

- 현재 문제는 skill 설계 자체보다 stale 경로가 더 급하다.
- 그래서 1차에서는 skill을 새로 만들지 않고 기존 skill이 새 docs 구조를 읽게 보정했다.
- `finance-phase-management`는 새 운영 구조와 맞지 않으므로 삭제했다.

## 2차 판단

- workflow skill은 `finance-doc-sync`와 분리하는 편이 맞다.
- 이유: task 생성 / 진행 상태 / root handoff log 운영은 작업 시작과 진행 중의 문제이고, `finance-doc-sync`는 작업 후반의 alignment 문제다.
- 초기 2차 설계에서는 새 `finance-task-management`가 active task 문서 규칙과 domain skill routing을 담당하게 했다.
- domain skill은 각 코드 영역의 구현 규칙을 유지하고, task 운영은 새 workflow skill로 넘긴다.

## 3차 판단

- 프로젝트 전용 skill을 `~/.codex/skills`에만 두면 커밋 / 리뷰 / 다른 worktree 재현이 어렵다.
- 따라서 repo-local `.aiworkspace/plugins/quant-finance-workflow/skills/`를 원본으로 두고, `~/.codex/skills/finance-*`는 설치본처럼 동기화하는 구조가 맞다.
- `SKILL.md`는 Codex가 처음 읽는 entry point라 짧아야 하며, domain rule과 긴 ownership 목록은 `references/`로 보내는 것이 맞다.
- 3차에서는 plugin을 완전히 publish-ready로 만들지는 않았다. 남은 placeholder와 실제 trigger 검증은 4차 범위다.
- AI workspace 이동 이후에는 repo-local plugin에만 남아 있는 skill도 함께 점검해야 한다. `finance-backtest-candidate-refinement`는 현재 runtime mirror에는 설치하지 않지만, repo-local source에 남아 있는 한 stale phase wording을 유지하면 다음 plugin 정리 때 혼선을 만든다.
- candidate refinement skill은 phase raw report 중심이 아니라 registry-backed candidate state, strategy hub/log, backtest report, root handoff log를 연결하는 bounded refinement skill로 해석한다.

## 4차 판단

- `quant-finance-workflow` plugin은 공개 배포용 package가 아니라 repo-local AI workspace bundle이다.
- 따라서 존재하지 않는 homepage / repository / icon / screenshots / hooks / MCP / app placeholder를 유지하지 않는다. 실제 존재하는 `skills/`와 helper `scripts/`를 설명하는 manifest만 둔다.
- `plugin-creator`의 기본 marketplace convention은 `./plugins/<plugin-name>`이지만, 이 프로젝트는 사용자가 `.aiworkspace/plugins/`를 canonical 위치로 확정했다. 그래서 `.agents/plugins/marketplace.json`은 실제 존재하는 `./.aiworkspace/plugins/quant-finance-workflow`를 가리키게 한다.
- 현재 세션에서 skill inventory 자체를 새로고침할 수는 없으므로, trigger 점검은 global mirror metadata 확인과 `quick_validate.py`, marketplace path 검증으로 판단한다.

## 5차 보정 판단

- 사용자가 원한 구조는 명확히 4개 workflow skill과 4개 implementation domain skill이다.
- `finance-task-management`라는 이름은 active task 운영까지 직접 소유하는 느낌이 강하므로, 요청 접수 / 분류 / 라우팅 중심의 `finance-task-intake`가 더 정확하다.
- `finance-doc-sync`는 문서 alignment만 담당해야 하며, 통합 검토와 반복 절차 문서화는 각각 `finance-integration-review`, `finance-runbook-maintainer`로 분리한다.
- `finance-backtest-candidate-refinement`는 candidate-search worktree 성격과 겹치므로 phase worktree의 공통 skill bundle에서는 제거한다.
