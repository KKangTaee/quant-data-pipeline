# Phase 4 Quality Snapshot Implementation First Pass

## 목적
이 문서는 `Quality Snapshot Strategy`의 broad-research first-pass 구현 기록이다.

## 구현한 것

### 1. 전략 시뮬레이션 함수
- `finance/strategy.py`
  - `_rank_quality_snapshot(...)`
  - `quality_snapshot_equal_weight(...)`

역할:
- quality factor snapshot을 ranking
- top N selection
- 다음 구간 equal-weight holding

### 2. DB-backed sample entrypoint
- `finance/sample.py`
  - `get_quality_snapshot_from_db(...)`

역할:
- DB-backed price path 준비
- rebalance date별 factor snapshot 조회
- quality strategy 시뮬레이션 실행

### 3. Public runtime wrapper
- `app/web/runtime/backtest.py`
  - `run_quality_snapshot_backtest_from_db(...)`

역할:
- UI가 직접 호출할 broad-research first-pass wrapper
- result bundle 반환

## first-pass 기본값
- snapshot mode: `broad_research`
- factor freq: `annual`
- rebalance freq: `monthly`
- default quality factors:
  - `roe`
  - `gross_margin`
  - `operating_margin`
  - `debt_ratio`

## 검증
- `.venv` 기준으로:
  - `tickers=['AAPL','MSFT','GOOG']`
  - `start='2016-01-01'`
  - `end='2026-03-20'`
  - `top_n=2`
  - `factor_freq='annual'`
  로 실행 검증

확인 결과:
- result rows: `123`
- wrapper `strategy_name = Quality Snapshot`
- `End Balance = 16411.8`
- `CAGR = 0.05008`
- `Sharpe Ratio = 0.469804`

## 현재 상태
- broad-research first-pass runtime은 구현 완료
- Backtest UI에는 이미 다섯 번째 공개 전략으로 노출되었다
- 현재 public quality path는:
  - DB-backed price history
  - `nyse_factors` snapshot
  을 함께 사용한다
- 따라서 first-pass 실행 전 실무적으로 필요한 수집은:
  - `Daily Market Update` 또는 OHLCV 수집
  - `Weekly Fundamental Refresh`
  이다
- `Extended Statement Refresh`는 현재 public quality strategy의 필수 전제는 아니다
