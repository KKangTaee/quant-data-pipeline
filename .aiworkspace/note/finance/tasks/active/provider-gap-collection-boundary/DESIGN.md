# Provider Gap Collection Boundary Design

## Current Coupling

`app/web/backtest_practical_validation.py`가 현재 함께 맡는 책임:

- ETF별 provider coverage row 생성
- verified provider source map 조회
- provider gap collection plan 생성
- source map discovery, operability, holdings / exposure, macro ingestion job 실행
- run history metadata 기록
- Streamlit table / warning / button render

이 중 앞의 네 가지는 UI가 아니라 service use-case에 가깝다.

## Target Boundary

```text
Streamlit UI
  -> app.services.backtest_practical_validation
       build_provider_gap_rows()
       build_provider_gap_collection_plan()
       run_provider_gap_collection()
  -> app.jobs.ingestion_jobs / app.jobs.run_history
  -> finance.data.etf_provider source map / provider source constants
```

역할:

- Service: source map 조회, collection 가능 여부 판단, collector 순서 실행, run history metadata 기록
- UI: rows / plan을 표와 message로 표시, button click 시 service 실행, result를 `st.session_state`에 보관
- Data/job layer: provider snapshot 수집과 DB 저장

## Behavior Preservation

- source map discovery 후 plan을 다시 계산한다.
- operability는 official 대상과 DB bridge 대상 모두 기존처럼 실행한다.
- holdings / exposure는 collectable로 판단된 ETF에만 실행한다.
- macro context는 기존 기준처럼 `NOT_RUN` 또는 `REVIEW`이고 coverage가 부족하거나 stale이면 실행한다.
- result metadata의 `pipeline_type`, `execution_mode`, `symbol_source`, `input_params`는 기존 값을 유지한다.
