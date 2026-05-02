# Phase 4 Coverage 1000 And Value Strict Closeout

## 목적

- `US Statement Coverage 1000`의 현재 위치를 closeout 기준으로 다시 고정한다.
- `Value Snapshot (Strict Annual)`이 early-history flat path에서 벗어나도록 보강한 내용을 정리한다.
- Phase 4 종료 직전 기준의 strict annual family 상태를 한 문서에서 확인할 수 있게 한다.

## 1. `Coverage 1000` stale-symbol refresh와 재검증

### 수행한 작업

- strict annual preflight가 잡아낸 stale symbol `9`개를 대상으로
  targeted `Daily Market Update`를 다시 실행했다.
- refresh 대상:
  - `CADE`, `CMA`, `DAY`, `CFLT`, `GSAT`, `UBSI`, `WMG`, `WTS`, `WWD`

### 결과

- refresh 이후 stale symbol은 `4`개만 남았다.
  - `CADE`
  - `CMA`
  - `DAY`
  - `CFLT`
- current preflight:
  - requested: `1000`
  - covered: `1000`
  - common latest: `2026-01-30`
  - newest latest: `2026-03-20`
  - spread: `49d`

### 해석

- `US Statement Coverage 1000`은 now usable staged preset이다.
- 다만 freshness warning이 아직 남아 있기 때문에
  official public default로 올리기보다
  operator / staging preset으로 두는 판단이 맞다.

## 2. `Coverage 1000` backtest 재검증

### quality strict

- `Quality Snapshot (Strict Annual)`
- preset:
  - `US Statement Coverage 1000`
- 결과:
  - canonical monthly rows 유지
  - large-universe sparse non-month-end row issue는 재현되지 않음

즉 현재 남은 이슈는 price freshness 운영 문제이지,
calendar shaping이나 strategy row construction 문제는 아니다.

## 3. `Value Snapshot (Strict Annual)` early-history flat 문제 원인

기존 value strict가 `2016~2021` 구간에서 사실상 현금 대기로 보인 이유는,
valuation 계열 factor가 주로 `market_cap` 및 shares-derived field에 의존하는데
statement shadow fundamentals의 `shares_outstanding`이 늦게 채워졌기 때문이다.

실제 root cause:
- annual statement shadow에서
  direct outstanding concept가 충분하지 않았다.
- 기존 fallback은 broad fundamentals nearest-period-end에 크게 의존했다.
- 그 결과 valuation factor usable history가 `2021` 이후로 밀렸다.

## 4. `Value Strict` 보강 내용

### shares fallback 강화

`finance/data/fundamentals.py`에서
statement shadow fundamentals 생성 시
historical share-count fallback을 더 넓혔다.

현재 fallback 우선순위:
- direct outstanding concepts
  - `dei:EntityCommonStockSharesOutstanding`
  - `us-gaap:CommonStockSharesOutstanding`
  - `us-gaap:CommonSharesOutstanding`
- fallback weighted-average shares concepts
  - `us-gaap:WeightedAverageNumberOfSharesOutstandingBasic`
  - `us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding`

이 변경 이후 valuation-related shadow factors는
top-300 기준으로 `2011-12-31`부터 usable history가 생긴다.

### value factor set 확장

strict annual value 기본 factor set도
coverage와 해석력을 고려해 다음과 같이 정리했다.

- `book_to_market`
- `earnings_yield`
- `sales_yield`
- `ocf_yield`
- `operating_income_yield`

UI advanced inputs에서는 추가로 아래 factor도 선택 가능하다.

- `fcf_yield`
- `per`
- `pbr`
- `psr`
- `pcr`
- `pfcr`
- `ev_ebit`
- `por`

## 5. `Value Strict` 재검증 결과

### `US Statement Coverage 300`

- `Value Snapshot (Strict Annual)`
- `2016-01-01 ~ 2026-03-20`
- `top_n = 10`
- first active:
  - `2016-01-29`
- 결과:
  - `End Balance = 85378.4`
  - `CAGR = 23.56%`
  - `Sharpe Ratio = 1.1341`
  - `Maximum Drawdown = -26.04%`

### `US Statement Coverage 1000`

- `Value Snapshot (Strict Annual)`
- `2016-01-01 ~ 2026-03-20`
- `top_n = 10`
- first active:
  - `2016-01-29`
- 결과:
  - `End Balance = 91733.7`
  - `CAGR = 24.43%`
  - `Sharpe Ratio = 1.0644`
  - `Maximum Drawdown = -26.72%`
- preflight:
  - `warning`
  - stale symbols `4`
  - spread `49d`

## 6. closeout 판단

- `Quality Snapshot (Strict Annual)`:
  - strict annual family의 primary public candidate 유지
- `Value Snapshot (Strict Annual)`:
  - 더 이상 `2021` 이후만 동작하는 incomplete candidate가 아니다
  - `2016`부터 실제 전략 경로로 동작한다
  - 다만 valuation/shares/freshness 의존성이 더 크므로
    current Phase 4 기준에서는 still secondary candidate로 두는 편이 맞다
- `US Statement Coverage 1000`:
  - real top-1000 managed preset으로 동작
  - canonical monthly rows도 유지
  - 하지만 stale symbol `4`와 `49d` spread 때문에
    public default로 승격하지 않고 staged preset으로 유지한다

## 7. Phase 4 의미

이 closeout 기준으로 보면 Phase 4는
- strict annual quality
- strict annual value
- strict annual quality+value
- wider managed preset
- stale/freshness preflight

까지 모두 구현/검증을 마친 상태다.

따라서 다음 workstream은
새 기능을 더 덧붙이는 작업보다
Phase 5 수준의 strategy library / comparative research 정리가 더 자연스럽다.
