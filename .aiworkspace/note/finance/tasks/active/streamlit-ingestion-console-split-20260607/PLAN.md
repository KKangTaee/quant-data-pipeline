# Streamlit Ingestion Console Split Plan

Status: Completed
Date: 2026-06-07

## 이걸 하는 이유?

6차까지 수집 / 조회 경계를 정리했지만, `app/web/streamlit_app.py`가 Finance Console shell과 Ingestion job UI를 동시에 소유하고 있었다.
이 구조는 향후 Ingestion diagnostic facade, service/job boundary 정리, 다른 대형 Streamlit 파일 분해를 진행할 때 변경 범위를 과도하게 넓힌다.

## Scope

- 7A는 `Workspace > Ingestion` 화면의 상태 초기화, prefill, pending job promotion, job scheduling, result display, diagnostics render를 `app/web/ingestion_console.py`로 이동한다.
- `app/web/streamlit_app.py`는 top navigation, page wrapper, runtime/build indicator, glossary render만 유지한다.
- job wrapper, collector, DB schema, loader 동작은 변경하지 않는다.
- registry / saved JSONL / run history source-of-truth는 재작성하지 않는다.

## Steps

1. RED 계약 테스트를 추가해 top-level shell이 Ingestion 전용 모듈로 위임해야 함을 고정한다.
2. Ingestion 전용 상수 / 상태 / render / diagnostic helper를 새 모듈로 이동한다.
3. runtime marker / loaded-at / git sha는 shell에서 생성하고 Ingestion page render entrypoint에 주입한다.
4. `streamlit_app.py` import와 page wrapper를 얇게 정리한다.
5. docs / roadmap / project map / architecture map / root handoff log를 7차 상태로 동기화한다.
6. py_compile, service contract, boundary checker, Streamlit health, Browser QA를 수행한다.

## Done Conditions

- `app/web/streamlit_app.py`에 `_render_ingestion_console` 정의가 남아 있지 않다.
- `app/web/ingestion_console.py`가 `render_ingestion_page` public entrypoint를 제공한다.
- Ingestion page가 기존 버튼 / 결과 / diagnostics 흐름을 유지한다.
- UI / engine boundary checker가 계속 통과한다.
- Browser QA에서 `http://localhost:8501/ingestion`이 정상 표시된다.
