# Market Movers Period Refresh And Chart Fix V1 Design

Status: Approved
Last Updated: 2026-07-21

## 이걸 하는 이유?

비-Daily Market Movers는 현재 S&P 500 구성종목이 최신이어도 가격 이력 커버리지가 오래된 날짜에 묶이면 Weekly/Monthly 랭킹 기준일이 함께 멈춘다. 현재 DB에서는 S&P 500 503종목 중 225종목의 마지막 일봉이 `2026-07-07`이고, `2026-07-15` 이후 가격이 있는 종목은 coverage 임계치에 못 미쳐 Weekly/Monthly 랭킹 기준일이 `2026-07-07`로 결정된다.

또한 `limited_price_history`로 한 번 분류된 신규 상장 종목은 목표일이 진행해도 다시 확인하지 않아, 선택 기간을 채울 수 있게 된 이후에도 랭킹에서 계속 제외될 수 있다. 화면에서는 실행 중 Streamlit 서버가 최신 번들보다 먼저 시작되고 자동 reload가 꺼진 상태라 가격 이력 갱신 대신 유니버스 기준 갱신만 실행된 흔적도 확인됐다.

차트에서는 재무 tooltip이 위쪽 값에서 scroll viewport의 `overflow-y: hidden` 경계를 넘어 잘리고, 가격·모멘텀 차트 X축은 시작일과 종료일만 보여 중간 시점을 판독하기 어렵다.

## 승인된 정책

### 1. 비-Daily 가격 갱신 window

- 갱신 목표일은 `latest_completed_nyse_session()`이 반환하는 최신 완료 NYSE 거래일이다.
- Weekly의 필수 수익률 구간은 목표일 이전 1주이며, 그 앞 1주를 overlap으로 추가한다.
  - 예: 목표일이 `2026-07-20`이면 대략 `2026-07-07`부터 `2026-07-20`까지를 요청한다.
- Monthly의 필수 수익률 구간은 목표일 이전 1개월이며, 그 앞 1개월을 overlap으로 추가한다.
  - 예: 목표일이 `2026-07-20`이면 대략 `2026-05-20`부터 `2026-07-20`까지를 요청한다.
- provider의 exclusive end 계약은 job 경계에서 한 번만 보정한다. preflight와 provider adapter가 각각 하루를 더하지 않도록 날짜 의미를 단일화한다.
- 기존 가격 행을 전부 다시 받지 않는다. stale, missing, 재확인이 필요한 limited-history 종목만 bounded window로 보강하고 기존 UPSERT 경로를 유지한다.

### 2. 신규 상장 및 짧은 가격 이력

- 선택 기간 시작점 이전 또는 그 시점에 유효 가격이 없으면 해당 기간 랭킹에서 제외한다.
- 상장 이후 수익률을 Weekly/Monthly 전체 기간 수익률처럼 다른 종목과 섞지 않는다.
- 화면에는 `신규 상장 · 선택 기간 이력 부족`처럼 제외 사유를 표시한다.
- 제외 상태여도 최신 가격 이력 수집은 계속한다.
- `limited_price_history`는 영구 제외 표식이 아니다. 저장된 최신일 또는 issue 확인일이 현재 목표일보다 오래됐거나, 상장 후 시간이 지나 선택 기간을 채울 가능성이 생기면 bounded retry 대상에 포함한다.
- 랭킹 가능 여부는 단순 누적 row 수 `10/45`가 아니라 다음 경계 충족 여부를 우선한다.
  - 선택 기간 시작점 또는 그 이전의 유효 가격 존재
  - 목표일에 충분히 가까운 최신 유효 가격 존재
  - 두 경계 사이에 수익률을 계산할 수 있는 유효 가격 존재
- HONA는 2026-06-29 신규 상장 종목이므로 Weekly 경계를 채우면 Weekly에는 포함할 수 있지만, Monthly 시작 경계를 채우지 못하면 Monthly에서는 제외한다.
- FDXF는 2026-06-01 신규 상장 종목이므로 현재 Monthly 시작 경계를 충족하는 가격이 확보되면 기존 `45 rows` 미달만으로 제외하지 않는다.

## 갱신 흐름

1. 화면이 최신 완료 시장일과 저장 가격의 종목별 최신일을 읽는다.
2. Weekly/Monthly 선택 기간과 overlap을 사용해 공통 bounded window를 만든다.
3. 종목을 `current`, `stale`, `missing`, `limited-retry`, `period-ineligible`로 분류한다.
4. `stale`, `missing`, `limited-retry`만 기존 `run_collect_ohlcv` 경로로 수집한다.
5. 수집 후 freshness와 기간 경계를 다시 계산한다.
6. 선택 기간을 충족하지 못한 신규 상장 종목은 명시적 사유와 함께 랭킹에서 제외한다.
7. coverage 임계치를 만족하는 가장 최신일로 Market Movers snapshot을 다시 생성한다.
8. 화면에는 `최근 완료 시장일`, `랭킹 데이터 기준`, `마지막 수동 갱신`을 서로 다른 의미로 유지한다.

## 액션 및 실행 상태

- `가격 이력 수동 갱신`과 `유니버스 기준 갱신`은 별도 버튼과 action id를 유지한다.
- 비-Daily의 주 액션은 가격 이력 수동 갱신이다. 유니버스 기준 갱신은 구성종목 자체가 오래됐을 때 사용하는 보조 액션이다.
- 별도의 운영 진단 패널은 추가하지 않는다.
- 실행 중에는 해당 버튼을 잠그고 짧은 inline 진행 문구만 표시한다. 완료 후 snapshot과 timing을 다시 읽는다.
- 최신 React bundle과 Python helper가 함께 로드되도록 QA 전에 Streamlit 서버를 재시작한다.

## 차트 UI

### 재무 tooltip

- tooltip은 기본적으로 데이터 지점 위에 표시한다.
- 지점이 상단 안전영역에 들어오면 tooltip을 지점 아래로 자동 전환한다.
- 좌우 끝에서는 tooltip 중심을 viewport 안쪽으로 제한한다.
- 가로 drag/scroll과 hover/focus/keyboard 탐색은 기존 동작을 유지한다.

### 가격·모멘텀 X축

- 실제 저장 거래일을 기준으로 중간 tick을 배치한다.
- `1M`: 약 1주 간격
- `3M`: 약 1개월 간격
- `6M`: 약 1개월 간격
- `1Y`: 약 2개월 간격
- 첫 날짜와 마지막 날짜는 항상 유지하고, 좁은 화면에서는 겹치는 중간 tick을 줄인다.
- hover/focus tooltip은 축의 축약 라벨과 무관하게 정확한 `YYYY-MM-DD`와 해당 값·수익률을 표시한다.

### 가격·모멘텀 선택 기간 readout 후속 보정

- `1M / 3M / 6M / 1Y`는 YTD 정규화 값을 자르는 방식이 아니라 선택 구간의 첫 유효 거래일 가격을 `0%`로 다시 기준화한다.
- 우측 첫 지표 이름도 `YTD 수익률`에 고정하지 않고 현재 선택값에 맞춰 `1M 수익률`처럼 바뀐다.
- 최근 값, 범위 최고, 범위 최저는 같은 선택 구간에서 계산한다.
- 서버는 기존 YTD 수익률 계약을 보존하면서 별도 raw `price_series`에 최근 1년 조정주가를 제공한다.
- 달력 월말 이동은 3월 31일의 1개월 전을 2월 말로 clamp해 3월 초로 넘치지 않게 한다.

## 오류 및 경계 처리

- provider가 한 종목에 대해 빈 응답을 주면 기존 DB 행을 삭제하지 않는다.
- 일부 종목 실패는 성공 종목의 저장을 유지하고 실패 종목만 다음 retry 대상으로 남긴다.
- 휴일과 주말 때문에 단순 calendar day 수가 부족해지지 않도록 ranking eligibility는 실제 저장 거래일 경계로 판정한다.
- 최신 상장 종목의 과거 값을 기존 모회사 가격이나 synthetic series로 자동 연결하지 않는다.
- ticker change는 active alias 또는 lifecycle 근거가 있을 때만 별도 resolver 경로를 사용한다.

## 예상 변경 범위

- `app/jobs/overview_actions.py`
- `app/services/overview/market_movers.py`
- `app/web/overview/market_movers_helpers.py`
- `app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx`
- `app/web/streamlit_components/market_movers_workbench/src/style.css`
- 관련 Market Movers service/UI tests
- React `component_static/` production build
- task 및 durable finance 문서

## 검증 계약

- Weekly/Monthly preflight가 최신 완료 시장일과 승인된 overlap window를 사용한다.
- 503종목 중 이미 최신인 종목은 수집 대상에서 제외된다.
- 오래된 limited-history issue는 bounded retry 대상이 된다.
- HONA는 Weekly 경계 확보 여부에 따라 포함되고 Monthly 경계가 없으면 명시적으로 제외된다.
- FDXF는 Monthly 양쪽 경계를 확보하면 누적 45행 미만이어도 기간 수익률 계산 대상이 된다.
- 갱신 후 coverage-qualified 랭킹 기준일이 실제 저장 커버리지에 따라 전진한다.
- 재무 tooltip은 상단·좌측·우측 지점에서 잘리지 않는다.
- 가격 X축은 모든 기간 선택에서 중간 tick과 정확한 hover 날짜를 제공한다.
- Python focused tests, React tests/build, `git diff --check`를 통과한다.
- 최신 서버 재시작 후 desktop/narrow Browser QA를 수행하고 스크린샷 1장을 확보한다.

## Tradeoff

bounded overlap은 전체 universe 장기 이력을 매번 다시 받는 방식보다 빠르고 provider 부하가 작다. 대신 period eligibility와 limited retry 상태를 명시적으로 관리해야 한다. 신규 상장 종목을 기간 랭킹에서 제외하면 표시 종목 수는 줄 수 있지만, 서로 다른 관측 기간의 수익률을 같은 랭킹에 섞는 왜곡을 피할 수 있다.

## Non-goals

- 신규 상장 종목의 상장 이후 수익률을 별도 랭킹으로 만드는 작업
- 모회사와 분사 기업 가격 이력의 synthetic backfill
- 실시간 또는 broker-grade 시세 전환
- 별도 운영 진단 dashboard 추가
