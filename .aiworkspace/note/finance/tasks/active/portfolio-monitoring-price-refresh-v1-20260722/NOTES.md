# Notes

- 확인 당시 active group latest daily rows: AMD/RKLB/TEM 2026-07-20, QQQ 2026-07-17, SOXX 2026-07-16.
- 공통 기준일은 의도적으로 active lane latest date의 최솟값이며 interpolation을 하지 않는다.
- 기존 `run_collect_ohlcv`는 explicit end를 inclusive하게 처리하고 loaded symbol에 대해서만 요청 범위를 교체한 뒤 UPSERT한다.
- 목표일은 `latest_completed_nyse_session()`으로 고정해 한국 기준 오늘이나 장중 날짜를 완료 일봉으로 오인하지 않는다.
- stale 종목은 최신 저장일에서 7일을 겹쳐 다시 수집하고, 가격이 전혀 없는 종목은 유효 추적 시작일부터 수집한다.
- 성공 판정은 job의 저장 row 수만 보지 않고 수집 후 DB 최신성을 다시 읽어 unresolved symbol이 없는지 확인한다.
- React는 stale 요약과 action intent만 소유하고, 대상 선정·수집·재검증·run history 기록·가치곡선 재계산은 Python/service 경계가 소유한다.
- actual refresh 이후 active group의 다섯 종목 모두 2026-07-21 완료 일봉을 확보했다.
