# Portfolio Monitoring Chart Zoom / Pan V1 Design

Status: Zoom/pan implemented; readability follow-up approved for planning
Last Updated: 2026-07-19

## 목적

Portfolio Monitoring의 선택 direct security 가격 차트는 저장된 최신 120거래일 OHLCV를
한 번에 표시한다. 데이터 의미와 DB-only 경계는 유지하면서, 관심 구간을 확대하고 좌우로
이동해 candle과 close line을 더 선명하게 읽을 수 있게 한다.

## Confirmed Scope And Boundaries

- zoom/pan은 선택한 미국 주식·ETF의 `MarketPriceChart`에만 적용한다.
- 종합 가치곡선과 selected strategy 가치곡선은 현재 동작을 유지한다.
- 기존 `selected_item_market_chart`의 최대 120개 row를 그대로 사용한다.
- 확대나 이동으로 Python rerun, DB read, provider fetch를 만들지 않는다.
- line/candle은 같은 viewport를 공유하며 같은 OHLCV row를 사용한다.
- 최소 표시 범위는 15거래일, 최대 범위는 현재 projection 전체다.
- 주문, 신호, 자동 리밸런싱 의미는 추가하지 않는다.

## Alternatives

### A. 현재 SVG에 client-side viewport 추가 — 채택

기존 React/SVG renderer에 inclusive `startIndex`와 `endIndex` 상태를 두고 표시 row만 다시
계산한다. 현재 tooltip, 색상, production bundle과 DB contract를 재사용하며 변경 범위가 가장
작다.

### B. 하단 navigator와 range handle

범위가 시각적으로 명확하지만 추가 높이를 요구해 사용자가 지적한 타이트한 화면을 더
복잡하게 만든다. V1에서는 채택하지 않는다.

### C. 전문 chart library 교체

기능은 많지만 번들, 스타일, accessibility, Streamlit component height 회귀 범위가 커진다.
120-row V1에는 과하다.

## Viewport Model

`MarketPriceChart`는 전체 `projection.rows`와 별도로 다음 inclusive window를 소유한다.

```text
viewport = { startIndex, endIndex }
visibleCount = endIndex - startIndex + 1
15 <= visibleCount <= totalRows
0 <= startIndex <= endIndex < totalRows
```

- 처음 mount와 선택 `monitoring_item_id`, row count 또는 first/last date가 변경될 때 전체 범위로
  초기화한다.
- line/candle mode 변경은 viewport를 초기화하지 않는다.
- Y축 price bounds, close path, candle width, volume bars, 날짜 눈금, hover index는 visible rows로
  다시 계산한다.
- 현재 표시 범위 밖의 값은 Y축에 포함하지 않는다. 확대 상태는 헤더의 날짜/거래일 표시와
  활성화된 `전체 보기`로 명시한다.

## Interaction Contract

### Desktop Pointer

- pointer move without press: 기존 nearest-row OHLCV tooltip을 표시한다.
- wheel: 브라우저 page scroll이 아니라 차트 viewport를 변경하고 hit area 안에서만
  `preventDefault`한다. pointer x에 대응하는 row를 anchor로 유지한다. zoom-in target은
  `round(visibleCount * 0.8)`, zoom-out target은 `round(visibleCount * 1.25)`이며 15와 전체 row
  수 사이로 clamp한다.
- pointer down 후 수평 4px 이상 이동: drag mode로 전환한다.
- drag: 이동한 pixel을 `round(deltaX / plotWidth * visibleCount)` row로 환산해 window를 좌우로
  이동하고 전체 row 경계에서 clamp한다. 화면을 오른쪽으로 끌면 이전 날짜가 보이도록 window
  index를 감소시킨다.
- drag 중에는 tooltip과 active guide를 숨긴다. pointer up/cancel 후 hover를 다시 허용한다.
- 확대되지 않은 전체 보기 상태에서는 drag가 window를 움직이지 않는다.
- double click 또는 `전체 보기`: 전체 projection으로 복귀한다.

### Explicit Controls

- `−`: zoom out
- `+`: chart center 기준 zoom in
- `전체 보기`: full range reset
- 헤더에 `M월 d일–M월 d일 · N거래일`을 표시한다.
- limit에 도달한 zoom button은 disabled 처리한다.

### Mobile

420px 이하에서는 세로 page scroll과 충돌하지 않도록 touch drag와 pinch를 지원하지 않는다.
`− / + / 전체 보기` 버튼만 사용하며 chart hit area는 기존 `touch-action: pan-y`를 유지한다.

## Pure Helper Boundary

`workbenchState.ts`가 아래 계산을 소유하고 React component는 DOM event를 index/pixel 입력으로
변환하는 역할만 맡는다.

- full viewport 생성과 normalization
- cursor/center anchor zoom
- pixel delta 기반 horizontal pan
- visible row slicing과 viewport state 비교

helper는 invalid total, min-window > total, boundary anchor, 과도한 pan delta도 항상 유효한
viewport로 clamp한다.

## Rendering And Accessibility

- 차트 hit area는 idle에서 crosshair, drag 가능 상태에서 grab, drag 중 grabbing cursor를 사용한다.
- controls는 `button`과 명확한 Korean `aria-label`을 사용한다.
- 차트는 기존 keyboard focus tooltip을 유지한다. V1에서 keyboard pan shortcut은 추가하지 않는다.
- line/candle toggle, tooltip content, up/down color, volume-null semantics는 변경하지 않는다.

## Error And Recovery

- projection이 `READY`가 아니거나 row가 부족하면 기존 localized state를 유지하고 controls를
  표시하지 않는다.
- projection row 수, first/last date 또는 selected item이 바뀌면 stale viewport를 full range로
  reset한다.
- pointer capture를 잃거나 component 밖에서 release되면 drag state를 종료한다.
- zoom/pan 계산 실패가 전체 workspace를 숨기지 않도록 pure helper가 full normalized window로
  fallback한다.

## Files Expected To Change

- `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.ts`
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.test.ts`
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx`
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css`
- `app/web/streamlit_components/portfolio_monitoring_workbench/component_static/`
- `tests/test_portfolio_monitoring_component.py`
- task/root/canonical closeout documents

Python services, DB schema, market-chart projection과 Operations summary read는 변경하지 않는다.

## Test Contract

### Unit

- full viewport와 minimum 15-session clamp
- cursor left/center/right anchor zoom
- repeated zoom in/out와 edge clamp
- positive/negative pixel drag와 full-range no-op
- selection/row-count reset 조건
- visible rows를 기준으로 nearest tooltip index 계산

### Component Contract

- zoom/pan controls와 pointer/wheel handlers가 production source에 포함된다.
- mobile button-only policy와 `touch-action: pan-y`가 유지된다.
- line/candle mode가 viewport state를 공유한다.

### Browser QA

- desktop: pointer-centered wheel zoom, drag pan, drag 중 tooltip suppression, hover recovery,
  double-click/reset, line/candle viewport 유지
- 420px: buttons로 zoom/reset, page vertical scroll 유지, horizontal overflow 0
- 기존 group value hover, drawer, selected strategy value-only 동작 회귀 없음

## Delivery Roadmap

1. **1차 — Viewport 계산**
   - pure helper와 경계 TDD
   - 완료 조건: anchor, min/max, pan clamp tests PASS
2. **2차 — Interaction UI**
   - wheel, drag, controls, range label, cursor state와 production rebuild
   - 완료 조건: React/component contract tests, typecheck/build PASS
3. **3차 — 통합 QA와 문서**
   - Portfolio Monitoring regression과 desktop/420px Browser QA
   - 완료 조건: hover/drag/reset/overflow 확인, QA screenshot, durable docs와 coherent commits

## Approved Readability Follow-up

### 문제와 원인

- 선택 종목 가격 차트의 Y축 가격, `VOL`, X축 날짜는 SVG user-space 기준 `9px`라
  실제 카드 너비로 축소될 때 화면상 크기가 더 작아진다.
- 데스크톱 `pm-content-grid`가 종목·전략 목록과 선택 상세를 약 `56:44`로 배분해,
  사용자의 핵심 분석 대상인 가격 차트보다 선택용 목록이 더 넓다.

### 채택안

- 데스크톱에서 종목·전략 목록과 선택 상세를 나란히 유지하되 열 비율을 `35:65`로 바꾼다.
- 선택 상세 열은 현재 최소 폭을 유지하고, 목록 열도 종목명·현재 가치·기여 손익을 읽을 수 있는
  최소 폭 아래로 줄이지 않는다.
- 선택 가격 차트의 Y축 가격, `VOL`, X축 날짜를 `11px`로 올리고 색 대비와 font weight를
  한 단계 보강한다.
- tooltip 글자와 전체 Portfolio Monitoring 타이포그래피는 이번 후속 범위에서 변경하지 않는다.
- `900px` 이하의 기존 단일 열 전환은 유지해 모바일과 좁은 화면의 가로 overflow를 만들지 않는다.

### 검토한 대안

- **전체 너비 세로 배치:** 차트는 가장 넓어지지만 목록을 선택한 뒤 상세까지 이동 거리가 길어져
  데스크톱의 빠른 종목 비교 흐름이 약해진다.
- **목록 접기/펼치기:** 필요할 때 최대 차트 폭을 얻을 수 있지만 새로운 상태와 컨트롤이 생겨
  이번 가독성 보정 범위보다 복잡하다.

### 변경 후 사용자 흐름

사용자는 왼쪽의 좁아진 종목·전략 목록에서 항목을 선택하고, 같은 행의 넓어진 상세 영역에서
KPI와 가격 차트를 읽는다. 화면이 900px 이하가 되면 목록 다음에 상세가 이어지는 기존 단일 열로
전환된다. 데이터 조회, 선택 상태, zoom/pan viewport와 line/candle 전환은 바뀌지 않는다.

### 구현 및 검증 경계

- 주 변경 파일: `src/style.css`
- React markup이나 data contract는 변경하지 않는다.
- static source contract에서 desktop `35:65`, axis/date `11px`, `900px` 단일 열 계약을 고정한다.
- React test, TypeScript typecheck, production build와 Portfolio Monitoring Python 회귀를 실행한다.
- Browser QA에서는 desktop 목록/상세 실제 폭, 축 가독성, 기존 wheel/drag/tooltip과 420px overflow를 확인한다.

## Explicit Non-Goals

- 전체 history 재조회와 user-defined date picker
- 종합/전략 차트 확대
- 모바일 pinch/touch pan
- vertical pan, price-axis manual scale, chart drawing
- 기술적 보조지표와 alert
