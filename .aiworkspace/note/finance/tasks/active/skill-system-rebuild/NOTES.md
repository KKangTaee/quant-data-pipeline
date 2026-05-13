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
- 새 `finance-task-management`는 active task 문서 규칙과 domain skill routing을 담당한다.
- domain skill은 각 코드 영역의 구현 규칙을 유지하고, task 운영은 새 workflow skill로 넘긴다.

## 3차 판단

- 프로젝트 전용 skill을 `~/.codex/skills`에만 두면 커밋 / 리뷰 / 다른 worktree 재현이 어렵다.
- 따라서 repo-local `.aiworkspace/plugins/quant-finance-workflow/skills/`를 원본으로 두고, `~/.codex/skills/finance-*`는 설치본처럼 동기화하는 구조가 맞다.
- `SKILL.md`는 Codex가 처음 읽는 entry point라 짧아야 하며, domain rule과 긴 ownership 목록은 `references/`로 보내는 것이 맞다.
- 3차에서는 plugin을 완전히 publish-ready로 만들지는 않았다. 남은 placeholder와 실제 trigger 검증은 4차 범위다.
