# Finance Canonical Docs Alignment V1 Design

Status: Approved Direction / Written Spec Review
Last Updated: 2026-07-26

## Goal

사람과 AI가 root README 다음에 finance canonical docs를 읽을 때 다음 질문에
순서대로 답을 얻도록 한다.

1. 이 문서 체계에서 어디부터 읽어야 하는가?
2. 이 제품은 왜 존재하고 사용자는 무엇을 끝낼 수 있는가?
3. 지금 구현은 어디에 있고 각 계층은 무엇을 소유하는가?
4. 현재 어디까지 왔고 다음에는 무엇을 결정해야 하는가?

## Diagnosis

### INDEX

- 189줄 중 `Current Phase State`가 약 130줄이다.
- task 링크 124개, `Latest / Previous / Current` 상태 표현 106개다.
- local link 143개는 모두 유효하지만 index가 완료 작업 changelog 역할을 겸한다.
- `Portfolio Lab`은 누락되고 오래된 navigation 표현이 남아 있다.
- 장기 지식만 둔다는 자체 규칙과 rolling task snapshot이 충돌한다.

### PRODUCT_DIRECTION

- 76줄로 짧지만 `Workspace / Operations / Backtest / Reference` 기반의 옛
  navigation 표현이 13곳 남아 있다.
- 현재 `Today`, `Institutional Holdings`, `Portfolio Lab`, `Data Operations`,
  `Reference Center`의 제품 가치가 일관된 사용자 흐름으로 정리되지 않았다.
- product purpose와 특정 시점의 구현 완료 목록이 섞여 있다.

### PROJECT_MAP

- 288줄 안에 entry point, layer ownership, 세부 도메인 계약과 화면별 최근 UX
  변경이 함께 들어 있다.
- current path는 대체로 정확하지만, 중앙 지도에서 읽기에는 domain-specific
  설명이 길어 architecture / flow / data 문서와 책임이 겹친다.
- 처음 읽는 개발자가 “어디부터 볼지”보다 개별 구현 세부사항을 먼저 만나게 된다.

### ROADMAP

- 1,291줄, 완료 표현 163개, task 링크 182개, 옛 navigation 표현 75개다.
- 실제 `Next Decisions`는 문서 1,222줄 이후에 나온다.
- 완료 task changelog가 현재 상태와 미래 결정보다 훨씬 크다.
- Sentiment task는 자체 상태에서 다음 차수가 보류됐지만 current active로 표시된다.
- 일부 Browser QA-only follow-up은 현재 사용할 수 있는 in-app Browser 환경과
  상태가 맞지 않는다.

## Chosen Approach

사용자가 승인한 `A · 역할 분리형 전면 정리`를 적용한다.

- 완료 이력은 삭제하지 않는다.
- 상세 구현과 QA 근거는 기존 task / phase / root handoff에 보존한다.
- canonical 문서는 현재 사실, 안정된 경계, 다음 결정만 요약한다.
- 네 문서가 서로의 본문을 복제하지 않고 책임 문서로 연결한다.

## Document Responsibilities

### INDEX.md — 어디서 무엇을 읽을지

`INDEX.md`는 문서 시스템의 stable router다.

권장 구조:

1. Purpose
2. Start Here
3. Reading Paths
4. Canonical Docs By Concern
5. Current Work Pointers
6. Workspace Boundaries
7. Maintenance Rules

규칙:

- 완료 task 목록을 복제하지 않는다.
- current work는 `ROADMAP`, active task index와 state manifest 링크만 제공한다.
- current 7개 화면을 장황하게 설명하지 않고 Product Direction으로 연결한다.
- 60~100줄을 목표로 하되 정보 손실보다 역할 명확성을 우선한다.

### PRODUCT_DIRECTION.md — 왜 만들고 무엇을 제공하는지

제품의 안정적인 목적과 사용자 가치를 소유한다.

권장 구조:

1. Product Promise
2. Who It Is For
3. User Journey
4. Current Product Surfaces
5. Product Principles
6. Safety / Non-Goals
7. Current Maturity And Known Limits

규칙:

- `Research / Portfolio / Data / Help`와 7개 surface를 current contract로 사용한다.
- Practical Validation과 Final Review는 Portfolio Lab 내부 stage로 설명한다.
- task 이름, commit, 최근 UI polish와 단기 상태를 넣지 않는다.
- 파일 경로와 세부 implementation ownership은 Project Map으로 넘긴다.

### PROJECT_MAP.md — 어디에 무엇이 구현되어 있는지

현재 code / runtime / storage / UI ownership의 빠른 지도를 소유한다.

권장 구조:

1. System At A Glance
2. Layer Ownership
3. Product Surface Entry Points
4. Workflow Ownership
5. Data And Storage Boundaries
6. Where To Start By Change Type
7. Detailed Documentation

규칙:

- surface별 entry point는 route adapter, service, React workbench 수준까지만 적는다.
- 한 화면의 UX 변경 이력, 긴 payload 필드와 algorithm detail은 제거한다.
- 경제사이클·13F·Portfolio Monitoring 같은 상세 계약은 architecture / flow / data
  문서로 연결한다.
- 문서에 표시하는 code path는 실제 존재해야 한다.

### ROADMAP.md — 지금 어디까지 왔고 다음에 무엇을 결정할지

현재 product baseline, 실제 open state와 미래 승인 후보를 소유한다.

권장 구조:

1. Current Snapshot
2. Implemented Baseline
3. Active / Paused / Verification-Only Work
4. Next Decision Queue
5. Recommended Order
6. Completion / Approval Rules
7. Work Model And Update Rules

규칙:

- 완료 task별 changelog를 제거한다.
- 구현 기반은 제품 축별 한 줄 또는 compact table로 요약한다.
- active, paused, verification-only를 구분한다.
- 승인 전 후보와 이미 구현된 사실을 섞지 않는다.
- 상세 history는 task / phase / root handoff로 연결한다.
- 120~220줄을 목표로 하되 decision context를 충분히 보존한다.

## Canonical Reading Flow

### 제품을 이해하는 사람

```text
README
  -> INDEX
  -> PRODUCT_DIRECTION
  -> ROADMAP
  -> 필요한 flow / data / runbook
```

### 구현을 시작하는 개발자 또는 AI

```text
AGENTS
  -> INDEX
  -> ROADMAP
  -> PROJECT_MAP
  -> owning architecture / flow / data doc
  -> active task
```

`INDEX`는 두 경로의 공통 router이며, `ROADMAP`은 history archive가 아니라 current
decision surface다.

## Current-State Source Priority

문서 간 충돌이 있으면 다음 순서로 current fact를 판정한다.

1. 실제 route / code ownership
2. current surface의 focused architecture / flow / data 문서
3. active task의 `STATUS.md`
4. root handoff summary
5. 과거 완료 task와 phase 기록

과거 task에만 존재하고 current code 또는 focused durable doc과 충돌하는 표현은
historical context로 남기고 canonical 문서에는 승격하지 않는다.

## Information Preservation

- `ROADMAP`과 `INDEX`에서 제거되는 완료 작업 목록은 원본 task / phase 폴더에
  그대로 남는다.
- root handoff는 최근 milestone 위치를 제공하고 상세 history를 복제하지 않는다.
- 물리적 archive 이동이나 과거 link repair는 이번 범위에 포함하지 않는다.
- registry / saved / run history와 generated QA artifact는 건드리지 않는다.

## Validation

### Structural

- 네 문서의 local Markdown link가 모두 존재한다.
- Markdown fence가 균형을 이룬다.
- INDEX와 ROADMAP에 대량 완료 task 목록이 다시 생기지 않는다.

### Current Product Contract

- `app/web/streamlit_app.py`의 navigation group과 7개 `st.Page` title이
  Product Direction / Project Map과 일치한다.
- 옛 `Workspace >`, `Operations >`, `Backtest >`, `Reference >` user-facing
  navigation 표현이 네 문서에 남지 않는다.

### Ownership

- Project Map의 주요 local code / doc path가 실제로 존재한다.
- data flow는 `Ingestion -> DB -> Loader / Service -> Runtime -> UI`를 유지한다.
- React가 provider / DB / canonical decision persistence를 소유한다고 쓰지 않는다.

### State

- Roadmap의 active / paused / verification-only 표기가 각 task `STATUS.md`와
  모순되지 않는다.
- 완료 task detail은 canonical docs가 아니라 task / phase 기록에서 찾게 한다.

## Important Trade-Offs

- 문서 길이를 줄이면 한 파일에서 모든 과거를 검색하기는 어려워진다. 대신 현재
  판단 속도와 drift 저항성이 높아지고, 상세 근거는 task 기록에서 계속 찾을 수 있다.
- Project Map에서 세부 계약을 제거하면 중앙 문서만으로 모든 구현을 알 수 없지만,
  책임별 focused 문서와 code path로 이동하는 흐름이 선명해진다.
- Roadmap에 active task 이름을 많이 나열하지 않으면 즉시성은 줄지만, paused와
  completed를 active로 오인하는 문제를 줄일 수 있다.

## Scope Boundary

이번 개편은 documentation architecture와 current-state alignment만 바꾼다.
제품 behavior, UI, provider, DB, strategy, validation, registry / saved contract는
변경하지 않는다.
