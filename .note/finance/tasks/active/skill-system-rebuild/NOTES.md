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
