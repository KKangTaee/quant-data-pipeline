# PLAN - Product Research Skill Stage 1

Status: Active
Last Updated: 2026-05-13

## Goal

퀀트 프로젝트의 다음 개발 방향을 찾기 위한 리서치 workflow의 1단계 스킬을 만든다.

## 이걸 하는 이유?

현재 `finance` 프로젝트는 Backtest, Practical Validation, Final Review, Selected Dashboard의 기본 흐름이 잡혀 있다. 다음 단계에서는 즉흥적으로 기능을 추가하기보다, 현재 제품의 약점, 외부 유사 서비스의 기능 패턴, 추가 기능 후보의 근거와 우선순위를 분리해서 조사할 수 있어야 한다.

## Scope

- `finance-product-audit` 스킬 추가
- `finance-benchmark-research` 스킬 추가
- `finance-feature-opportunity` 스킬 추가
- 각 스킬의 최소 reference와 `agents/openai.yaml` 추가
- repo-local plugin manifest와 global skill mirror 정합성 확인

## Out Of Scope

- 실제 외부 벤치마킹 리서치 수행
- ROADMAP 직접 수정
- phase 생성
- 별도 product research plugin 패키징

## Done Criteria

- 3개 스킬이 repo-local source에 생성된다.
- 각 스킬이 산출물, 읽기 순서, 경계, 후속 handoff를 명시한다.
- global `~/.codex/skills` mirror가 생성된다.
- validation 명령과 git diff 검토를 완료한다.
