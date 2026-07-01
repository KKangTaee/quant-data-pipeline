# Ingestion Console Structure V1 Implementation Plan

> For agentic workers: Execute sequentially. Each phase must complete development, QA, and commit before the next phase starts.

## 이걸 하는 이유?

Workspace > Ingestion 화면의 오른쪽 column에 있던 최근 수집 / 누적 실행 기록 / 로그 / failure CSV가 수집 작업 화면과 항상 함께 보여서, 사용자는 현재 해야 할 수집 작업과 실행 결과 확인 작업을 동시에 해석해야 했다. 이번 작업은 Ingestion 화면을 공용 제목 / 공용 요약 / 3개 작업 탭 구조로 바꾸고, 수집 실행과 기록 확인의 사용 목적을 분리한다.

## 전체 Roadmap

### 1차: 기록 탭 신설과 우측 column 이동

- 목적: `실행 기록 / 결과` 탭을 만들고 기존 우측 column 기능을 이 탭 안으로 옮긴다.
- 범위: `app/web/ingestion_console.py`, `tests/test_service_contracts.py`, task docs.
- 완료 조건: 세 개의 section selector가 보이고, session recent / persistent history / logs / failure CSV가 별도 탭에서 렌더된다.
- QA: Ingestion 구조 테스트, `py_compile`, `git diff --check`.

### 2차: 탭별 렌더 함수 분리

- 목적: `render_ingestion_console()`의 조건문 덩어리를 탭별 함수로 나눠 후속 수정 위험을 줄인다.
- 범위: `app/web/ingestion_console.py`, 구조 테스트.
- 완료 조건: 운영 / 수동 / 기록 탭 렌더 함수가 명시적으로 존재하고 entrypoint는 dispatch만 담당한다.
- QA: 구조 테스트, `py_compile`, `git diff --check`.

### 3차: 중복 수집 entry 정리와 공용 요약 보강

- 목적: 운영 alias와 수동 수집 alias의 관계를 화면에서 명확히 하고, 공용 영역은 수집 결과와 다음 행동 중심으로 얇게 유지한다.
- 범위: `app/web/ingestion_console.py`, 구조 테스트.
- 완료 조건: `daily_market_update` / `collect_ohlcv`, `metadata_refresh` / `collect_asset_profiles`, EDGAR 운영 refresh / raw manual collection의 차이가 화면 copy와 helper 구조로 분명해진다.
- QA: 구조 테스트, `py_compile`, `git diff --check`.

### 4차: 문서 동기화와 브라우저 QA

- 목적: durable docs와 handoff log를 새 화면 구조에 맞추고 Streamlit 화면을 실제로 확인한다.
- 범위: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`, `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`, root handoff logs, task docs.
- 완료 조건: 문서가 3탭 구조와 기록 탭을 설명하고, 브라우저 QA 스크린샷을 남긴다.
- QA: 문서/코드 diff check, Streamlit compile/import check, Browser QA.

## Verification Commands

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_collection_section_selector_is_stateful_across_reruns tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_running_jobs_preserve_section_and_show_elapsed_time tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_ui_removes_legacy_broad_collection_cards_but_keeps_compatibility_actions
.venv/bin/python -m py_compile app/web/ingestion_console.py app/services/ingestion_diagnostics.py app/jobs/ingestion_jobs.py
git diff --check
```
