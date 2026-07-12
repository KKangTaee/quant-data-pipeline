# Institutional Portfolios Interactive Security Chart V1 Plan

Status: Completed
Started: 2026-07-12
Completed: 2026-07-12

## 이걸 하는 이유?

사용자가 `Workspace > Institutional Portfolios`의 보유 기관 조회 차트가 단순 라인이라 hover, 구간 이동, 캔들 같은 실제 차트 탐색 기능이 부족하다고 지적했다.

이 task의 목적은 UI가 외부 fetch를 하지 않는 기존 경계를 유지하면서, 저장 가격 DB에서 내려오는 선택 종목 차트를 더 읽기 쉬운 인터랙티브 OHLCV 차트로 바꾸는 것이다.

## Scope

- `app/services/institutional_portfolios.py`: selected-security chart payload에 `open/high/low/close/volume` 포함.
- `app/web/streamlit_components/institutional_portfolios_workbench/`: React 상세 차트를 hover tooltip, crosshair, high/low dotted guides, line/candle toggle, range/pan controls로 교체.
- `tests/test_institutional_portfolios.py`: OHLCV payload와 interactive chart source contract 회귀 테스트.
- React `component_static/`: Vite build output refresh.

## Non-Goals

- 새 가격 provider 추가.
- UI에서 외부 사이트, SEC, provider 직접 fetch.
- live trading, 추천, broker action, auto rebalance 연결.
- DB schema 변경.

## Done Conditions

- 선택 종목 chart payload가 stored OHLCV field를 포함한다.
- React 차트가 라인/캔들 모드, hover tooltip/crosshair, high/low guide, range 이동을 렌더링한다.
- focused Python tests, py_compile, npm build, git diff check 통과.
- Browser QA에서 chart stage, range, dotted guides, hover tooltip/crosshair가 보인다.
