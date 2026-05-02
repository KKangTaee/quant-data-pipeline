# Phase 8 Quarterly Validation First Pass

## 목적

- quarterly value / quality+value prototype가 실제로 실행되는지 확인
- single + compare + interpretation surface가 최소한의 parity를 갖는지 확인

## validation set

### Manual small universe

- tickers:
  - `AAPL`
  - `MSFT`
  - `GOOG`
- period:
  - `2016-01-01 -> 2026-03-28`

### Managed preset

- preset:
  - `US Statement Coverage 100`
- period:
  - `2016-01-01 -> 2026-03-28`

## confirmed results

### Value Snapshot (Strict Quarterly Prototype)

- manual `AAPL/MSFT/GOOG`
  - first active date:
    - `2017-05-31`
  - summary:
    - `End Balance = 72,034.4`
    - `CAGR = 21.46%`
    - `Sharpe = 1.0285`
    - `MDD = -26.98%`
- preset `US Statement Coverage 100`
  - first active date:
    - `2016-01-29`
  - summary:
    - `End Balance = 140,853.2`
    - `CAGR = 29.75%`
    - `Sharpe = 1.3447`
    - `MDD = -37.56%`

### Quality + Value Snapshot (Strict Quarterly Prototype)

- manual `AAPL/MSFT/GOOG`
  - first active date:
    - `2017-05-31`
  - summary:
    - `End Balance = 68,258.0`
    - `CAGR = 20.82%`
    - `Sharpe = 1.0066`
    - `MDD = -26.98%`
- preset `US Statement Coverage 100`
  - first active date:
    - `2016-01-29`
  - summary:
    - `End Balance = 187,769.4`
    - `CAGR = 33.47%`
    - `Sharpe = 1.4283`
    - `MDD = -32.86%`

### Compare surface smoke

- `_run_compare_strategy("Value Snapshot (Strict Quarterly Prototype)", ...)` 실행 확인
- selection history build 확인:
  - `selection_rows = 123`
- compare bundle meta에 아래 key가 남음:
  - `factor_freq`
  - `snapshot_mode`
  - `snapshot_source`
  - `trend_filter_enabled`
  - `trend_filter_window`
  - `market_regime_enabled`
  - `market_regime_window`
  - `market_regime_benchmark`
  - `value_factors`

### import / compile smoke

- `py_compile`:
  - `app/web/pages/backtest.py`
  - `app/web/runtime/backtest.py`
  - `app/web/runtime/__init__.py`
  - `finance/sample.py`
- `app.web.streamlit_app` import:
  - OK

## interpretation

- quarterly value / quality+value path는 이제 single-only 데모가 아니라
  compare / history까지 연결된 연구 surface로 볼 수 있다.
- 다만 active start가 small manual universe에서 늦게 열리는 점은 여전히 quarterly research-only semantics와 잘 맞는다.
- managed preset 기준으로는 `2016-01-29`까지 복구되어,
  quarterly family의 비교 연구는 이제 충분히 가능한 상태다.
