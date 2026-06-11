# Overview Market Context Brief Flow V1 Plan

## 이걸 하는 이유?

`Overview > Market Context`는 핵심요약은 유용하지만, 그 아래가 `다음 확인 순서`, Deep Tab guide, Data Health 안내처럼 보여 시장 브리프를 읽는 흐름을 끊는다.
이번 1차는 사용자가 별도 가이드 섹션을 읽지 않아도 위에서 아래로 시장 움직임, 확산/집중, futures/macro 배경, 해석 전 변수만 자연스럽게 이해하게 만드는 UX 개선이다.

## 1차: Market Context를 시장 브리프로 재배치

- 목적: 기존 핵심요약은 유지하고, 하단 guide/card 구조를 브리프 행과 해석 변수 흐름으로 바꾼다.
- 변경 범위: `app/web/overview_dashboard.py`, `app/web/overview_ui_components.py`, `app/services/overview_market_intelligence.py`, 관련 focused tests.
- 완료 조건: 첫 화면이 `시장 맥락 요약 -> 시장 브리프 -> 해석할 때 같이 볼 변수 -> 자료 상태/출처 보조` 흐름으로 읽힌다.
- 이번 차수에서 하지 않는 일: Events/Data Health collector 보강, DB schema, provider 추가, 과거 유사국면/예측 기능, Operations/Backtest/Validation/Monitoring 변경.

## 후속 차수 메모

- 2차: 갱신 후 상단 context 반영 문제와 Data Health 노출 범위 재검토.
- 3차: CPI/Event coverage와 Events/Data Health 수집 보강.
- 4차: 과거 유사국면 기능은 별도 제품 기능으로 검토.
