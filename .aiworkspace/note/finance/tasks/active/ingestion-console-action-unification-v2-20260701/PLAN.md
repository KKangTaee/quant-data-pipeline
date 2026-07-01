# Ingestion Console Action Unification V2 Plan

> For agentic workers: Execute sequentially. Each phase must complete development, QA, and commit before the next phase starts.

## 이걸 하는 이유?

Ingestion 화면은 3-section 구조로 정리됐지만, 실제 실행 기능은 아직 UI section, job dispatch, 진단 카드, progress callback, run history 해석에 흩어져 있다. 이번 작업은 모든 실행 기능을 action registry로 파악 가능하게 만들고, 수집 / 진단 실행 후 화면 위치와 진행 상태를 잃지 않게 하며, 중복 entry는 역할만 다르게 유지하거나 통합한다.

## 전체 Roadmap

### 1차: action registry / 기능 inventory 코드화

- 목적: action별 section, 실행 mode, read/write 성격, target table, progress 지원 여부를 코드에서 한눈에 파악한다.
- 범위: `app/web/ingestion_console.py`, `tests/test_service_contracts.py`, task docs.
- 완료 조건: active UI action과 compatibility action이 registry에 분류되고, section 추론이 registry를 우선 사용한다.
- QA: focused unittest, `py_compile`, `git diff --check`.

### 2차: 진단 action도 공용 실행 흐름으로 통합

- 목적: read-only 진단도 `_schedule_job -> running_job -> dispatch -> result/history` 흐름을 타게 한다.
- 범위: `app/web/ingestion_console.py`, `tests/test_service_contracts.py`.
- 완료 조건: price stale / statement universe QA / coverage diagnosis / PIT inspection이 화면 고정, 경과 시간, result 저장 흐름에 들어간다.
- QA: focused unittest, `py_compile`, `git diff --check`.

### 3차: 파편화된 수집 form/helper 통합과 화면 언어 보정

- 목적: 가격 / asset profile / EDGAR 수집의 운영 entry와 수동 복구 entry를 같은 helper contract로 관리한다.
- 범위: `app/web/ingestion_console.py`, focused tests.
- 완료 조건: OHLCV params builder, asset profile job builder, EDGAR annual/quarterly label 보정이 적용된다.
- QA: focused unittest, `py_compile`, `git diff --check`.

### 4차: progress coverage 보강

- 목적: progress callback을 일부 대형 job에만 국한하지 않고, event / lifecycle / profile / futures 계열에도 최소 stage progress를 제공한다.
- 범위: `app/web/ingestion_console.py`, `app/jobs/ingestion_jobs.py`, focused tests.
- 완료 조건: 모든 active write action이 최소 `job_start` / `stage_start` / `stage_complete` / `job_complete` event를 상단 panel에 전달할 수 있다.
- QA: focused unittest, `py_compile`, `git diff --check`.

### 5차: legacy compatibility와 active UI 정리

- 목적: broad yfinance compatibility action은 active UI에 재노출하지 않고, dispatch / run-history compatibility만 명시적으로 유지한다.
- 범위: `app/web/ingestion_console.py`, `app/jobs/run_history.py`, tests.
- 완료 조건: registry에서 `compatibility=True` action은 active surface가 아니며, records/history 해석은 유지된다.
- QA: focused unittest, `py_compile`, `git diff --check`.

### 6차: docs sync와 Browser QA

- 목적: durable docs와 root handoff log를 새 action registry / progress / 진단 통합 구조에 맞춘다.
- 범위: `.aiworkspace/note/finance/docs/`, root logs, task docs.
- 완료 조건: 문서와 Browser QA가 6차 상태를 설명한다.
- QA: focused unittest, `py_compile`, `git diff --check`, Browser QA.
