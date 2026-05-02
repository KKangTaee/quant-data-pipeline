# Phase 4 Strict Annual Final-Month Price Refresh Verification

## 목적
- `Quality Snapshot (Strict Annual)`의 `US Statement Coverage 300` 실행에서
  마지막 달에 `2026-03-17`과 `2026-03-20`이 함께 나타나던 현상이
  전략 로직 문제인지, 가격 데이터 freshness 문제인지 확인한다.

## 초기 관찰
- `Quality Snapshot (Strict Annual)`
- preset: `US Statement Coverage 300`
- 기간: `2016-01-01 ~ 2026-03-20`
- `option = month_end`

초기 결과 테이블에서는 마지막 달에 아래 두 row가 함께 보였다.
- `2026-03-17`
- `2026-03-20`

이는 large-universe strict annual 경로가 `union calendar`를 사용하기 때문에,
동일 월 안에서 종목별 마지막 사용 가능 거래일이 서로 다르면
마지막 달이 두 번 이상 보일 수 있음을 시사했다.

## 1차 확인
- 우선 사용자가 직접 확인한 마지막 선택 종목 주변에서 lagging name을 점검했다.
- 첫 확인 대상:
  - `APH`
  - `CVNA`
  - `GWW`
  - `LLY`
  - `MPWR`
- 이 다섯 종목은 당시 `finance_price.nyse_price_history` 기준으로
  마지막 가격 날짜가 `2026-03-17`에 머물러 있었다.

대조군:
- `APP`
- `KLAC`
- `LRCX`
- `NVDA`
- `UI`

위 다섯 종목은 `2026-03-20`까지 들어와 있었다.

## 1차 조치
- 대상:
  - `APH`, `CVNA`, `GWW`, `LLY`, `MPWR`
- 실행:
  - `run_daily_market_update(...)`
  - `start='2026-03-01'`
  - `end='2026-03-20'`
  - `interval='1d'`

결과:
- `status = success`
- `rows_written = 75`
- `symbols_processed = 5`
- 이 다섯 종목 모두 `2026-03-20`까지 갱신됨

## 2차 확인
- 하지만 strict annual `US Statement Coverage 300` 재실행 시
  마지막 달의 `2026-03-17` row가 여전히 남아 있었다.
- 따라서 문제는 최초 다섯 종목만의 lag가 아니라,
  preset 전체에서 더 넓게 남아 있는 stale price coverage임을 확인했다.

전체 `US Statement Coverage 300` universe를 다시 조회한 결과:
- `2026-03-17`에 멈춘 종목: `28`
- `2026-03-20`까지 있는 종목: `230`
- `2026-03-25`까지 이미 들어와 있는 종목: `42`

`2026-03-17` lagging `28` symbols:
- `CI`
- `CMI`
- `EBAY`
- `EQIX`
- `EW`
- `FANG`
- `FCX`
- `GD`
- `GEHC`
- `GEV`
- `HBAN`
- `HD`
- `HEI`
- `HLT`
- `IBM`
- `ISRG`
- `LITE`
- `LMT`
- `MAR`
- `MLM`
- `MS`
- `MSI`
- `MU`
- `PM`
- `RCL`
- `URI`
- `WMB`
- `XOM`

## 2차 조치
- 대상: 위 `28` symbols
- 실행:
  - `run_daily_market_update(...)`
  - `start='2026-03-18'`
  - `end='2026-03-20'`
  - `interval='1d'`

결과:
- `status = success`
- `rows_written = 84`
- `symbols_processed = 28`
- 이후 `US Statement Coverage 300` 기준
  `2026-03-20` 미만으로 끝나는 종목 수는 `0`

## 재검증 결과
동일 조건으로 strict annual quality를 다시 실행:
- strategy: `Quality Snapshot (Strict Annual)`
- preset: `US Statement Coverage 300`
- 기간: `2016-01-01 ~ 2026-03-20`
- `top_n = 5`
- `option = month_end`

최종 결과:
- result rows: `123`
- 마지막 row 날짜: `2026-03-20`
- 마지막 달의 `2026-03-17` row는 사라짐
- `End Balance = 192994.7`
- `CAGR = 33.9064%`
- `Sharpe Ratio = 1.33433`
- `Maximum Drawdown = -31.5606%`

마지막 5개 row:
- `2025-11-28`
- `2025-12-31`
- `2026-01-30`
- `2026-02-27`
- `2026-03-20`

## 결론
- 이번 final-month duplicate row 현상은
  strict annual ranking bug가 아니라
  `US Statement Coverage 300` 내부의 uneven latest price coverage가 직접 원인이었다.
- union-calendar snapshot 경로에서는
  large universe 일부 심볼만 최신 일별 가격이 덜 들어와 있어도
  마지막 달이 두 개 이상의 rebalance date로 보일 수 있다.
- targeted `Daily Market Update`로 lagging symbols를 따라잡게 하면
  해당 현상은 실제로 해소된다.

## 운영 메모
- strict annual wide-universe preset을 쓸 때는
  백테스트 직전 `Daily Market Update` freshness가 매우 중요하다.
- 추후 개선 후보:
  - 마지막 미완성 월을 강제로 한 row로 압축
  - 혹은 stale-price 진단 메시지를 UI에 노출
  - 혹은 preset 전체 latest date spread를 preflight로 점검
