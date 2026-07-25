# Data Operations Task-Oriented IA V1

Status: Design Review
Created: 2026-07-25

## 이걸 하는 이유?

`Data > Data Operations`는 30개의 활성 수집·진단 action을 제공하지만,
사용자는 자신이 준비하려는 제품 화면보다 collector, provider, table 관계를 먼저 알아야 한다.

이번 작업은 backend 수집 자유도와 `Ingestion -> DB -> Loader -> UI` 경계를 유지하면서
Data Operations의 첫 질문을
“어떤 job을 실행할 것인가?”에서
“어느 제품 기능에 필요한 데이터를 준비할 것인가?”로 바꾼다.

근거 audit:

- `.aiworkspace/note/finance/researches/active/2026-07-data-operations-product-audit/`

## 승인된 방향

- `Task-oriented Hybrid`
- primary 화면은 consumer 목적 기반 workflow
- 저수준 action은 workflow step 또는 Advanced Data Tools에서 보존
- raw log, failure CSV, full JSON, absolute artifact path는 기본 UI에서 제거
- manual explicit action과 partial-success disclosure는 유지
- backend collector, DB schema, saved / registry JSONL은 V1에서 변경하지 않음

## 전체 Roadmap

### 1차 — 현행 제품 감사

- 목적: 현재 기능, 사용자 마찰, 제품/내부 운영 경계를 확인한다.
- 범위: docs, Ingestion code, action registry, desktop/mobile Browser QA.
- 완료 조건: 유지·통합·기본 UI 제거·추가 후보가 근거와 함께 정리된다.
- 상태: 완료.

### 2차 — Task-Oriented IA 설계

- 목적: 승인된 방향을 실제 화면 구조, action 이동표, code boundary로 확정한다.
- 범위: 이 active task의 `PLAN.md`, `DESIGN.md`, `RISKS.md`.
- 완료 조건: primary workflow, imports, recovery, history, advanced 경계와
  구현/QA stop condition을 사용자가 검토할 수 있다.
- 상태: 진행 중.

### 3차 — V1 구현과 QA

- 목적: Data Operations를 task-oriented surface로 전환한다.
- 범위:
  - `app/web/ingestion/`
  - `app/services/ingestion_diagnostics.py`
  - `app/web/streamlit_app.py`
  - 관련 tests와 finance docs
- 내부 순서:
  - 3A: page identity, default preparation surface, 상단 clutter 제거
  - 3B: consumer workflow, official import, recovery, normalized history, advanced route
  - 3C: module boundary cleanup, focused regression, 1280 / 420px Browser QA, docs sync
- 완료 조건:
  - 첫 viewport에서 실제 준비 목적을 선택할 수 있다.
  - 활성 action 30개가 primary workflow 또는 Advanced 경로에서 유실 없이 접근된다.
  - raw log / failure CSV / full JSON / absolute path가 기본 화면에 없다.
  - 기존 explicit execution, progress, partial success, run artifact backend가 보존된다.
  - relevant tests, compile, diff check, Browser QA가 통과한다.
- 상태: 사용자 설계 승인 후 시작.

### 4차 후보 — Durable Execution / Scheduling

- 목적: 10k-symbol 장기 작업의 재접속, 부분 재시도, 취소와 source별 cadence를 검토한다.
- 범위: background worker / queue, durable state, retry policy, scheduling policy.
- 완료 조건: provider rate limit, 중복 실행, atomic writer, market calendar 경계가 먼저 확정된다.
- 상태: V1 실사용 근거와 별도 승인 전에는 시작하지 않음.

## Scope

포함:

- page title / description / section IA
- action-to-workflow mapping
- action form 재사용과 low-level action demotion
- official file import 분리
- recovery diagnosis -> bounded action 흐름
- normalized data activity history
- responsive layout와 tests

제외:

- 새 provider
- DB schema 변경
- collector semantics 변경
- automatic multi-step execution
- scheduler / cron / background queue
- 새로운 raw run/job/row 상태 dashboard
- broker order, account sync, live approval, auto rebalance
- `financial_advisor`

## Stop Condition

3차 구현은 다음 조건을 모두 만족할 때 끝난다.

1. `Data Operations` identity와 default task flow가 일치한다.
2. 사용자가 네 consumer workflow와 공식 파일 / 복구 / 이력 / 고급 도구를 구분할 수 있다.
3. 기존 활성 action과 compatibility action이 유실되지 않는다.
4. 기본 화면은 raw diagnostic artifact를 노출하지 않는다.
5. data correctness caveat와 explicit execution boundary가 보존된다.
6. focused test와 desktop/mobile Browser QA가 완료된다.
