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

Phase 27 이후 result bundle meta에는 Data Trust Summary가 읽을 수 있도록 아래 값도 포함한다.

- `result_rows`: 실제 result table row 수
- `actual_result_start`: 실제 결과 시작일
- `actual_result_end`: 실제 결과 종료일
- `price_freshness`: ticker별 최신 가격 날짜 / stale / missing 진단
- `excluded_tickers`: 실행 중 제외된 ticker
- `malformed_price_rows`: 가격 결측 행이 있는 ticker 요약

Phase 28 이후 새 backtest history record도 재실행 / form 복원 QA를 위해
일부 result-window / data-trust 값을 같이 보존한다.

- `result_rows`
- `actual_result_start`
- `actual_result_end`
- `price_freshness`
- `requested_tickers`
- `excluded_tickers`
- `malformed_price_rows`
- `guardrail_reference_ticker`

Saved Portfolio replay로 생성되는 history context에는 재진입 확인을 위해
`weights_percent`도 함께 남긴다.
strategy별 세부 override는 saved portfolio record의 `compare_context.strategy_overrides`가 기준이다.

Phase 28 이후 compare / weighted portfolio history context에는 component별 data trust rows도 남긴다.

- `strategy_data_trust_rows`: strategy compare record에 저장되는 전략별 data trust snapshot
- `component_data_trust_rows`: weighted portfolio record에 저장되는 구성 전략별 data trust snapshot

이 값은 성과 계산 자체를 바꾸지 않고, 사용자가 compare / weighted / saved replay 결과를 읽을 때
각 component의 실제 결과 기간과 데이터 품질 조건을 다시 확인하게 하는 metadata다.

Phase 28 이후 Real-Money / Guardrail parity는 별도의 성과 계산 로직을 새로 만들지 않고,
이미 result bundle meta나 saved portfolio override에 남아 있는 값을 읽어 scope table로 보여준다.

- annual strict: benchmark / investability / promotion / guardrail 입력을 full strict surface로 해석한다.
- strict quarterly prototype: portfolio handling과 risk-off contract는 저장하지만, promotion guardrail surface는 deferred로 해석한다.
- ETF 전략군: Equal Weight / GTAA / Global Relative Strength / Risk Parity Trend / Dual Momentum의 ETF operability, cost, benchmark, ETF guardrail first pass를 strategy별 지원 범위로 해석한다.

이 scope table은 runtime result를 바꾸지 않는다.
사용자가 history / saved replay 전에 어떤 검증 범위의 결과인지 이해하게 하는 metadata 해석 layer다.

## Real-Money / Guardrail / Pre-Live runtime 기준

runtime은 단순 성과표만 반환하지 않는다.
특히 실전형 후보 검토가 붙은 전략은 아래 진단 정보를 같이 남겨야 한다.

- gross / net / cost result
- turnover / cost assumption
- benchmark overlay와 benchmark-relative diagnostics
- investability filter 결과
- liquidity / coverage policy status
- underperformance / drawdown guardrail trigger state
- promotion / shortlist / deployment 또는 pre-live review status

주의:

- `Real-Money`는 실제 투자 승인 자체가 아니라 실행 가능성 진단 계층이다.
- `Pre-Live`는 real-money 진단 이후 paper / watchlist / hold / reject / re-review 같은 운영 상태를 기록하는 계층이다.
- runtime metadata가 없으면 UI는 숫자를 보여줄 수 있어도 왜 그 결과가 나왔는지 설명하기 어렵다.

## Date alignment 주의

`finance/transform.py`의 alignment 계층은 결과 기간을 크게 바꿀 수 있다.

- `add_ma(...)`: moving average warmup 이전 구간 제거
- `add_interval_returns(...)`: trailing return warmup 이전 구간 제거
- `align_dfs_by_date_intersection(...)`: 모든 ticker에 공통으로 있는 날짜만 유지
- `align_dfs_by_date_union(...)`: 공통 날짜보다 넓은 union 기준이 필요한 경우 사용

ETF basket 전략에서 특정 ticker의 가격 이력이나 결측이 부족하면,
전체 결과가 짧아지거나 ticker가 excluded 처리될 수 있다.
이 경우 조용히 지나가지 말고 warning / metadata에 남겨야 한다.

`Global Relative Strength`는 Phase 27 첫 작업부터 price freshness preflight와
Data Trust Summary metadata를 남기는 첫 적용 대상이다.

## 갱신해야 하는 경우

- 새 `run_*_backtest_from_db(...)` 함수가 추가될 때
- result bundle shape가 바뀔 때
- warning / metadata 계약이 바뀔 때
- date alignment 정책이 바뀔 때
- real-money / pre-live / history replay가 runtime output을 새 방식으로 읽게 될 때
