# Notes

- 실제 재현에서 React `setComponentValue`와 Python handler는 정상 동작했다.
- 문제는 handler 이후 full-app rerun 승격이 아니라 fragment callback rerun으로 끝나는 경계다.
- latest GTAA history row는 selection source 변환이 가능한 정상 계약이었다.
- 저장 handler와 route owner는 유지하고 intent 소비 시점만 옮긴다.
- custom component에 `on_change`를 넘기지 않고 fragment 본문이 반환 intent를 소비하도록 바꿨다.
- handler 성공 뒤 `st.rerun(scope="app")`이 root의 `init_backtest_state()`를 다시 실행해 `backtest_requested_panel`을 Practical Validation stage로 반영한다.
- 후보 source schema, append-only registry, gate, React payload 계약은 변경하지 않았다.
