# Backtest Execution Service Boundary Plan

Status: Complete
Created: 2026-05-19

## 이걸 하는 이유?

Single Strategy 실행은 UI와 engine 분리의 첫 검증 지점이다.
기존 `app/web/backtest_single_runner.py`는 Streamlit payload 표시, spinner, runtime dispatch, error normalization, session state 저장, history append를 한 파일에서 처리했다.

이 task는 화면 동작은 유지하면서 runtime dispatch와 error normalization만 `app/services/backtest_execution.py`로 옮겨, 이후 Compare / Practical Validation도 같은 방식으로 분리할 수 있는 기준을 만든다.

## Scope

포함:

- `app/services` source package 생성
- `app/services/backtest_execution.py` 생성
- Single Strategy DB-backed runtime dispatch 이동
- input / data / system error normalization 이동
- elapsed time metadata 유지
- `app/web/backtest_single_runner.py`를 Streamlit UI state / history append 담당으로 축소

제외:

- Compare 실행 분리
- Practical Validation 분리
- strategy runtime behavior 변경
- DB / loader / registry schema 변경
- Streamlit UX 변경

## Done Criteria

- service module이 Streamlit을 import하지 않는다.
- `app/web/backtest_single_runner.py`는 service를 호출하고 기존 session state key와 history append를 유지한다.
- compile / import smoke / service no-Streamlit check가 통과한다.
- phase docs와 durable code maps가 새 boundary를 가리킨다.
