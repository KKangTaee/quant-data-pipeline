# Runtime Backtest Risk-On Momentum Split Plan

Status: Completed
Date: 2026-06-07

## 이걸 하는 이유?

`app/runtime/backtest.py`는 DB-backed strategy runtime의 public entrypoint이지만, strategy family 구현까지 함께 들고 있어 5천 라인을 넘었다.
8차는 runtime 대형 파일 분해를 시작하되 public import compatibility를 깨지 않는 것이 핵심이다.

## Scope

- 8A는 `Risk-On Momentum 5D` runtime slice만 `app/runtime/backtest_risk_on_momentum.py`로 이동한다.
- `app/runtime/backtest.py`는 기존 caller를 위해 `run_risk_on_momentum_5d_backtest_from_db`를 계속 export한다.
- shared freshness helper, real-money / guardrail contracts, quality/value strict family는 이번 차수에서 이동하지 않는다.
- strategy behavior, artifact format, registry / saved JSONL, DB schema는 변경하지 않는다.

## Steps

1. RED 계약 테스트로 `app/runtime/backtest.py`가 Risk-On Momentum 구현을 전용 module에 위임해야 함을 고정한다.
2. Risk-On Momentum constants, universe resolution, artifact writer, public runner를 `app/runtime/backtest_risk_on_momentum.py`로 이동한다.
3. `app/runtime/backtest.py`에서 기존 public import path를 유지하도록 re-export한다.
4. runtime / architecture docs와 active task manifest를 업데이트한다.
5. py_compile, service contract, boundary checker, Streamlit health를 확인한다.

## Done Conditions

- `app/runtime/backtest.py`에 `run_risk_on_momentum_5d_backtest_from_db` 함수 정의가 남아 있지 않다.
- `app/runtime/backtest_risk_on_momentum.py`가 public runner를 소유한다.
- 기존 `from app.runtime.backtest import run_risk_on_momentum_5d_backtest_from_db`는 계속 작동한다.
- service contract tests와 UI / engine boundary checker가 통과한다.
