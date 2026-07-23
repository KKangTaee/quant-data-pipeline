# Risks

- 최초 workspace의 차트 DB 조회와 payload가 표시 항목 수만큼 늘어난다. active는 최대 10개,
  차트는 120행으로 제한되지만 종료 이력은 누적될 수 있다. actual 5개 그룹은 정상 동작을
  확인했으며 큰 종료 이력 그룹은 후속 pagination/lazy-detail 후보로 남긴다.
- 새 field가 없는 구 payload를 받을 수 있으므로 기존 selected projection fallback을 유지한다.
- item-specific command 뒤의 server rerun에서는 event의 `monitoring_item_id`로 같은 선택을
  복구하며 `end_item` / `reopen_item` dispatcher 회귀를 추가했다.
- 항목별 상세 높이 차이로 iframe 높이와 바깥 scroll 위치가 조정될 수 있다. 이는 선택 event에
  따른 page rerun이 아니며, Running 0과 개별 detail만 바뀌는 actual QA로 확인했다.
