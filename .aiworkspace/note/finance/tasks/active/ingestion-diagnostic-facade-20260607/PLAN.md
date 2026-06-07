# Ingestion Diagnostic Facade 2026-06-07

Status: Completed record
Last Verified: 2026-06-07

## Purpose

7차 대형 Streamlit 파일 분해의 7B 작업이다.

7A에서 `Workspace > Ingestion` 화면을 `app/web/ingestion_console.py`로 물리 분리했지만, read-only diagnostics orchestration 일부가 여전히 Streamlit render module 안에 남아 있었다.
이번 작업은 진단 호출 경계를 Streamlit-free service facade로 옮기고, UI는 입력 / 버튼 / 세션 상태 / 표 렌더링에 집중하게 만든다.

## 이걸 하는 이유?

Ingestion 화면은 사용자가 데이터 수집 상태를 보고 수동 복구를 결정하는 중요한 운영 화면이다.
진단은 DB loader, job helper, live EDGAR sample inspection을 함께 호출하므로 렌더 파일에 직접 있으면 UI / data boundary가 흐려진다.
서비스 facade를 두면 진단 경로를 단위 테스트로 고정하고, 후속 UI 분해나 job wrapper 정리 때 호출 위치를 더 쉽게 따라갈 수 있다.

## Scope

- Create `app/services/ingestion_diagnostics.py`.
- Move read-only diagnostic orchestration behind service functions.
- Route `app/web/ingestion_console.py` diagnostic buttons and price window preflight through the service facade.
- Add boundary contract tests for the new facade.
- Update durable docs and retained task manifests.

## Not In Scope

- DB schema or collector behavior changes.
- New persistence, registry, saved setup, run-history rewrite.
- Changing diagnostic result payload shape.
- Ingestion job execution dispatch split.
- Backtest Compare Streamlit split.
- Push / PR creation.

## Completion Criteria

- `app/web/ingestion_console.py` imports `app.services.ingestion_diagnostics` for read-only diagnostics.
- `app/web/ingestion_console.py` no longer directly imports `app.jobs.diagnostics`, `finance.data.financial_statements`, `finance.loaders`, or `finance.loaders.price`.
- Existing diagnostic result renderers keep the same payload shape.
- Boundary contract tests and UI / engine boundary checker pass.
- Roadmap no longer lists Ingestion diagnostic facade as an open next decision.
