# Notes

## 2026-07-07

- BK 케이스의 오류 메시지는 `run_collect_ohlcv`가 해당 구간에 provider row를 받지 못해 rows_written=0을 반환한 상황이다.
- 현재 UI는 이 실패 결과를 표시하면서도 기존 plan의 `eligible=True` action card를 먼저 렌더링하므로 사용자가 같은 버튼을 반복 클릭하게 된다.
- 해결은 수집 반복이 아니라 `provider/source gap`을 Data Trust 확인 대상으로 낮추고 버튼 재노출을 막는 것이다.
- 첫 클릭 전에는 heuristic이 `minor_source_lag`로만 보일 수 있다. 따라서 plan 단계의 provider-gap 제외와 실행 후 no-row unresolved retry-block을 함께 둬야 한다.
