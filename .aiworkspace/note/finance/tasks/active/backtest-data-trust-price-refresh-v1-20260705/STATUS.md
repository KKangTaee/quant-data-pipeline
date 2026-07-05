# Backtest Data Trust Price Refresh V1 Status

Status: Done
Started: 2026-07-05

## Current Goal

`데이터 기준 요약`에서 DB OHLCV가 현재 기준 최신 거래일까지 채워져 있지 않을 때, 현재 백테스트 ticker만 갱신하는 버튼을 제공한다.

## Implementation Notes

- Backtest 화면은 React component submit event 소비와 session feedback만 소유한다.
- 실제 수집은 `app/jobs/ingestion_jobs.py::run_collect_ohlcv`를 재사용한다.
- 최신 기준일 계산은 주말 / NYSE 휴장일을 제외한다.
- `app/services/backtest_price_refresh.py`가 refresh plan과 실행 wrapper를 소유한다.
- `app/web/components/backtest_price_refresh_action/`은 보이는 action card / 버튼을 렌더링한다.
- `app/web/backtest_result_display.py`는 plan을 읽어 component event를 처리하고 실행 결과를 표시한다.

## Done Criteria

- 최신 DB 기준이면 버튼이 보이지 않는다.
- DB 기준이 최신 거래일보다 오래됐으면 버튼과 대상 기간 / ticker 안내가 보인다.
- 버튼 실행 결과가 성공 / 부분 성공 / 실패 상태로 표시된다.
- 실행 후 자동으로 후보 등록이나 2차 검증 전송이 발생하지 않는다.
- focused tests, compile, browser QA가 완료된다.

## Result

- `데이터 기준 요약` 아래에 조건부 `가격 데이터 업데이트` 액션을 추가했다.
- 버튼은 React action card 내부에 통합했고, 현재 백테스트 ticker의 OHLCV만 기존 ingestion job으로 보강한다.
- 최신 기준일은 주말 / NYSE 휴장일을 제외한 마지막 완료 거래일로 계산한다.
- 업데이트 후 성과 재계산, 후보 등록, 2차 검증 handoff는 자동 실행하지 않고 사용자가 `Run Backtest`를 다시 실행하도록 안내한다.
