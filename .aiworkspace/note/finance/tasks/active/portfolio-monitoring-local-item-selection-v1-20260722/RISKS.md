# Risks

- 최초 workspace의 차트 DB 조회와 payload가 항목 수만큼 늘어난다. 최대 10개/차트 120행
  경계를 지키고 Browser QA에서 체감 로딩을 확인한다.
- 새 field가 없는 구 payload를 받을 수 있으므로 기존 selected projection fallback을 유지한다.
- item-specific command 뒤의 server rerun에서는 event의 `monitoring_item_id`로 같은 선택을
  복구하는 기존 경계를 회귀 검증한다.

