# PLAN - Product Research Plugin Stage 5

Status: Active
Last Updated: 2026-05-14

## Goal

검증된 product direction research 흐름을 기존 `quant-finance-workflow` plugin 안에서 반복 가능한 workflow로 고정한다.

## 이걸 하는 이유?

1단계에서는 product research skill 초안을 만들었고, 2단계와 4단계에서는 서로 다른 주제로 실제 research run을 수행했다. 두 run 모두 `audit -> benchmark -> pattern -> feature candidates -> recommendation` 구조가 잘 작동했으므로, 이제 이 흐름을 매번 대화 기억에 의존하지 않고 plugin source 안에서 재사용할 수 있게 만들어야 한다.

5단계의 목적은 별도 product research plugin을 바로 분리하는 것이 아니다. 먼저 현재 `quant-finance-workflow` 안에 orchestration skill과 deterministic helper script를 넣어, 이후 별도 plugin으로 분리해도 흔들리지 않을 최소 운영 계약을 만든다.

## Scope

- end-to-end product research run을 안내하는 orchestration skill 추가
- research bundle skeleton을 만드는 helper script 추가
- active research bundle을 검증하는 helper script 추가
- `finance-task-intake`, plugin metadata, workspace 안내 문서에 새 workflow 반영
- repo-local skill source와 global `~/.codex/skills` mirror 동기화
- 5단계 실행 기록과 root handoff log 정리

## Out Of Scope

- 별도 product research plugin 분리
- 새 외부 벤치마크 리서치 수행
- `docs/ROADMAP.md`에 research 추천안을 승인된 개발 계획으로 승격
- `BacktestReportPack` 구현
- FastAPI / Next.js / Markdown report generator 구현

## Done Criteria

- `finance-product-research-workflow` skill이 repo-local plugin source와 global mirror에 존재한다.
- research bundle bootstrap / validation script가 dry-run 또는 validation으로 동작한다.
- 기존 두 active research bundle이 validation helper에서 fatal error 없이 확인된다.
- plugin manifest와 workspace docs가 새 workflow를 설명한다.
- `git diff --check`, JSON validation, skill quick validation, py_compile을 통과한다.
