# Today Live Island Rerun Isolation V1 Notes

## 2026-07-23 Decisions

- 15초 heartbeat는 provider cadence가 아니라 background completion/DB state 확인용으로만 유지한다.
- fixed 300초 collection, 600초 quote stale, EOD bounded handoff 계약은 변경하지 않는다.
- 전체 Today fragment와 1초 top-level state는 결합 오류로 판단한다.
- 별도 API/SSE/WebSocket 없이 Streamlit 내부에서 portfolio live island를 우선 구현한다.
- CLOSED에서 관찰된 periodic run은 의도된 사용자 가치가 없으므로 제거 대상이다.
- component key를 context/portfolio/actions로 분리해 portfolio fragment 실행이 static shell iframe identity를 바꾸지 않게 한다.
- phase transition event는 navigation과 분리된 allowlist이며 최초 mount나 동일 phase에서는 발생하지 않는다.
