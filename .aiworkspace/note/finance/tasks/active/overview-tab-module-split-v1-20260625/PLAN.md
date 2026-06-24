# Overview Tab Module Split V1 Plan

## 이걸 하는 이유?

`Workspace > Overview`는 UI / engine 경계가 논리적으로는 나뉘어 있지만, 탭 렌더링이 `app/web/overview_dashboard.py` 한 파일에 모여 있어 구조 파악과 후속 분리가 어렵다. 1차 작업은 동작을 바꾸지 않고 active page shell과 primary tab entrypoint를 `app/web/overview/` package로 분리해 다음 차수의 실제 helper 이동 기준점을 만든다.

## Scope

- `app/web/overview_dashboard.py`는 compatibility wrapper로 줄인다.
- 새 `app/web/overview/page.py`가 top-level title, session banner, primary tab dispatch를 소유한다.
- 새 primary tab modules가 Market Context, Market Movers, Futures Macro, Sentiment, Events entrypoint를 소유한다.
- 기존 복잡한 helper 구현은 `app/web/overview/legacy_dashboard.py`에 남겨 private helper import 계약을 보존한다.

## Out Of Scope

- 탭 내부 helper / controls / session-state 함수의 완전 이동
- `overview_ui_components.py` 분리
- `overview_market_intelligence.py` service 분리
- refresh job / read model behavior 변경
