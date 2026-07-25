# Finance Documentation Index

Status: Active
Last Verified: 2026-07-26

## Purpose

이 폴더는 `finance` 패키지와 Finance Console의 오래 유지될 제품·구조·데이터·운영
지식을 보관한다.

현재 작업의 진행 상황, 실험 메모와 실행 로그는 task·phase·research 기록에 두고,
반복해서 필요한 결론만 `docs/`로 승격한다. 이 문서는 상세 내용을 복제하지 않고
사람과 AI를 올바른 책임 문서로 안내한다.

## Start Here

1. [Product Direction](./PRODUCT_DIRECTION.md) — 제품이 해결하는 문제와 사용자 흐름
2. [Roadmap](./ROADMAP.md) — 현재 구현 기준선, 열린 상태와 다음 승인 결정
3. [Project Map](./PROJECT_MAP.md) — 화면·계층·저장소의 code ownership
4. [Glossary](./GLOSSARY.md) — 제품과 검증 용어

처음 실행하거나 전체 제품을 빠르게 보고 싶다면 root
[README](../../../../README.md)부터 읽는다. 저장소에서 작업하는 AI와 개발자는
[AGENTS.md](../../../../AGENTS.md)의 범위·검증·기록 규칙을 함께 따른다.

## Reading Paths

### 제품과 사용자 흐름을 이해할 때

```text
README
  -> Product Direction
  -> Roadmap
  -> 필요한 flows / data 문서
```

### 코드 변경 위치를 찾을 때

```text
AGENTS
  -> Project Map
  -> owning architecture / flow / data 문서
  -> active task
  -> Roadmap (baseline / state / priority가 관련될 때)
```

### 실행·수집·QA 절차를 찾을 때

```text
Runbooks
  -> 관련 architecture / data 문서
  -> owning job / service / UI entry point
```

## Canonical Docs By Concern

| 알고 싶은 것 | Canonical entry |
|---|---|
| 제품 목적, 대상 사용자, 사용자 여정과 non-goal | [Product Direction](./PRODUCT_DIRECTION.md) |
| 현재 상태, paused work와 다음 결정 순서 | [Roadmap](./ROADMAP.md) |
| 화면 entry point, layer와 code ownership | [Project Map](./PROJECT_MAP.md) |
| system / UI-engine / storage 경계 | [Architecture](./architecture/README.md), [System Boundaries](./architecture/SYSTEM_BOUNDARIES.md) |
| Today부터 Portfolio Monitoring까지 사용자·runtime 흐름 | [Flows](./flows/README.md) |
| DB schema, table 의미와 JSONL 저장 정책 | [Data](./data/README.md) |
| 반복 실행, ingestion, QA와 복구 절차 | [Runbooks](./runbooks/README.md) |
| 제품 용어와 검증 상태 의미 | [Glossary](./GLOSSARY.md) |
| 전략·후보·validation의 사람이 읽는 결과 | [Backtest Reports](../reports/backtests/INDEX.md) |
| 제품 방향·벤치마킹·기능 후보 조사 | [Research Workspace](../researches/README.md) |

현재 Finance Console의 top-level 제품 surface는 `Research / Portfolio / Data / Help`
아래 `Today / Market Research / Institutional Holdings / Portfolio Lab /
Portfolio Monitoring / Data Operations / Reference Center`다. 각 화면의 가치와
경계는 Product Direction, 구현 위치는 Project Map에서 확인한다.

## Current Work Pointers

- 제품 기준선과 다음 승인 후보: [Roadmap](./ROADMAP.md)
- 현재와 retained task 기록: [Active Task Index](../tasks/active/README.md)
- task 상태의 compact pointer: [Task Status Manifest](../tasks/active/STATUS_MANIFEST.md)
- phase 상태의 compact pointer: [Phase Status Manifest](../phases/active/STATUS_MANIFEST.md)

작업·phase 기록 폴더에는 과거 완료 board도 보존되어 있다. 폴더 위치만으로 현재
진행 중이라고 판단하지 않고 Roadmap과 해당 `STATUS.md`를 함께 확인한다.

## Workspace Boundaries

| 위치 | 역할 |
|---|---|
| `docs/` | 오래 유지될 제품·구조·데이터·운영 지식 |
| `tasks/active/` | 개별 구현·문서·QA task의 계획과 실행 기록 |
| `phases/active/` | 사용자가 승인한 multi-task phase의 통합 기록 |
| `researches/active/` | 제품 방향, 벤치마킹과 기능 후보 리서치 |
| `reports/backtests/` | 사람이 읽는 전략·실행·후보·validation report |
| `agent/` | 반복 실수, 교훈과 Codex 운영 팁 |
| `registries/` | 제품 workflow가 읽고 쓰는 append-only JSONL |
| `saved/` | 사용자가 저장한 reusable portfolio setup |
| `run_history/`, `run_artifacts/` | local runtime 기록과 generated artifact |

## Maintenance Rules

- INDEX에는 개별 완료 task 목록이나 최근 변경 로그를 복제하지 않는다.
- 구현된 사실과 미래 계획을 같은 문장에 섞지 않는다.
- 제품 목적이 바뀌면 Product Direction, code ownership이 바뀌면 Project Map,
  우선순위·상태가 바뀌면 Roadmap을 수정한다.
- 상세 algorithm, payload, table과 실행 절차는 각각 architecture, flow, data,
  runbook 문서가 소유한다.
- `registries/`와 `saved/`는 문서 정리 대상으로 삭제하거나 재작성하지 않는다.
- 임시 분석, 실패 로그, QA 출력과 local run history는 durable docs에 넣지 않는다.
