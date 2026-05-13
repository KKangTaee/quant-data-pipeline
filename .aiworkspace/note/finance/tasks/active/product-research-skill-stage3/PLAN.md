# PLAN - Product Research Skill Stage 3

Status: Active
Last Updated: 2026-05-14

## Goal

2단계 실제 product research run을 복기하고, 반복 실행에서 드러난 혼동 지점을 product research 관련 skill에 반영한다.

## 이걸 하는 이유?

1단계에서는 product research skill skeleton을 만들었고, 2단계에서는 `2026-05-ui-platform-research`를 실제로 운영했다. 이제 같은 방식으로 다음 리서치를 반복하려면 산출물 위치, research와 implementation의 경계, 추천안의 승인 범위, research worktree 상태 차이를 skill이 더 명확히 안내해야 한다.

## Scope

- `finance-task-intake`가 product research run과 skill hardening task를 더 잘 구분하게 보강
- `finance-product-audit`가 user-facing product surface와 internal/ops console 구분을 audit하도록 보강
- `finance-benchmark-research`가 framework/API/UI architecture benchmark도 처리하도록 보강
- `finance-feature-opportunity`가 1차 실행 범위와 장기 roadmap 후보를 분리하도록 보강
- 관련 reference template 보강
- repo-local source와 global `~/.codex/skills` mirror 동기화

## Out Of Scope

- 새 외부 benchmark 수행
- `2026-05-ui-platform-research` 본문 재작성
- ROADMAP / PRODUCT_DIRECTION 승격
- 실제 FastAPI / Next.js 구현

## Done Criteria

- Stage 2 복기 결과가 task docs에 남는다.
- 4개 skill과 필요한 reference가 보강된다.
- global mirror가 repo-local source와 동기화된다.
- `git diff --check`와 skill path 검증을 통과한다.
