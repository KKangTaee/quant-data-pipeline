# Phase 4 Strict Multi-Factor Public Candidate First Pass

## 목적

- strict annual family를 `Quality`, `Value` 단일 팩터 후보에서
  첫 multi-factor public candidate까지 확장한다.

## 추가된 전략

- `Quality + Value Snapshot (Strict Annual)`

## 기본 구성

- quality factors:
  - `roe`
  - `roa`
  - `net_margin`
  - `asset_turnover`
  - `current_ratio`
- value factors:
  - `per`
  - `pbr`
  - `sales_yield`
  - `earnings_yield`
- execution:
  - `timeframe = 1d`
  - `option = month_end`
  - `annual statement shadow factors`
  - `equal-weight holding`

## UI / runtime 반영 범위

- single strategy form 추가
- compare strategy 옵션 추가
- runtime wrapper 추가
- history / prefill 경로 추가
- selection history는 기존 strict family와 동일하게 읽을 수 있다

## first-pass 검증

### `US Statement Coverage 100`

- runtime:
  - `3.569s`
- first active date:
  - `2021-08-31`
- result:
  - `End Balance = 24778.9`
  - `CAGR = 9.36%`
  - `Sharpe Ratio = 0.7048`
  - `Maximum Drawdown = -27.68%`

### `US Statement Coverage 300`

- runtime:
  - `9.785s`
- first active date:
  - `2021-08-31`
- result:
  - `End Balance = 16931.4`
  - `CAGR = 5.33%`
  - `Sharpe Ratio = 0.4275`
  - `Maximum Drawdown = -27.83%`

## 해석

- strict multi-factor family는 현재 **first public candidate** 수준까지는 올라왔다.
- 다만 현재 결과만 보면 primary strict annual family는 여전히 `Quality Snapshot (Strict Annual)`이다.
- 즉 지금 multi-factor는
  - public candidate: `yes`
  - primary default family: `not yet`

