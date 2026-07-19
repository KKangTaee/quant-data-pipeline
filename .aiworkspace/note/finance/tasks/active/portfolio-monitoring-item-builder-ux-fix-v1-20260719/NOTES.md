# Portfolio Monitoring Item Builder UX Fix V1 Notes

## Confirmed Findings

- Browser viewport height 720px, component iframe height 1,616px.
- drawer footer는 iframe 내부 top 약 1,536px에 배치됐다.
- 요청 시작일 input은 disabled가 아니지만 review 이동 시 `-`로 돌아가는 현상이 재현됐다.
- 날짜 blur는 `search_catalog`, Python route는 모든 처리 event 뒤 rerun한다.

## Decisions

- DB/command 계산 계약은 유지한다.
- automatic blur lookup보다 uninterrupted wizard completion을 우선한다.
- server round-trip recovery state는 UI 복구 전용이며 command input 권위로 사용하지 않는다.
