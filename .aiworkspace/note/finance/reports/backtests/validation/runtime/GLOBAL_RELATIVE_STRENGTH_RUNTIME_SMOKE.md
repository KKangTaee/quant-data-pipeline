# Global Relative Strength Runtime Smoke

## 이 문서는 무엇인가

`Global Relative Strength`가
최소한 코드 레벨에서 실행 가능한지 확인한 개발 검증 report다.

이번 문서는 “이 전략이 투자하기 좋다”를 판단하지 않는다.
목표는 더 작다.

`quant-research` 전략 문서에서 온 아이디어가
`finance.strategy -> finance.sample -> app.web.runtime.backtest` 경로를 지나
DB-backed result bundle까지 만들 수 있는지 확인한다.

## 검증 목적

이번 smoke validation은 아래 질문에 답하기 위한 것이다.

- 새 전략의 simulation 함수가 기존 result schema와 호환되는가?
- `finance.sample`에서 DB 가격 데이터를 읽고 필요한 signal을 만들 수 있는가?
- runtime wrapper가 `build_backtest_result_bundle()` 형태로 결과를 반환하는가?
- 이 단계가 UI 완성이 아니라 core/runtime first implementation이라는 점이 문서에 명확히 남는가?

## 구현된 범위

| 영역 | 현재 상태 |
|---|---|
| Core strategy | `finance.strategy.global_relative_strength_allocation()` 추가 |
| Strategy class | `finance.strategy.GlobalRelativeStrengthStrategy` 추가 |
| DB-backed sample helper | `finance.sample.get_global_relative_strength_from_db()` 추가 |
| Web runtime wrapper | `app.web.runtime.backtest.run_global_relative_strength_backtest_from_db()` 추가 |
| Result bundle | `strategy_name = Global Relative Strength`, `meta.strategy_key = global_relative_strength` |
| UI catalog / Single Strategy | 이 core report 작성 시점에는 미연결, 이후 UI replay smoke report에서 연결 확인 |
| Compare / History / Saved Replay | 이 core report 작성 시점에는 미연결, 이후 UI replay smoke report에서 연결 확인 |

## 전략 규칙 요약

현재 구현은 price-only ETF 월간 전략으로 시작한다.

1. ETF 후보군의 `1M / 3M / 6M / 12M` trailing return을 계산한다.
2. 각 return을 같은 비중으로 평균해 relative-strength score를 만든다.
3. score가 높은 상위 `Top N` ETF를 고른다.
4. 각 후보가 `MA200` trend filter를 통과하는지 확인한다.
5. trend를 통과하지 못한 슬롯은 cash proxy ticker로 둔다.

현재 기본값:

| 항목 | 값 |
|---|---|
| Default risky universe | SPY, EFA, EEM, IWM, VNQ, GLD, DBC, LQD, HYG, IEF, TLT, TIP |
| Cash proxy | BIL |
| Top N | 4 |
| Score lookback | 1M, 3M, 6M, 12M |
| Trend filter | 200-day moving average |
| Cadence | month-end / monthly |

## 실행한 검증

### 1. Python compile check

대상:

- `finance/strategy.py`
- `finance/sample.py`
- `app/web/runtime/backtest.py`
- `app/web/runtime/__init__.py`

결과:

- 통과

### 2. Synthetic strategy smoke

목적:

- DB 없이 작은 synthetic price frame에서 strategy simulation이 `Date`, `Total Balance`, `Total Return`을 반환하는지 확인한다.

결과:

- 통과
- 핵심 result column 생성 확인

### 3. Runtime import smoke

목적:

- Streamlit UI를 거치지 않고 runtime wrapper를 import할 수 있는지 확인한다.

결과:

- 통과
- `run_global_relative_strength_backtest_from_db` import 가능 확인

### 4. DB-backed runtime smoke

실행 조건:

| 항목 | 값 |
|---|---|
| 실행 목적 | core/runtime 개발 검증 |
| Tickers | SPY, EFA, TLT, GLD |
| Cash proxy | BIL |
| 기간 | 2021-01-01 ~ 2024-12-31 |
| Top N | 2 |
| Score lookback | 1M, 3M, 6M, 12M |
| Trend filter | MA200 |
| Universe mode | manual_tickers |

결과 요약:

| 항목 | 값 |
|---|---:|
| Rows | 48 |
| End Balance | 13,660.47 |
| CAGR | 8.28% |
| Strategy Name | Global Relative Strength |
| Meta Strategy Key | global_relative_strength |

## 해석

이번 결과로 확인한 것은 다음이다.

- 새 전략 core simulation은 기존 backtest result schema와 맞는다.
- DB-backed monthly price path에서 필요한 trailing return, average score, trend filter를 만들 수 있다.
- runtime wrapper는 result bundle을 만들 수 있다.

이번 결과로 아직 확인하지 않은 것은 다음이다.

- `Backtest > Single Strategy`에서 사용자가 직접 실행할 수 있는지
- `Compare & Portfolio Builder`에서 전략을 선택하고 strategy-specific input을 볼 수 있는지
- `History > Load Into Form` 또는 `Run Again`에서 입력값이 보존되는지
- saved portfolio replay에서 이 전략이 다른 전략과 함께 재실행되는지
- 이 전략이 투자 후보로 충분한지

## 다음 작업

이 core report 작성 당시 다음 구현 단위는 UI와 재진입 경로 연결이었다.
이후 [GLOBAL_RELATIVE_STRENGTH_UI_REPLAY_SMOKE.md](../ui_replay/GLOBAL_RELATIVE_STRENGTH_UI_REPLAY_SMOKE.md)에서 해당 연결을 검증했다.

- `app.web.backtest_strategy_catalog`에 `global_relative_strength` family 등록
- `Backtest > Single Strategy` 입력 UI 추가
- compare strategy selector와 strategy-specific advanced input 연결
- history payload / load-into-form / run-again 연결
- saved portfolio replay compatibility 확인
- manual QA checklist를 실제 UI 확인 항목으로 갱신

## 한 줄 정리

이 report는 `Global Relative Strength`의 core strategy와 DB-backed runtime smoke 통과를 기록한다.
제품 UI / compare / history / replay 연결 결과는 후속 UI replay smoke report에서 확인한다.
