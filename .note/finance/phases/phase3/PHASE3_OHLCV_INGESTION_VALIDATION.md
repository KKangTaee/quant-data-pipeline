# Phase 3 OHLCV Ingestion Validation

## 목적
이 문서는 stock + ETF 공통 OHLCV 수집 hardening 이후
실제 검증 결과를 기록한다.

---

## 적용 내용 요약

1. stock + ETF를 같은 `nyse_price_history`에 저장하는 구조 유지
2. yfinance OHLCV batch fetch 병렬화
3. `start/end` 지원 보강
4. missing symbol / processed symbol 집계 보강
5. Daily Market Update 기본 source를 `NYSE Stocks + ETFs`로 변경
6. Manual symbol preset/custom 입력 해석 UX 정리

---

## 검증 1. ETF OHLCV 적재

실행:
- `run_daily_market_update(['VIG', 'SCHD', 'DGRO', 'GLD'], period='1y', interval='1d')`

결과:
- `status = success`
- `rows_written = 1004`
- `symbols_requested = 4`
- `symbols_processed = 4`
- `failed_symbols = []`

DB 확인:
- `finance_price.nyse_price_history`
  - `VIG`: 251 rows
  - `SCHD`: 251 rows
  - `DGRO`: 251 rows
  - `GLD`: 251 rows

---

## 검증 2. DB 기반 Equal Weight 샘플

실행:
- `get_equal_weight_from_db(tickers=['VIG','SCHD','DGRO','GLD'], start='2025-01-01', end='2026-03-22', interval=1)`

결과:
- result rows: `13`
- final `Total Balance = 11815.2`

의미:
- ETF OHLCV 적재 후
- DB -> loader -> engine -> strategy 경로가 정상적으로 이어짐

---

## 주의 메모

- `finance/transform.py:121` 에 기존 `SettingWithCopyWarning`이 남아 있음
- 이번 검증에서는 실행 결과 자체에는 영향이 없었음

---

## 결론

이번 hardening 이후
stock + ETF OHLCV 공통 수집 경로는 정상 동작이 확인되었다.

특히 ETF 4종 적재와
DB 기반 `EqualWeightStrategy` 샘플 실행까지 확인했으므로,
Daily Market Update와 DB-backed sample 경로는 현재 기준으로 usable 상태다.
