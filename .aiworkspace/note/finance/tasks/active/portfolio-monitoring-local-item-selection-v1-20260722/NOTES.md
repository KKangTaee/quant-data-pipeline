# Notes

- `select_item`은 read-only 선택인데도 Python bridge의 공통 event 경로를 타며 전체
  `runtime.rerun()`을 유발한다.
- 활성 그룹 lane은 모든 항목에 대해 이미 로드되므로 항목별 position projection은 추가
  lane 계산 없이 만들 수 있다.
- 직접 종목 차트는 기존 120행 제한을 재사용하며 그룹 활성 항목 한도는 10개다. 종료 이력은
  누적될 수 있으므로 `item_details` 전체 수는 active 한도와 같다고 가정하지 않는다.
- `end_item` / `reopen_item`은 과거 `select_item` event가 먼저 session selection을 저장하던
  흐름에 기대고 있었다. 새 로컬 선택에서는 mutation event의 `monitoring_item_id`를 dispatcher가
  먼저 session에 저장해야 command 이후 같은 항목이 복구된다.
- 실제 화면에서 선택 항목별 ledger 높이에 따라 Streamlit iframe height가 바뀌며 바깥 scroll이
  조정될 수 있다. 선택 직후 Running 0, console warning/error 0, 그룹 가치 유지와 차트 전환을
  확인해 전체 rerun과 구분했다.
