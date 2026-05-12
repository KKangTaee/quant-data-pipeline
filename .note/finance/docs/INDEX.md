# Finance Documentation Index

Status: Active
Last Verified: 2026-05-12

## Purpose

이 폴더는 `finance` 프로젝트의 장기 지식만 보관한다.

작업 중 임시 분석, 실행 로그, 진행 상태는 `docs/`에 바로 넣지 않는다.
진행 중 기록은 `.note/finance/tasks/active/<task>/` 또는 `.note/finance/phases/active/<phase>/`에 두고,
반복적으로 필요한 내용만 이 폴더로 승격한다.

## Read First

1. [Product Direction](./PRODUCT_DIRECTION.md)
2. [Roadmap](./ROADMAP.md)
3. [Project Map](./PROJECT_MAP.md)
4. [Glossary](./GLOSSARY.md)

## By Purpose

| 목적 | 먼저 볼 문서 |
|---|---|
| 프로젝트가 무엇을 만드는지 확인 | [Product Direction](./PRODUCT_DIRECTION.md) |
| 현재 개발 순서와 active task 확인 | [Roadmap](./ROADMAP.md) |
| 코드 위치와 책임 확인 | [Project Map](./PROJECT_MAP.md) |
| 용어 의미 확인 | [Glossary](./GLOSSARY.md) |
| 시스템 구조 확인 | [Architecture](./architecture/README.md) |
| 사용자 / 런타임 흐름 확인 | [Flows](./flows/README.md) |
| DB / JSONL / 저장 경계 확인 | [Data](./data/README.md) |
| 실행 / 검증 / 운영 절차 확인 | [Runbooks](./runbooks/README.md) |
| backtest 결과 report 확인 | [Backtest Reports](../reports/backtests/INDEX.md) |

## Work Records

| 위치 | 역할 |
|---|---|
| `.note/finance/phases/active/` | Main phase worktree가 관리하는 phase 단위 계획과 통합 기록 |
| `.note/finance/tasks/active/` | 개별 실행 task의 계획, 진행 상태, 실행 결과 |
| `.note/finance/agent/` | Codex 반복 실수, 교훈, 운영 팁 |
| `.note/finance/reports/backtests/` | 전략 탐색, 후보 근거, validation report |
| `.note/finance/registries/` | 제품 workflow가 읽고 쓰는 append-only JSONL registry |
| `.note/finance/saved/` | 사용자가 저장한 reusable portfolio setup |

## Documentation Rules

- `docs/`에는 오래 유지될 프로젝트 지식만 둔다.
- 작업 중 추측, 조사 메모, 실패 로그는 task 문서에 먼저 둔다.
- phase는 여러 task를 묶는 상위 관리 단위다.
- task는 실제 코드나 문서를 수정하는 실행 단위다.
- `registries/`와 `saved/`의 JSONL은 제품 데이터이므로 문서 정리 과정에서 삭제하거나 재작성하지 않는다.
- backtest report는 `.note/finance/reports/backtests/`에 두고, registry / saved source-of-truth와 섞지 않는다.
- run history, runtime artifact, Playwright output, temp CSV는 장기 문서가 아니다.
