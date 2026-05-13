# PLAN - Product Research Output Contract

Status: Active
Last Updated: 2026-05-13

## Goal

제품 방향 리서치 산출물의 canonical 위치를 `.aiworkspace/note/finance/researches/`로 정리하고, 관련 스킬과 문서 라우팅을 맞춘다.

## 이걸 하는 이유?

`tasks/active/`는 스킬 개발, 문서 정리, 코드 구현 같은 실행 작업 기록에는 적합하지만, 실제 제품 방향 리서치의 본문 산출물을 담기에는 역할이 섞인다. 2단계 리서치를 시작하기 전에 `researches/active/<research-id>/`를 명확한 조사 작업장으로 정해야 이후 audit, benchmark, feature opportunity 결과가 task 로그와 섞이지 않는다.

## Scope

- `.aiworkspace/note/finance/researches/active/`, `done/` 구조 추가
- `AGENTS.md`, docs index, project map에 research 역할 반영
- `finance-product-audit`, `finance-benchmark-research`, `finance-feature-opportunity` output contract 수정
- `finance-task-intake`가 제품 방향 리서치를 research folder로 라우팅하게 수정
- global `~/.codex/skills` mirror 동기화

## Out Of Scope

- 실제 외부 리서치 수행
- 첫 research run 생성
- ROADMAP 기능 우선순위 변경
- plugin 분리 패키징

## Done Criteria

- 실제 리서치 산출물은 `researches/active/<research-id>/`에 둔다는 규칙이 문서화된다.
- 관련 스킬들이 task folder보다 research folder를 우선 출력 위치로 안내한다.
- skill validation과 diff 검증을 통과한다.
