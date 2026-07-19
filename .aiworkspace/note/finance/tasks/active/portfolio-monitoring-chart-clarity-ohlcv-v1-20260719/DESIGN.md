# Portfolio Monitoring Chart Clarity / OHLCV V1 Design

Status: User-approved direction, written-spec review pending
Last Updated: 2026-07-19

## 이걸 하는 이유?

Portfolio Monitoring의 종합 가치곡선은 모든 관측일에 반투명 원을 그려 굵은 선 주변이
후광처럼 흐려 보인다. 또한 현재 개별 항목 상세에는 저장된 미국 주식·ETF OHLCV를
직접 확인하는 가격 차트가 없다.

이번 작업은 포트폴리오 성과 의미를 바꾸지 않고 종합 가치곡선을 선명하게 만들며,
실제 OHLCV가 존재하는 직접 미국 주식·ETF에만 라인/캔들 가격 차트를 추가한다.

## Confirmed Product Boundaries

- 종합 가치곡선은 날짜별 `total_value`이며 실제 open/high/low/volume이 아니다.
- 종합 가치곡선이나 백테스트 전략에 합성 OHLCV를 만들지 않는다.
- 실제 OHLCV는 기존 `Ingestion -> DB -> finance.loaders.price -> service -> React` 경로만 사용한다.
- 화면 진입이나 종목 선택으로 provider를 직접 호출하지 않는다.
- 주문, 자동 리밸런싱, 매수·매도 신호는 만들지 않는다.

## Alternatives Considered

### A. 종합 포트폴리오 캔들 합성

구성 종목의 일별 open/high/low를 더해 포트폴리오 캔들처럼 표시할 수 있으나, 종목별
고가와 저가는 같은 시각에 발생하지 않으며 전략 항목에는 OHLCV 자체가 없다. 실제
포트폴리오 intraday NAV로 오인될 수 있어 채택하지 않는다.

### B. 선택한 직접 종목의 실제 OHLCV 가격 차트 — 채택

종합 가치곡선은 포트폴리오 성과 라인으로 유지하고, 개별 항목 상세에서 미국 주식·ETF만
`라인 | 캔들` 전환을 제공한다. 데이터 의미가 정확하고 기존 DB-only 경계를 재사용한다.

### C. 종합 차트를 선택 종목 가격 차트로 교체

구현은 단순하지만 그룹 전체 추적 화면의 중심 질문을 잃는다. 종합 성과와 개별 가격은
동시에 필요하므로 채택하지 않는다.

## Chosen Design

### 1. 종합 가치곡선 선명도

- 평상시 모든 관측일 원은 시각적으로 숨긴다.
- hover 또는 키보드 focus 지점만 기존 active point와 tooltip으로 표시한다.
- 메인 라인, grid, hover guide는 화면 확대 시 두께가 과도하게 커지지 않도록
  non-scaling stroke를 사용한다.
- 메인 라인은 기존 파란색 계열에서 대비를 소폭 높이고, area fill은 농도를 낮춰 선을
  first-read로 만든다.
- 계산값, Y축 범위, nearest valid observation hover 계약은 변경하지 않는다.

### 2. 종합 가치곡선 날짜 눈금

- 관측 row 기준 `0% / 25% / 50% / 75% / 100%`에 가장 가까운 실제 날짜를 고른다.
- 중복 index는 제거하며 시작일과 종료일은 항상 유지한다.
- desktop/tablet은 최대 5개 날짜, `420px` 이하에서는 시작/중간/종료 최대 3개만 표시한다.
- 날짜 형식은 기존 `M월 d일`을 유지하고 첫 눈금은 start, 마지막은 end anchor를 사용한다.

### 3. 선택 항목 market-chart projection

`portfolio_monitoring_workspace_v1`에 현재 선택 항목 하나만 위한 compact projection을 추가한다.

```text
selected_item_market_chart
  status: READY | UNSUPPORTED | MISSING | ERROR
  monitoring_item_id
  source_type
  source_ref
  instrument_kind
  timeframe: 1d
  max_rows: 120
  rows: [{date, open, high, low, close, volume|null}]
  reason
```

- page는 session의 `portfolio_monitoring_selected_item_id`를 workspace builder에 전달한다.
- 선택값이 없거나 현재 그룹에 없으면 화면과 같은 규칙으로 첫 항목을 선택한다.
- read model은 선택 record와 loader callback만 조율하고 MySQL을 직접 알지 않는다.
- page runtime callback이 `load_price_history(..., timeframe="1d")`를 사용한다.
- 직접 주식·ETF는 `max(effective start, basis date - 240 calendar days)`부터 basis date까지
  DB에서 읽은 뒤 최신 120거래일로 제한한다.
- 날짜/가격이 유효한 완전한 OHLC row만 candle row로 공개한다. volume 결측은 차트 상태를
  막지 않고 거래량만 `자료 없음`으로 표시한다.
- selected strategy는 loader를 호출하지 않고 `UNSUPPORTED`와 이유를 반환한다.
- Operations landing summary에서는 선택 상세 projection을 만들지 않아 추가 DB read를 피한다.

### 4. React 개별 상세 가격 차트

- 직접 주식·ETF 상세에 `가격 차트`와 `라인 | 캔들` segmented control을 추가한다.
- 기본값은 `라인`이며 line은 같은 OHLCV row의 close를 사용한다.
- candle은 상승일 녹색, 하락일 붉은색 body와 wick을 사용하고 하단에 volume bar를 둔다.
- hover/focus tooltip은 날짜, O/H/L/C, 거래량을 표시한다.
- V1은 최신 120거래일 고정이며 zoom, pan, 기간 selector, 보조지표는 추가하지 않는다.
- 백테스트 전략 상세는 `active_group.curve`의 해당 item total-value series를 `전략 가치곡선`
  라인으로 표시하며 `전략에는 OHLCV 캔들이 없습니다`를 명시한다. disabled candle control은
  표시하지 않는다.
- `MISSING/ERROR`는 기존 가치·기여 지표를 유지한 채 가격 차트 영역에만 격리해 안내한다.

## Data Flow

```text
select_item React event
  -> Streamlit session selected_item_id
  -> portfolio monitoring workspace builder
  -> selected direct-security record
  -> load_price_history (DB-only, daily, bounded)
  -> compact selected_item_market_chart
  -> React line/candle renderer
```

그룹 가치곡선과 OHLCV 가격 차트는 서로 다른 projection을 사용한다. 어느 한쪽의 데이터
부족이나 렌더링 실패가 다른 쪽을 숨기지 않는다.

## Files Expected To Change

- `app/services/portfolio_monitoring/read_model.py`
- `app/web/final_selected_portfolio_dashboard.py`
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/contracts.ts`
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.ts`
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx`
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css`
- focused Python / Vitest tests and rebuilt `component_static`
- task/root finance closeout documentation

## Test Contract

### Python

- 직접 stock/ETF 선택은 DB loader row를 latest 120 sessions로 compact projection한다.
- selected strategy는 `UNSUPPORTED`이며 price loader를 호출하지 않는다.
- 없는 선택 id, empty OHLCV, invalid OHLC row, loader error를 각각 격리한다.
- Operations summary read는 selected item OHLCV를 추가 조회하지 않는다.

### React

- date tick helper는 시작/종료를 보존하고 5개 이하의 고유 관측 index를 반환한다.
- 정적 point는 보이지 않고 hover/focus active point는 유지된다.
- 직접 종목 READY projection에서 line/candle 전환과 OHLCV tooltip이 동작한다.
- strategy 및 missing projection은 candle을 만들지 않는다.
- desktop과 420px에서 날짜 겹침, candle/volume 가독성, 기존 hover 회귀를 확인한다.

## Tentative Delivery Roadmap

1. **1차 — 종합 차트 선명도 / 날짜 눈금**
   - 목적: 흐릿한 후광 제거와 기간 읽기 개선
   - 완료 조건: 5/3개 날짜 눈금, line/hover/focus 회귀 PASS
2. **2차 — 선택 항목 OHLCV projection**
   - 목적: DB-only 실제 가격 contract 제공
   - 완료 조건: direct security READY, strategy UNSUPPORTED, bounded/error tests PASS
3. **3차 — 개별 라인/캔들 UI**
   - 목적: 선택 직접 종목의 close line과 OHLCV/volume 탐색
   - 완료 조건: toggle/tooltip/empty-state desktop+mobile Browser QA PASS
4. **4차 — 통합 검증 / 문서 / 커밋**
   - 목적: 배포 번들과 durable task 기록 정렬
   - 완료 조건: React/Python monitoring regression, typecheck/build, QA screenshot, coherent commit

## Out Of Scope

- 종합 포트폴리오 또는 selected strategy의 합성 캔들
- intraday/minute candles
- provider 자동 수집 또는 refresh action
- 기술적 보조지표, drawing tool, zoom/pan, 기간 selector
- broker/order/rebalance 기능
