# Portfolio Monitoring Item Builder UX Fix V1 Notes

## Confirmed Findings

- Browser viewport height 720px, component iframe height 1,616px.
- drawer footer는 iframe 내부 top 약 1,536px에 배치됐다.
- 요청 시작일 input은 disabled가 아니지만 review 이동 시 `-`로 돌아가는 현상이 재현됐다.
- 날짜 blur는 `search_catalog`, Python route는 모든 처리 event 뒤 rerun한다.
- iframe을 560px로 축소하면 drawer만 작아지는 것이 아니라 React workbench 전체가 잘리고 아래 Streamlit 영역이 빈 화면으로 남는다.
- recovery projection object가 다시 전달되면 local `setDrawerOpen(false)` 뒤 effect가 drawer를 재개방할 수 있다.

## Decisions

- DB/command 계산 계약은 유지한다.
- automatic blur lookup보다 uninterrupted wizard completion을 우선한다.
- server round-trip recovery state는 UI 복구 전용이며 command input 권위로 사용하지 않는다.
- iframe은 auto measurement를 유지하고 panel만 560px로 제한한다.
- normalized recovery 내용의 stable key를 한 번 소비해 local 닫기 상태를 우선한다.
