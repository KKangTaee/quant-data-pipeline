# Ingestion Manual Job State And Elapsed Time V1 Plan

## 이걸 하는 이유?

사용자가 `수동 복구 / 진단 > 상세 재무제표 수동 수집 > 상세 재무제표 수동 수집 실행`을 누른 뒤 화면이 처음 Ingestion 진입처럼 돌아가는 문제를 보고했다. 수집 실행은 Streamlit rerun을 동반하므로, 사용자가 선택한 수동 섹션과 실행 중 context를 session state에 명시적으로 보존해야 한다.

## Scope

- `app/web/ingestion_console.py`의 수집 작업 섹션 선택 UX를 stateful selector로 변경한다.
- manual job scheduling 시 선택 섹션과 UI 시작 시각을 job state에 저장한다.
- 실행 중 banner / progress caption에 경과 시간을 표시한다.
- 관련 boundary contract test를 추가한다.
- 실제 EDGAR 수집 실행은 QA에서 누르지 않는다. 데이터 부작용 없이 화면 동작과 코드 경로를 검증한다.

## Out Of Scope

- EDGAR provider / collector 로직 변경.
- DB schema 변경 또는 table drop.
- run history / registry / saved JSONL 정리.
- 새 provider 또는 paid provider 추가.

## Completion Criteria

- 수동 섹션을 선택하면 manual 작업 목록이 표시되고 operational expanded body는 보이지 않는다.
- manual collection job 예약 시 rerun 후에도 수동 섹션으로 복귀할 수 있는 state를 갖는다.
- running banner / supported progress callback caption이 elapsed time을 노출한다.
- focused tests, py_compile, `git diff --check`, Browser QA를 통과한다.
