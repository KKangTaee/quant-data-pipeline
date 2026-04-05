# Phase 12 Strict Annual Investability And Benchmark Reinforcement First Pass

## 목적

- strict annual family를 실전형으로 읽을 때
  `Minimum Price`만으로는 부족했던 investability 판단을 조금 더 보강한다.
- benchmark를 단순 overlay로만 두지 않고,
  전략과 benchmark의 상대 성과를 더 직접적으로 읽을 수 있게 만든다.

## 이번에 추가된 것

### 1. `Minimum History (Months)`

- 대상:
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`
- 의미:
  - 각 리밸런싱 시점 전에 최소 몇 개월의 가격 이력이 쌓여 있어야
    그 종목을 투자 후보로 인정할지 정하는 필터다.
- 기본값:
  - `0`
  - 즉 기본 동작은 기존과 같고, 필요할 때만 더 엄격하게 켤 수 있다.

### 2. richer benchmark surface

- shared real-money helper가 이제 benchmark가 있을 때 아래도 같이 계산한다.
  - `Benchmark CAGR`
  - `Net CAGR Spread`
  - `Benchmark Coverage`
- 의미:
  - 전략 자체 CAGR만 보는 것이 아니라,
    같은 기간 benchmark CAGR과의 차이를 같이 읽게 해준다.
  - benchmark 데이터가 실제로 얼마나 잘 정렬되었는지도 coverage로 바로 확인할 수 있다.

## UI / Runtime 반영 위치

### Single Strategy

- annual strict 3종 form에
  - `Minimum Price`
  - `Minimum History (Months)`
  - `Transaction Cost (bps)`
  - `Benchmark Ticker`
  가 같이 보인다.

### Real-Money 탭

- 상단 metric에
  - `Minimum History`
  - `Benchmark CAGR`
  - `Net CAGR Spread`
  가 추가되었다.
- `Benchmark Coverage`는 caption으로 같이 보여준다.

### Execution Context / Compare

- `Execution Context`에
  - `Minimum History`
  - `Benchmark CAGR`
  - `Net CAGR Spread`
  - `Benchmark Coverage`
  가 같이 남는다.
- `Compare > Strategy Highlights`에는
  - `Min History (M)`
  - `Net CAGR Spread`
  가 추가되었다.

### History / Prefill

- 아래 값이 history payload / `Load Into Form` / compare prefill에도 같이 남는다.
  - `min_history_months_filter`

## 전략 규칙 쪽 변화

- strict annual selection runtime은 이제
  - `min_price`
  - `min_history_months`
  를 함께 candidate filter로 사용한다.
- result row에는
  - `Minimum History Months`
  - `History Excluded Count`
  가 남아서,
  실제로 history 부족 때문에 얼마나 제외되었는지 읽을 수 있다.

## 현재 해석

- 이 작업은 stronger investability proxy의 first pass다.
- 여전히 완전한 유동성/거래량/spread 기반 investability는 아니다.
- 하지만
  - 너무 짧은 가격 이력만 가진 종목이
  - annual strict ranking에 바로 섞이는 문제는
  지금보다 훨씬 덜하게 된다.

## 검증

- `py_compile`
  - `finance/sample.py`
  - `finance/strategy.py`
  - `app/web/runtime/backtest.py`
  - `app/web/runtime/history.py`
  - `app/web/pages/backtest.py`
- DB-backed annual strict smoke:
  - `min_history_months_filter = 12`
  - `benchmark_cagr` 생성 확인
  - `net_cagr_spread` 생성 확인
  - result row의 `Minimum History Months`, `History Excluded Count` 확인

## 남은 것

- stronger investability later pass
  - volume / AUM / spread 계열
- richer benchmark contract later pass
  - 더 다양한 benchmark policy
  - subperiod benchmark-relative review
- stricter promotion reinforcement later pass
