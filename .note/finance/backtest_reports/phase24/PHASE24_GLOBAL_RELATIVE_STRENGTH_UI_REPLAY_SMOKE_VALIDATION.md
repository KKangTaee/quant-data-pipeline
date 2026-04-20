# Phase 24 Global Relative Strength UI Replay Smoke Validation

## 이 문서는 무엇인가

`Global Relative Strength`가 core/runtime 단계를 지나
`Backtest` 제품 화면과 재진입 흐름에 연결되었는지 확인한 개발 검증 report다.

이 문서는 투자 성과를 평가하지 않는다.
목적은 새 전략이 single, compare, history, saved replay 흐름에서
설정값을 잃지 않고 반복 실행될 수 있는지 확인하는 것이다.

## 검증 범위

| 영역 | 확인 내용 | 결과 |
|---|---|---|
| Strategy catalog | single / compare 선택지에 `Global Relative Strength` 노출 | 통과 |
| Single Strategy | 전략 전용 입력 form 추가 | 통과 |
| Compare | strategy-specific box와 compare override 연결 | 통과 |
| History payload | `cash_ticker`, `interval`, score horizon 복원 | 통과 |
| Saved replay override | saved portfolio compare context 복원용 override 추가 | 통과 |
| Runtime meta | `cash_ticker`, `research_source`, `trend_filter_enabled` 보존 | 통과 |

## 실행한 smoke checks

### 1. Python compile

대상:

- `app/web/backtest_strategy_catalog.py`
- `app/web/runtime/backtest.py`
- `app/web/runtime/history.py`
- `app/web/pages/backtest.py`

결과:

- 통과

### 2. Catalog / history payload smoke

확인한 것:

- `Global Relative Strength`가 `SINGLE_STRATEGY_OPTIONS`와 `COMPARE_STRATEGY_OPTIONS`에 들어간다.
- display name과 strategy key가 `global_relative_strength`로 왕복된다.
- history record에서 `cash_ticker = BIL`, `rebalance_interval = 1`이 payload로 복원된다.

결과:

- 통과

### 3. DB-backed runtime smoke

실행 조건:

| 항목 | 값 |
|---|---|
| Tickers | SPY, EFA, TLT, GLD |
| Cash proxy | BIL |
| 기간 | 2025-01-01 ~ 2025-06-30 |
| Top N | 2 |
| Signal interval | 1 |
| Min price | 5.0 |
| Transaction cost | 10 bps |

결과:

| 항목 | 값 |
|---|---:|
| Rows | 6 |
| End Balance | 10,979.56 |
| CAGR | 25.86% |
| Sharpe Ratio | 3.8266 |
| Maximum Drawdown | 0.00% |
| ETF Operability | watch |

해석:

- 이 수치는 짧은 smoke 기간에서 나온 기능 검증 결과다.
- 투자 판단이나 후보 승격 판단으로 쓰지 않는다.
- 핵심 확인점은 result bundle이 생성되고 meta가 보존된다는 점이다.

### 4. Compare runner smoke

확인한 것:

- `_run_compare_strategy("Global Relative Strength", ...)`가 새 전략을 실행한다.
- manual ticker universe와 `cash_ticker = BIL`이 runner에 전달된다.
- result rows와 meta가 생성된다.

결과:

- 통과

## 아직 manual QA가 필요한 것

아래는 실제 Streamlit 화면에서 사용자가 확인해야 한다.

- `Backtest > Single Strategy > Global Relative Strength`에서 form이 자연스럽게 보이는지
- `Run Global Relative Strength Backtest` 실행 후 결과가 표시되는지
- `Backtest > Compare & Portfolio Builder`에서 compare 전략으로 넣을 수 있는지
- `Backtest > History`에서 `Load Into Form`과 `Run Again`이 기대대로 작동하는지
- saved portfolio replay에 새 전략이 포함되어도 오류 없이 재실행되는지

## 한 줄 정리

`Global Relative Strength`는 이제 core/runtime smoke뿐 아니라
catalog, single UI, compare, history payload, saved replay override까지 연결된 상태이며,
남은 단계는 사용자 화면 QA다.
