# Phase 4 Strict Annual Interpretation And Value Strict First Pass

## 목적

- strict annual 전략이 단순히 수익률만 나오는 상태를 넘어서,
  어떤 종목을 왜 골랐는지 읽을 수 있게 한다.
- quality strict 다음 strict factor family로
  `Value Snapshot (Strict Annual)`을 public candidate로 추가한다.

## 구현한 것

### 1. strict/broad snapshot 전략용 Selection History 탭

파일:
- `app/web/pages/backtest.py`

적용 전략:
- `Quality Snapshot`
- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`

표시 내용:
- first active date
- active rebalance count
- distinct selected names 수
- factor family / snapshot mode / snapshot source
- rebalance date별
  - `Selected Tickers`
  - `Selected Count`
  - `Selection Score`
  - `Total Balance`
  - `Total Return`

즉 strict annual 전략 검증/해석 강화의 first-pass는
`Selection History` 화면으로 구현되었다.

### 2. Value Snapshot (Strict Annual) public candidate 추가

파일:
- `app/web/runtime/backtest.py`
- `app/web/runtime/__init__.py`
- `app/web/runtime/history.py`
- `app/web/pages/backtest.py`

추가된 것:
- `run_value_snapshot_strict_annual_backtest_from_db(...)`
- single-strategy form
- compare mode strategy option
- history / `Load Into Form` / `Run Again`
- `value_factors`, `snapshot_source` 메타 저장

현재 first-pass 기본 factor:
- `per`
- `pbr`
- `sales_yield`
- `earnings_yield`

## 검증

### sample-universe

대상:
- `AAPL`, `MSFT`, `GOOG`
- `2016-01-01 ~ 2026-03-20`

결과:
- `Value Snapshot (Strict Annual)`
  - `End Balance = 7725.2`

### wider-universe runtime check

대상:
- `US Statement Coverage 100`
- `top_n = 10`

결과:
- elapsed: `3.399s`
- `End Balance = 19578.5`
- first active date: `2022-07-29`

## 현재 의미

- strict annual family는 이제 public candidate가 2개다.
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
- 그리고 strict annual 전략은 이제
  수익률만 보는 black-box 경로가 아니라,
  selection history로 검증/해석 가능한 상태가 되었다.
