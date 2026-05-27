# UI Engine Boundary Lint Plan

Status: Complete
Created: 2026-05-20

## 이걸 하는 이유?

`ui-engine-boundary-foundation`에서 `app/services`를 Streamlit-free boundary로 만들었지만, 이 규칙을 사람이 매번 기억해서 확인하면 멀티에이전트 작업 중 다시 무너질 수 있다.

이 task는 UI / engine 분리 규칙을 repo-local helper script로 자동 확인해, 이후 service 작업 전후에 빠르게 경계 침범을 잡을 수 있게 한다.

## Scope

포함:

- `app/services`의 Streamlit import / `st.*` 사용 금지 검사
- service/runtime source의 `app.web` import hard failure 검사
- staged generated / registry / saved artifact guard 검사
- helper script runbook 등록

제외:

- CI 설정
- 기존 service import 경로 대규모 정리
- `app/web/runtime` rename / 이동
- unit test suite 추가

## Done Criteria

- helper script가 현재 main-dev 상태에서 통과한다.
- hard violation이 있으면 non-zero exit로 실패한다.
- `app.web` import는 후속 cleanup Task 9 이후 hard violation으로 실패한다.
- runbook에서 명령과 기대 결과를 찾을 수 있다.

## Later Update

2026-05-27 `ui-engine-boundary-cleanup` Task 9에서 transitional advisory 기간을 종료했다.
현재 `app.services/app.runtime -> app.web` import는 hard failure다.
