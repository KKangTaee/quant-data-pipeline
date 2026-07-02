# Finance Documentation Index

Status: Active
Last Verified: 2026-07-02

## Purpose

이 폴더는 `finance` 프로젝트의 장기 지식만 보관한다.

작업 중 임시 분석, 실행 로그, 진행 상태는 `docs/`에 바로 넣지 않는다.
진행 중 기록은 `.aiworkspace/note/finance/tasks/active/<task>/`, `.aiworkspace/note/finance/phases/active/<phase>/`, 또는 제품 방향 리서치의 경우 `.aiworkspace/note/finance/researches/active/<research-id>/`에 두고,
반복적으로 필요한 내용만 이 폴더로 승격한다.

## Read First

1. [Product Direction](./PRODUCT_DIRECTION.md)
2. [Roadmap](./ROADMAP.md)
3. [Project Map](./PROJECT_MAP.md)
4. [Glossary](./GLOSSARY.md)

## Current Phase State

- Latest completed phase: [Phase 13 First-Cycle Hardening Closeout](../phases/done/phase13-hardening-cycle-closeout.md)
- Previous completed phase: [Phase 12 Selected Monitoring / Recheck Operations](../phases/done/phase12-selected-monitoring-recheck-operations.md)
- Current active phase: none. New phase work should be opened only after a user-approved scope is selected from current research / carry-forward material.
- Current active task: none.
- Latest completed task: [Backtest Handoff UI Integrated V1 2026-07-02](../tasks/active/backtest-handoff-ui-integrated-v1-20260702/STATUS.md).
- Latest completed product task: [Backtest Handoff UI Integrated V1 2026-07-02](../tasks/active/backtest-handoff-ui-integrated-v1-20260702/STATUS.md).
- Recent Overview cleanup task: [Overview Legacy Dashboard Removal V17-V24 2026-06-25](../tasks/active/overview-legacy-dashboard-removal-v17-v24-20260625/STATUS.md).
- Recent Overview helper extraction task: [Overview Tab Helper Extraction V11-V16 2026-06-25](../tasks/active/overview-tab-helper-extraction-v11-v16-20260625/STATUS.md).
- Recent Backtest strategy contract task: [Risk Parity / Dual Momentum 5B 2026-06-10](../tasks/active/risk-parity-dual-momentum-5b-20260610/STATUS.md).
- Recent Reference merge-review fix: [Merge Review Fixes 2026-06-08](../tasks/active/merge-review-fixes-20260608/STATUS.md).
- Current product state: recent merged work is grouped as Overview / Market Context, Backtest Analysis, Practical Validation / Final Review, Operations / Portfolio Monitoring, and UI / Engine Boundary. Overview primary tabs are now `Market Context`, `Market Movers`, `Futures Macro`, `Sentiment`, and `Events`, rendered as an internal text-tab underline selector; each primary tab has a thin entrypoint plus tab-local helper bridge under `app/web/overview/*_helpers.py`. `Futures Monitor` / `Sector / Industry` are not primary navigation surfaces. `Market Context` renders immediately with a light cockpit and does not default-load futures macro or historical analog validation; `Futures Macro` owns stored futures daily macro diagnosis, historical validation, tab-local daily refresh / cache reload controls, and mixed top-level scenario subtype/reason copy without becoming trade signals. See [Roadmap](./ROADMAP.md).

## By Purpose

| 목적 | 먼저 볼 문서 |
|---|---|
| 프로젝트가 무엇을 만드는지 확인 | [Product Direction](./PRODUCT_DIRECTION.md) |
| 현재 개발 순서와 active task 확인 | [Roadmap](./ROADMAP.md) |
| 코드 위치와 책임 확인 | [Project Map](./PROJECT_MAP.md) |
| 용어 의미 확인 | [Glossary](./GLOSSARY.md) |
| 시스템 구조와 layer 경계 확인 | [Architecture](./architecture/README.md) / [System Boundaries](./architecture/SYSTEM_BOUNDARIES.md) |
| 사용자 / 런타임 흐름 확인 | [Flows](./flows/README.md) |
| DB / JSONL / 저장 경계 확인 | [Data](./data/README.md) |
| 실행 / 검증 / 운영 절차 확인 | [Runbooks](./runbooks/README.md) |
| 제품 방향 / 벤치마킹 리서치 확인 | [Research](../researches/README.md) |
| backtest 결과 report 확인 | [Backtest Reports](../reports/backtests/INDEX.md) |

## Work Records

| 위치 | 역할 |
|---|---|
| `.aiworkspace/note/finance/phases/active/` | `main-dev` worktree가 관리한 phase 단위 계획과 통합 기록. 현재 완료 board도 handoff 용도로 남아 있으므로 `STATUS_MANIFEST.md`, README, roadmap의 active 표시를 함께 확인 |
| `.aiworkspace/note/finance/phases/done/` | 완료된 phase의 closeout summary. full board archive가 아니라 summary 중심 |
| `.aiworkspace/note/finance/tasks/active/` | 개별 실행 task의 계획, 진행 상태, 실행 결과. 과거 완료 task도 retained work record로 남아 있으므로 `STATUS_MANIFEST.md`, README, roadmap에서 current active 상태를 확인 |
| `.aiworkspace/note/finance/researches/active/` | 제품 방향, 벤치마킹, 기능 후보 리서치 산출물 |
| `.aiworkspace/note/finance/agent/` | Codex 반복 실수, 교훈, 운영 팁 |
| `.aiworkspace/note/finance/reports/backtests/` | 전략 탐색, 후보 근거, validation report |
| `.aiworkspace/note/finance/registries/` | 제품 workflow가 읽고 쓰는 append-only JSONL registry |
| `.aiworkspace/note/finance/saved/` | 사용자가 저장한 reusable portfolio setup |

## Documentation Rules

- `docs/`에는 오래 유지될 프로젝트 지식만 둔다.
- 작업 중 추측, 조사 메모, 실패 로그는 task 문서에 먼저 둔다.
- 제품 방향 리서치의 추측, 비교표, source note, 기능 후보는 research 문서에 먼저 둔다.
- phase는 여러 task를 묶는 상위 관리 단위다.
- task는 실제 코드나 문서를 수정하는 실행 단위다.
- `registries/`와 `saved/`의 JSONL은 제품 데이터이므로 문서 정리 과정에서 삭제하거나 재작성하지 않는다.
- backtest report는 `.aiworkspace/note/finance/reports/backtests/`에 두고, registry / saved source-of-truth와 섞지 않는다.
- run history, runtime artifact, Playwright output, temp CSV는 장기 문서가 아니다.
