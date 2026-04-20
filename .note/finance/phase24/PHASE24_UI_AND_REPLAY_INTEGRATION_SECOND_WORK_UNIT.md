# Phase 24 UI And Replay Integration Second Work Unit

## 이 문서는 무엇인가

`Phase 24` 두 번째 작업 단위로,
첫 신규 전략 `Global Relative Strength`를 실제 `Backtest` 제품 화면에 연결한 내용을 정리한다.

첫 번째 작업이 core strategy와 runtime wrapper가 계산되는지 확인한 단계였다면,
이번 작업은 사용자가 화면에서 전략을 고르고,
compare에 넣고,
history나 saved portfolio에서 다시 불러올 수 있는지 확인하는 단계다.

## 쉽게 말하면

전략 계산 엔진만 있으면 개발자는 실행할 수 있지만,
사용자는 아직 제품 기능으로 쓰기 어렵다.

이번 작업은 `Global Relative Strength`를
`Backtest` 화면의 전략 선택지 안으로 넣고,
한 번 실행한 설정이 history / compare / saved replay 경로에서 사라지지 않도록 연결한 것이다.

## 왜 필요한가

- 새 전략이 single 실행만 되면 제품 전략이라고 보기 어렵다.
- compare, history, saved replay에서 다시 열 수 있어야 반복 검증이 가능하다.
- Phase 24의 목표는 신규 전략을 한 번 임시로 붙이는 것이 아니라,
  앞으로 다른 전략도 같은 방식으로 붙일 수 있는 경로를 만드는 것이다.

## 이번 작업에서 바꾼 것

### 1. 전략 카탈로그 등록

- `Global Relative Strength`를 single / compare 전략 선택지에 추가했다.
- strategy key는 `global_relative_strength`로 고정했다.

### 2. Single Strategy UI 추가

- `Backtest > Single Strategy`에서 `Global Relative Strength`를 선택할 수 있게 했다.
- 입력 항목:
  - universe preset / manual tickers
  - cash / defensive ticker
  - top assets
  - signal interval
  - score horizons
  - trend filter window
  - ETF real-money contract

### 3. Compare UI 추가

- `Backtest > Compare & Portfolio Builder`에서 `Global Relative Strength`를 비교 전략으로 고를 수 있게 했다.
- 선택된 전략 box 안에서 전략별 입력값을 바로 확인하고 수정할 수 있게 했다.
- compare 실행 시 새 전략 전용 설정이 runtime wrapper로 전달되도록 했다.

### 4. History / Load Into Form / Run Again 연결

- history record에 `cash_ticker`, `research_source`가 보존되도록 했다.
- `Load Into Form`에서 universe, cash ticker, score horizon, trend filter, real-money contract 값이 복원되도록 했다.
- `Run Again`에서 `global_relative_strength` payload가 다시 실행되도록 했다.

### 5. Saved Portfolio Replay 연결

- saved portfolio가 compare context를 복원할 때 `Global Relative Strength` override를 잃지 않도록 했다.
- saved replay가 compare runner를 통해 새 전략을 다시 실행할 수 있게 했다.

## 검증 결과

### Python compile

- `python3 -m py_compile app/web/backtest_strategy_catalog.py app/web/runtime/backtest.py app/web/runtime/history.py app/web/pages/backtest.py`
- 결과: 통과

### Catalog / history payload smoke

- `Global Relative Strength`가 single / compare strategy options에 포함되는지 확인했다.
- `global_relative_strength` history payload가 `cash_ticker`와 `interval`을 복원하는지 확인했다.
- 결과: 통과

### DB-backed runtime smoke

- 대상:
  - tickers: `SPY, EFA, TLT, GLD`
  - cash ticker: `BIL`
  - period: `2025-01-01 ~ 2025-06-30`
  - top: `2`
  - interval: `1`
- 결과:
  - `Global Relative Strength`
  - rows: `6`
  - `cash_ticker = BIL`
  - `etf_operability_status = watch`

### Compare runner smoke

- `_run_compare_strategy("Global Relative Strength", ...)`로 직접 실행했다.
- 결과:
  - strategy name 보존
  - result rows 생성
  - `cash_ticker = BIL` 보존

## 아직 확인할 것

이번 작업은 코드 레벨 smoke와 DB-backed smoke까지 완료했다.
사용자 manual QA에서는 아래 흐름을 실제 화면에서 확인해야 한다.

- `Backtest > Single Strategy > Global Relative Strength`
- `Backtest > Compare & Portfolio Builder > Strategies`
- `Backtest > History > Selected History Run > Load Into Form`
- `Backtest > History > Selected History Run > Run Again`
- `Backtest > Compare & Portfolio Builder > Saved Portfolios > Replay Saved Portfolio`

## 한 줄 정리

`Global Relative Strength`는 이제 core/runtime만 있는 전략이 아니라,
single / compare / history / saved replay 경로까지 제품 화면에 연결된 신규 전략 family가 되었다.
