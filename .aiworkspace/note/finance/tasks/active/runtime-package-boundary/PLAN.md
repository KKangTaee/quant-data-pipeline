# Runtime Package Boundary Plan

Status: Complete
Created: 2026-05-20

## 이걸 하는 이유?

`app/web/runtime`는 이름상 UI 하위 모듈처럼 보이지만 실제로는 DB-backed backtest runtime wrapper와 JSONL repository helper를 함께 가진 Streamlit-free runtime layer다.
서비스가 `app.web.runtime`을 import하면 UI와 engine 분리 관점에서 경계가 흐려진다.

## Task 5 Scope

`app/web/runtime` 위치 / 이름을 정리해, UI가 아닌 runtime 책임을 `app/runtime`으로 승격한다.

## Subtasks

### 5-01. Runtime package 이동

- `app/web/runtime/*.py`를 `app/runtime/*.py`로 이동한다.
- repo 내부 import를 `app.web.runtime`에서 `app.runtime`으로 전환한다.
- 동작, schema, JSONL path, registry write policy는 바꾸지 않는다.

### 5-02. Candidate Library replay helper 이동

- `app/web/backtest_candidate_library_helpers.py`를 `app/runtime/candidate_library.py`로 이동한다.
- Selected Portfolio Dashboard runtime이 web helper를 import하지 않게 한다.
- Candidate Library 화면은 새 runtime helper를 import해 기존 UI 동작을 유지한다.

## Non-Scope

- runtime wrapper 내부의 5천 줄 backtest dispatch refactor
- JSONL registry schema 변경
- FastAPI / React / Next.js 도입
- Streamlit 화면 UX 변경

## Completion Criteria

- `app/web/runtime` Python package가 남지 않는다.
- repo 내부 Python import가 `app.runtime`을 사용한다.
- `app/services`와 `app/runtime`은 Streamlit을 import하지 않는다.
- boundary lint가 `app/services`와 `app/runtime`을 함께 검사한다.
