# Phase 3 OHLCV Storage Decision

## 목적
이 문서는 stock과 ETF OHLCV를
어떤 테이블 구조로 관리할지에 대한 결정을 기록한다.

---

## 결론

stock과 ETF OHLCV는
동일한 `finance_price.nyse_price_history` 테이블에 함께 저장하는 것이 맞다.

즉:
- stock 전용 price table
- ETF 전용 price table

로 분리하지 않는다.

---

## 이유

1. price schema가 동일하다
   - `symbol`, `timeframe`, `date`, `open`, `high`, `low`, `close`, `adj_close`, `volume`, `dividends`, `stock_splits`

2. loader / backtest / strategy 계층에서
   stock과 ETF를 함께 다루는 경우가 많다

3. 하나의 사실 테이블로 유지해야
   조회 경로가 단순해진다

4. 자산 종류 구분은
   `finance_meta.nyse_stock`, `finance_meta.nyse_etf`, `nyse_asset_profile`
   에서 해석하면 된다

---

## 비채택 대안

### stock / ETF 분리 price table

채택하지 않은 이유:
- loader가 불필요하게 복잡해진다
- mixed portfolio 백테스트가 번거로워진다
- 동일 스키마 테이블을 중복 운영하게 된다

---

## 보완 메모

현재 단계에서는
`nyse_price_history`에 `asset_kind` 컬럼을 추가하지 않는다.

이유:
- 메타 테이블에 이미 같은 정보가 존재한다
- 중복 저장보다 symbol source / metadata join으로 해석하는 편이 낫다

---

## 결론 요약

OHLCV 저장 구조는
"하나의 price fact table + 별도 metadata table"
구조를 유지한다.
