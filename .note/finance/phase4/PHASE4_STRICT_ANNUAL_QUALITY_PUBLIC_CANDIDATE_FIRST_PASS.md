# Phase 4 Strict Annual Quality Public Candidate First Pass

## 목적

- sample-universe에서 검증된 strict annual statement-driven quality path를
  Backtest UI의 public candidate 전략으로 올린다.
- 기존 broad `Quality Snapshot`은 그대로 유지하고,
  strict annual path는 별도 전략으로 함께 노출한다.

## 왜 별도 전략으로 올렸는가

- broad `Quality Snapshot`은 현재 public path로 이미 사용 중이다.
- strict annual path는 source, strictness, 수집 전제가 다르다.
  - broad path:
    - `nyse_factors`
  - strict annual path:
    - `nyse_financial_statement_values`
    - `nyse_fundamentals_statement`
    - `nyse_factors_statement`
- 따라서 broad path를 조용히 교체하기보다
  `Quality Snapshot (Strict Annual)`이라는 별도 전략으로 비교 가능하게 여는 편이 안전하다.

## 구현한 것

### runtime

- `app/web/runtime/backtest.py`
  - `run_quality_snapshot_strict_annual_backtest_from_db(...)` 추가
  - strict statement quality 공용 helper `_run_statement_quality_bundle(...)` 추가

### UI

- `app/web/pages/backtest.py`
  - single-strategy selector에
    - `Quality Snapshot (Strict Annual)`
    추가
  - 별도 form 추가:
    - universe
    - start / end
    - top N
    - quality factor 선택
  - `Data Requirements` 안내 추가
    - OHLCV 필요
    - `Extended Statement Refresh (annual)` 필요
  - compare 전략 옵션에도 포함

### history / prefill

- strict annual strategy key:
  - `quality_snapshot_strict_annual`
- history 저장 / `Load Into Form` / `Run Again` 지원

## 검증

wrapper smoke check:
- tickers:
  - `AAPL`, `MSFT`, `GOOG`
- period:
  - `2016-01-01 ~ 2026-03-20`

결과:
- `strategy_name = Quality Snapshot (Strict Annual)`
- `End Balance = 93934.6`
- `CAGR = 0.24725673938829384`

추가 검증:
- compare defaults / history payload / display-name mapping 정상 확인
- `python3 -m py_compile`
  - `app/web/runtime/backtest.py`
  - `app/web/runtime/__init__.py`
  - `app/web/pages/backtest.py`
  통과

## 현재 의미

- broad quality:
  - current research-oriented public path
- strict annual quality:
  - statement-driven public candidate path

즉 이제 Backtest UI에는 quality 계열이 두 경로로 공존한다.

- `Quality Snapshot`
- `Quality Snapshot (Strict Annual)`

## 다음 판단

- 두 quality path를 어떤 원칙으로 함께 둘지
- wider universe coverage를 먼저 늘릴지
- hybrid shares fallback을 언제까지 허용할지
를 다음 단계에서 정리해야 한다.
