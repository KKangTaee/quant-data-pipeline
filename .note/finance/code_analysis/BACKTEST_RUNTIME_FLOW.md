# Backtest Runtime Flow

## 목적

이 문서는 백테스트 실행이 UI 입력에서 finance strategy 결과까지 어떻게 이동하는지 설명한다.
전략 실행 오류, payload 복원 오류, result bundle 누락을 볼 때 먼저 확인한다.

## 현재 큰 흐름

```text
app/web/streamlit_app.py
  -> app/web/pages/backtest.py
  -> app/web/runtime/backtest.py
  -> finance/loaders/*
  -> finance/engine.py / finance/transform.py
  -> finance/strategy.py
  -> finance/performance.py
  -> result bundle / metadata / warnings
  -> Backtest UI latest result, history, compare, saved replay
```

## 핵심 파일

| 파일 | 역할 |
|---|---|
| `app/web/streamlit_app.py` | Finance Console navigation entry |
| `app/web/pages/backtest.py` | form, panel, result surface, history, compare, saved portfolio UI |
| `app/web/runtime/backtest.py` | UI payload를 DB-backed runtime 실행으로 변환 |
| `finance/loaders/*` | DB read path와 point-in-time snapshot 조회 |
| `finance/engine.py` | price-based strategy orchestration wrapper |
| `finance/transform.py` | moving average, interval return, date alignment 같은 전처리 |
| `finance/strategy.py` | 실제 strategy simulation |
| `finance/performance.py` | CAGR, Sharpe, drawdown, weighted portfolio 계산 |

## Runtime wrapper 기준

`app/web/runtime/backtest.py`의 `run_*_backtest_from_db(...)` 함수는 제품 실행 경로의 중심이다.

대표 함수:

- `run_equal_weight_backtest_from_db(...)`
- `run_gtaa_backtest_from_db(...)`
- `run_global_relative_strength_backtest_from_db(...)`
- `run_risk_parity_trend_backtest_from_db(...)`
- `run_dual_momentum_backtest_from_db(...)`
- `run_quality_snapshot_strict_annual_backtest_from_db(...)`
- `run_value_snapshot_strict_annual_backtest_from_db(...)`
- `run_quality_value_snapshot_strict_annual_backtest_from_db(...)`
- quarterly prototype strict family runtime 함수들

## Result bundle 기준

제품 UI가 안정적으로 동작하려면 runtime 결과가 다음 정보를 유지해야 한다.

- `result_df`: 날짜별 balance / return table
- `summary`: CAGR, Sharpe, MDD 같은 성과 요약
- `meta`: strategy settings, contract, coverage, warning context
- `warnings`: 데이터 부족, excluded ticker, stale data 같은 사용자 주의사항
- selection history가 있는 전략은 selection row와 interpretation context

## Date alignment 주의

`finance/transform.py`의 alignment 계층은 결과 기간을 크게 바꿀 수 있다.

- `add_ma(...)`: moving average warmup 이전 구간 제거
- `add_interval_returns(...)`: trailing return warmup 이전 구간 제거
- `align_dfs_by_date_intersection(...)`: 모든 ticker에 공통으로 있는 날짜만 유지
- `align_dfs_by_date_union(...)`: 공통 날짜보다 넓은 union 기준이 필요한 경우 사용

ETF basket 전략에서 특정 ticker의 가격 이력이나 결측이 부족하면,
전체 결과가 짧아지거나 ticker가 excluded 처리될 수 있다.
이 경우 조용히 지나가지 말고 warning / metadata에 남겨야 한다.

## 갱신해야 하는 경우

- 새 `run_*_backtest_from_db(...)` 함수가 추가될 때
- result bundle shape가 바뀔 때
- warning / metadata 계약이 바뀔 때
- date alignment 정책이 바뀔 때
- real-money / pre-live / history replay가 runtime output을 새 방식으로 읽게 될 때
